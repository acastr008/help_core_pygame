#!/usr/bin/python3
########## Copyright (c) ##########################################################
# SPDX-FileCopyrightText: 2025 Antonio Castro Snurmacher <acastro0841@gmail.com>
# SPDX-License-Identifier: MIT
###################################################################################
from __future__ import annotations

"""
######################################################################################################################
Fichero   : view_markdown_help_core.py
Versión   : 1.0  (5-feb-2026)
Licencia de uso MIT
Descripción Breve: Abre un fichero .md y lo visualiza 
Descripción: Abre un fichero .md y lo visualiza con open_help_standalone, resolviendo rutas relativas desde el directorio del .md.
######################################################################################################################
"""

import argparse
from pathlib import Path
from typing import Tuple

from help_core_pygame import open_help_standalone


USAGE_EXAMPLES_TEXT = """\
Ejemplos de uso:
  python3 examples/view_markdown_help_core.py docs/TUTORIAL.md
  python3 examples/view_markdown_help_core.py docs/TUTORIAL.md --size 1400x900
  python3 examples/view_markdown_help_core.py docs/TUTORIAL.md --title "Mi ayuda" --cooldown-ms 250
"""


class FriendlyArgumentParser(argparse.ArgumentParser):
    """ArgumentParser con errores más amigables (incluye ejemplos de uso)."""

    def error(self, message: str) -> None:
        """
        Muestra una ayuda completa (una sola vez) y un mensaje de error claro.

        :param message: Mensaje de error generado por argparse.
        """
        help_text = self.format_help()
        self.exit(2, f"{help_text}\nERROR: {message}\n")


def parse_window_size(size_text: str) -> Tuple[int, int]:
    """
    Parsea el tamaño de ventana desde un texto tipo '1200x900'.

    :param size_text: Cadena con formato ANCHOxALTO (ej. '1200x900').
    :return: Tupla (ancho, alto).
    :raises ValueError: Si el formato no es válido.
    """
    cleaned = size_text.lower().strip()
    if "x" not in cleaned:
        raise ValueError("Formato inválido. Use ANCHOxALTO, por ejemplo 1200x900.")

    width_text, height_text = cleaned.split("x", 1)
    width = int(width_text.strip())
    height = int(height_text.strip())

    if width <= 0 or height <= 0:
        raise ValueError("El tamaño debe ser positivo.")

    return width, height


def read_text_file(file_path: Path) -> str:
    """
    Lee un fichero de texto con UTF-8 (con tolerancia a BOM) y devuelve su contenido.

    :param file_path: Ruta al fichero.
    :return: Contenido del fichero como str.
    """
    return file_path.read_text(encoding="utf-8-sig")


def build_parser() -> FriendlyArgumentParser:
    """
    Construye el parser de argumentos.

    :return: Instancia de FriendlyArgumentParser.
    """
    parser = FriendlyArgumentParser(
        prog="view_markdown_help_core.py",
        description="Visualiza un fichero Markdown con help_core_pygame.open_help_standalone.",
        epilog=USAGE_EXAMPLES_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "markdown_file",
        type=str,
        help="Ruta al fichero .md a visualizar.",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Título de la ventana (por defecto: nombre del fichero).",
    )
    parser.add_argument(
        "--size",
        type=str,
        default="1200x900",
        help="Tamaño de la ventana en formato ANCHOxALTO (por defecto: 1200x900).",
    )
    parser.add_argument(
        "--cooldown-ms",
        type=int,
        default=300,
        help="Cooldown del evento on_scroll_limit (por defecto: 300).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    markdown_path = Path(args.markdown_file).expanduser().resolve()
    if not markdown_path.exists():
        raise SystemExit(f"ERROR: No existe el fichero: {markdown_path}")
    if not markdown_path.is_file():
        raise SystemExit(f"ERROR: No es un fichero: {markdown_path}")

    try:
        window_size = parse_window_size(args.size)
    except ValueError as exc:
        raise SystemExit(f"ERROR: {exc}\n\n{USAGE_EXAMPLES_TEXT}") from exc

    markdown_text = read_text_file(markdown_path)

    window_title = args.title if args.title is not None else markdown_path.name

    # base_dir = directorio del .md para resolver rutas relativas (imágenes, etc.)
    base_dir = str(markdown_path.parent)

    window_title += "      (Pulse <ESC> para salir)"

    open_help_standalone(
        markdown_text,
        title=window_title,
        size=window_size,
        scroll_limit_cooldown_ms=args.cooldown_ms,
        base_dir=base_dir,
    )


if __name__ == "__main__":
    main()

