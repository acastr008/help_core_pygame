#!/usr/bin/python3
"""
Programa asistido por ChatGPT en fecha 12/Feb/2026 y hora 00:00
Titulo: Extracción de anclas HTML reales en Markdown
Descripción: Escanea un fichero Markdown y extrae IDs de anclas HTML reales (<a ... id="...">...</a>),
             ignorando apariciones dentro de fences de código y código inline con backticks. Genera
             ids_anclas_md.txt y reporta problemas (duplicados / anclas malformadas) por terminal.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Regex para detectar inicio/fin de fence (``` o ~~~), tolerando espacios.
_FENCE_RE = re.compile(r"^\s*(```|~~~)")

# Regex para detectar una etiqueta <a ...> (apertura), en línea no-código.
_ANCHOR_OPEN_RE = re.compile(r"<a\b[^>]*>", re.IGNORECASE)

# Regex para extraer id="..." o id='...' dentro de la etiqueta de apertura.
_ID_ATTR_RE = re.compile(r"""\bid\s*=\s*(?:"([^"]+)"|'([^']+)')""", re.IGNORECASE)

# Regex para detectar que la etiqueta de apertura es de un <a ...> real (no algo raro con <a).
_TAG_A_RE = re.compile(r"<a\b", re.IGNORECASE)


def _strip_inline_code_spans(line: str) -> str:
    """Elimina segmentos de código inline delimitados por backticks.

    Regla simple: alterna entre "texto normal" y "código" al dividir por `.
    No intenta soportar variantes con múltiples backticks.
    """
    parts = line.split("`")
    kept_parts: List[str] = []
    for idx, part in enumerate(parts):
        if idx % 2 == 0:
            kept_parts.append(part)
        else:
            kept_parts.append(" ")  # sustituye código por espacio para no pegar tokens
    return "".join(kept_parts)


def _extract_anchor_ids_from_line(line: str) -> Tuple[List[str], List[str]]:
    """Extrae ids de anclas en una línea ya filtrada de inline-code.

    Retorna:
        - ids_encontrados: lista de ids válidos encontrados.
        - problemas: lista de mensajes de problema detectados en esa línea.
    """
    ids_found: List[str] = []
    problems: List[str] = []

    for match in _ANCHOR_OPEN_RE.finditer(line):
        tag = match.group(0)
        if not _TAG_A_RE.search(tag):
            continue

        id_match = _ID_ATTR_RE.search(tag)
        if not id_match:
            # Hay <a ...> pero sin id="..." o id='...'
            problems.append("Etiqueta <a> sin atributo id entre comillas.")
            continue

        anchor_id = id_match.group(1) or id_match.group(2) or ""
        anchor_id = anchor_id.strip()

        if not anchor_id:
            problems.append('Atributo id vacío en etiqueta <a id="...">.')
            continue

        ids_found.append(anchor_id)

    return ids_found, problems


def extract_markdown_anchor_ids(markdown_path: Path) -> Tuple[List[str], List[str]]:
    """Escanea el Markdown y devuelve (ids_en_orden, lista_de_problemas)."""
    if not markdown_path.exists():
        raise FileNotFoundError(f"No existe el fichero: {markdown_path}")

    in_fence = False
    ids_in_order: List[str] = []
    problems: List[str] = []

    with markdown_path.open("r", encoding="utf-8") as file_handle:
        for lineno, raw_line in enumerate(file_handle, start=1):
            line = raw_line.rstrip("\n")

            if _FENCE_RE.match(line):
                in_fence = not in_fence
                continue

            if in_fence:
                continue

            # Ignorar inline code para evitar falsos positivos como `<a id="x"></a>`
            filtered_line = _strip_inline_code_spans(line)

            ids_found, line_problems = _extract_anchor_ids_from_line(filtered_line)
            ids_in_order.extend(ids_found)

            for p in line_problems:
                problems.append(f"Línea {lineno}: {p} | {line.strip()}")

    if in_fence:
        problems.append("EOF: el fichero termina dentro de un fence de código sin cerrar (``` o ~~~).")

    return ids_in_order, problems


def validate_ids(ids_in_order: List[str]) -> List[str]:
    """Valida duplicados y devuelve mensajes de error."""
    errors: List[str] = []
    first_occurrence: Dict[str, int] = {}

    for idx, anchor_id in enumerate(ids_in_order, start=1):
        if anchor_id in first_occurrence:
            errors.append(
                f"ERROR: ID duplicado '{anchor_id}' (aparición #{first_occurrence[anchor_id]} y #{idx})."
            )
        else:
            first_occurrence[anchor_id] = idx

    return errors


def write_ids_file(output_path: Path, ids_in_order: List[str]) -> None:
    """Escribe el fichero ids_anclas_md.txt con un id por línea, en orden de aparición."""
    with output_path.open("w", encoding="utf-8") as file_handle:
        for anchor_id in ids_in_order:
            file_handle.write(f"{anchor_id}\n")


def build_arg_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos."""
    parser = argparse.ArgumentParser(
        description="Extrae IDs de anclas HTML reales (<a id=\"...\">) en Markdown, ignorando código."
    )
    parser.add_argument(
        "markdown_file",
        help="Ruta al fichero Markdown de entrada.",
    )
    parser.add_argument(
        "--out",
        default="ids_anclas_md.txt",
        help="Ruta del fichero de salida. Por defecto: ids_anclas_md.txt",
    )
    return parser


def main() -> int:
    """Punto de entrada principal."""
    parser = build_arg_parser()
    args = parser.parse_args()

    markdown_path = Path(args.markdown_file).expanduser()
    output_path = Path(args.out).expanduser()

    try:
        ids_in_order, scan_problems = extract_markdown_anchor_ids(markdown_path)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    duplicate_errors = validate_ids(ids_in_order)

    # Reporte por terminal (solo problemas)
    for p in scan_problems:
        print(f"AVISO: {p}", file=sys.stderr)

    for e in duplicate_errors:
        print(e, file=sys.stderr)

    # Generación del fichero solicitado
    try:
        write_ids_file(output_path, ids_in_order)
    except Exception as exc:
        print(f"ERROR escribiendo salida: {exc}", file=sys.stderr)
        return 3

    # Código de retorno no-cero si hay duplicados (útil para CI)
    if duplicate_errors:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

