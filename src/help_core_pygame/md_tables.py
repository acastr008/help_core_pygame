"""
Fecha: 02/feb/2026 y hora 10:05
Archivo: md_tables.py
Descripción breve: Parser modular de tablas tipo GFM (subconjunto) para mini_MarkDown.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, Dict, Any


_ALIGN_LEFT = "left"
_ALIGN_CENTER = "center"
_ALIGN_RIGHT = "right"

# Celda separadora válida (GFM reducido):
#  - opcional ':' al inicio
#  - al menos 3 guiones
#  - opcional ':' al final
_RE_SEPARATOR_CELL = re.compile(r"^\s*:?-{3,}:?\s*$")


@dataclass(frozen=True)
class TableParseResult:
    """Resultado del parseo de una tabla.

    Attributes:
        block: Diccionario con la estructura de tabla acordada.
        next_index: Índice de línea desde el que continuar el parseo global.
    """
    block: Dict[str, Any]
    next_index: int


def is_table_start(lines: Sequence[str], index: int) -> bool:
    """Indica si en `lines[index]` comienza un bloque de tabla válido.

    Reglas mínimas:
      1) Cabecera con '|' y >= 2 columnas.
      2) Separador válido inmediatamente debajo (alineación).
      3) Al menos una fila de datos válida inmediatamente debajo del separador (>= 2 columnas).

    Args:
        lines: Líneas del documento (sin el salto final).
        index: Posición a comprobar.

    Returns:
        True si se detecta una tabla válida; False en caso contrario.
    """
    if index < 0 or index + 2 >= len(lines):
        return False

    header_cells = _parse_table_row(lines[index])
    if header_cells is None or len(header_cells) < 2:
        return False

    align = _parse_separator_row(lines[index + 1], expected_cols=len(header_cells))
    if align is None:
        return False

    first_row_cells = _parse_table_row(lines[index + 2])
    if first_row_cells is None or len(first_row_cells) < 2:
        return False

    return True


def parse_table(lines: Sequence[str], index: int) -> Optional[TableParseResult]:
    """Parsea un bloque de tabla a partir de `index`.

    Si no se reconoce una tabla válida con las reglas mínimas, devuelve None.

    Contrato del bloque:
        {
          "type": "table",
          "header": [...],           # len = ncols
          "align":  [...],           # len = ncols (alineación cuerpo)
          "rows":   [[...], ...],    # cada fila normalizada a ncols
          "row_overflow": [bool, ...]
        }

    Args:
        lines: Líneas del documento.
        index: Índice donde se espera la cabecera.

    Returns:
        TableParseResult o None si no hay tabla válida en ese punto.
    """
    if not is_table_start(lines, index):
        return None

    header_cells = _parse_table_row(lines[index])
    if header_cells is None:
        return None

    ncols = len(header_cells)

    align = _parse_separator_row(lines[index + 1], expected_cols=ncols)
    if align is None:
        return None

    rows: List[List[str]] = []
    row_overflow: List[bool] = []

    i = index + 2
    while i < len(lines):
        line = lines[i]

        # Nota: la tabla es un bloque; una línea vacía corta el bloque.
        if line.strip() == "":
            break

        row_cells = _parse_table_row(line)
        if row_cells is None or len(row_cells) < 2:
            break

        normalized_cells, overflow = _normalize_row(row_cells, ncols=ncols)
        rows.append(normalized_cells)
        row_overflow.append(overflow)

        i += 1

    # Regla mínima: al menos 1 fila de datos
    if not rows:
        return None

    block: Dict[str, Any] = {
        "type": "table",
        "header": header_cells,
        "align": align,
        "rows": rows,
        "row_overflow": row_overflow,
    }
    return TableParseResult(block=block, next_index=i)


def _parse_table_row(line: str) -> Optional[List[str]]:
    """Convierte una línea con pipes en lista de celdas.

    Soporta pipes al inicio/fin (estilo GFM):
        | a | b |
    y también sin pipes externos:
        a | b

    No se soporta escapado de '|' dentro de celda.

    Args:
        line: Línea a parsear.

    Returns:
        Lista de celdas ya recortadas (strip), o None si no parece una fila.
    """
    if "|" not in line:
        return None

    raw = line.strip()

    parts = raw.split("|")

    # Eliminar celda vacía creada por pipe inicial/final
    if raw.startswith("|"):
        parts = parts[1:]
    if raw.endswith("|"):
        parts = parts[:-1]

    cells = [p.strip() for p in parts]

    # Si tras limpiar queda 0/1 celda, no lo consideramos fila de tabla
    if len(cells) < 2:
        return None

    return cells


def _parse_separator_row(line: str, expected_cols: int) -> Optional[List[str]]:
    """Parsea la fila separadora y produce la alineación por columna.

    Alineación (cuerpo):
      - :---  -> left
      - ---:  -> right
      - :---: -> center
      - ---   -> left (por defecto)

    Args:
        line: Línea separadora.
        expected_cols: Número de columnas esperado (el de la cabecera).

    Returns:
        Lista de strings: ["left"|"center"|"right", ...] de longitud expected_cols,
        o None si la línea no es separador válido.
    """
    cells = _parse_table_row(line)
    if cells is None:
        return None

    if len(cells) != expected_cols:
        # Mantenerlo estricto reduce falsos positivos y ambigüedades.
        return None

    align: List[str] = []
    for cell in cells:
        if not _RE_SEPARATOR_CELL.match(cell):
            return None

        trimmed = cell.strip()
        starts_colon = trimmed.startswith(":")
        ends_colon = trimmed.endswith(":")

        if starts_colon and ends_colon:
            align.append(_ALIGN_CENTER)
        elif starts_colon:
            align.append(_ALIGN_LEFT)
        elif ends_colon:
            align.append(_ALIGN_RIGHT)
        else:
            align.append(_ALIGN_LEFT)

    return align


def _normalize_row(row_cells: List[str], ncols: int) -> Tuple[List[str], bool]:
    """Normaliza una fila respecto al número de columnas de cabecera.

    Reglas acordadas:
      - Si faltan celdas: rellenar cada celda faltante con '@' dentro de la tabla.
      - Si sobran celdas: truncar a ncols y marcar overflow=True (renderer pondrá '@' fuera a la derecha).

    Args:
        row_cells: Celdas originales de la fila.
        ncols: Número de columnas definido por la cabecera.

    Returns:
        (celdas_normalizadas, overflow)
    """
    if len(row_cells) < ncols:
        missing = ncols - len(row_cells)
        normalized = row_cells + ["@"] * missing
        return normalized, False

    if len(row_cells) > ncols:
        normalized = row_cells[:ncols]
        return normalized, True

    return row_cells, False

