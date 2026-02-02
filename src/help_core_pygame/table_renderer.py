#!/usr/bin/python3
"""
Fecha: 02/feb/2026 y hora 10:20
Archivo: table_renderer.py
Descripción breve: Renderiza un bloque de tabla (subconjunto GFM) a un pygame.Surface con estilo fijo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple

import pygame


# ---------------------------------------------------------------------
# Estilo fijo (NO configurable por diseño)
# ---------------------------------------------------------------------

HEADER_BG_COLOR: Tuple[int, int, int] = (50, 50, 180)
HEADER_FG_COLOR: Tuple[int, int, int] = (255, 255, 255)

BODY_BG_COLOR: Tuple[int, int, int] = (255, 255, 255)
BODY_FG_COLOR: Tuple[int, int, int] = (0, 0, 0)

GRID_COLOR: Tuple[int, int, int] = (0, 0, 0)

CELL_PAD_X: int = 8
CELL_PAD_Y: int = 4

BORDER_THICKNESS: int = 1


_ALIGN_LEFT = "left"
_ALIGN_CENTER = "center"
_ALIGN_RIGHT = "right"


@dataclass(frozen=True)
class TableRenderResult:
    """Resultado del renderizado de una tabla.

    Attributes:
        surface: Superficie renderizada con la tabla completa.
        width: Ancho en píxeles.
        height: Alto en píxeles.
    """

    surface: pygame.Surface
    width: int
    height: int


def render_table(
    table_block: Dict[str, Any],
    body_font: pygame.font.Font,
    header_font: pygame.font.Font,
) -> TableRenderResult:
    """Renderiza una tabla pre-parseada a una Surface.

    Requisitos del contrato del bloque:
        {
          "type": "table",
          "header": ["Col A", "Col B", ...],      # len = ncols >= 2
          "align":  ["left|center|right", ...],   # len = ncols (solo cuerpo)
          "rows": [
            ["r1c1", "r1c2", ...],                # cada fila normalizada a ncols
            ...
          ],
          "row_overflow": [False, True, ...]      # len = len(rows)
        }

    Notas:
      - Cabecera SIEMPRE centrada (ignora "align").
      - Sin wrapping: anchos por máximo de celda (cabecera + filas).
      - Si alguna fila tiene overflow, se dibuja un '@' a la derecha (fuera de tabla)
        alineado con esa fila.

    Args:
        table_block: Bloque de tabla emitido por el parser.
        body_font: Fuente normal para filas.
        header_font: Fuente negrita para cabecera.

    Returns:
        TableRenderResult con la Surface renderizada.
    """
    header_cells, body_rows, body_align, row_overflow = _validate_table_block(table_block)

    ncols = len(header_cells)
    nrows = len(body_rows)

    # --------------------------------------------------------------
    # 1) Medición de anchos por columna (máximo cabecera + filas)
    # --------------------------------------------------------------
    max_text_widths = [0] * ncols

    for col_index, text in enumerate(header_cells):
        text_width, _ = header_font.size(text)
        if text_width > max_text_widths[col_index]:
            max_text_widths[col_index] = text_width

    for row in body_rows:
        for col_index, text in enumerate(row):
            text_width, _ = body_font.size(text)
            if text_width > max_text_widths[col_index]:
                max_text_widths[col_index] = text_width

    col_widths = [
        max_width + 2 * CELL_PAD_X
        for max_width in max_text_widths
    ]

    table_content_width = sum(col_widths)
    table_content_height_header = header_font.get_linesize() + 2 * CELL_PAD_Y
    table_content_height_row = body_font.get_linesize() + 2 * CELL_PAD_Y

    # --------------------------------------------------------------
    # 2) Gutter de overflow (si hay filas con overflow)
    # --------------------------------------------------------------
    has_overflow = any(row_overflow)
    gutter_width = 0
    if has_overflow:
        at_width, _ = body_font.size("@")
        gutter_width = at_width + 2 * CELL_PAD_X

    # --------------------------------------------------------------
    # 3) Tamaño final de Surface (bordes externos, líneas internas dibujadas encima)
    # --------------------------------------------------------------
    total_width = table_content_width + 2 * BORDER_THICKNESS + gutter_width
    total_height = (
        table_content_height_header
        + nrows * table_content_height_row
        + 2 * BORDER_THICKNESS
    )

    surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
    surface.fill(BODY_BG_COLOR)

    # --------------------------------------------------------------
    # 4) Fondos (cabecera negro, cuerpo blanco ya está)
    # --------------------------------------------------------------
    table_x0 = BORDER_THICKNESS
    table_y0 = BORDER_THICKNESS

    header_rect = pygame.Rect(
        table_x0,
        table_y0,
        table_content_width,
        table_content_height_header,
    )
    surface.fill(HEADER_BG_COLOR, header_rect)

    # --------------------------------------------------------------
    # 5) Dibujar texto: cabecera (centrada siempre)
    # --------------------------------------------------------------
    current_x = table_x0
    for col_index in range(ncols):
        cell_w = col_widths[col_index]
        cell_rect = pygame.Rect(
            current_x,
            table_y0,
            cell_w,
            table_content_height_header,
        )
        _blit_text_centered(
            target_surface=surface,
            font=header_font,
            text=header_cells[col_index],
            fg_color=HEADER_FG_COLOR,
            cell_rect=cell_rect,
        )
        current_x += cell_w

    # --------------------------------------------------------------
    # 6) Dibujar texto: filas (alineación por columna)
    # --------------------------------------------------------------
    for row_index in range(nrows):
        row_y = table_y0 + table_content_height_header + row_index * table_content_height_row

        current_x = table_x0
        for col_index in range(ncols):
            cell_w = col_widths[col_index]
            cell_rect = pygame.Rect(
                current_x,
                row_y,
                cell_w,
                table_content_height_row,
            )

            align_mode = body_align[col_index] if col_index < len(body_align) else _ALIGN_LEFT
            _blit_text_aligned(
                target_surface=surface,
                font=body_font,
                text=body_rows[row_index][col_index],
                fg_color=BODY_FG_COLOR,
                cell_rect=cell_rect,
                align_mode=align_mode,
            )
            current_x += cell_w

        # Indicador '@' fuera de la tabla si sobran celdas
        if has_overflow and row_overflow[row_index]:
            gutter_x0 = table_x0 + table_content_width
            gutter_rect = pygame.Rect(
                gutter_x0,
                row_y,
                gutter_width,
                table_content_height_row,
            )
            _blit_text_centered(
                target_surface=surface,
                font=body_font,
                text="@",
                fg_color=BODY_FG_COLOR,
                cell_rect=gutter_rect,
            )

    # --------------------------------------------------------------
    # 7) Líneas de rejilla y borde exterior (dibujadas encima)
    # --------------------------------------------------------------
    _draw_grid(
        surface=surface,
        table_x0=table_x0,
        table_y0=table_y0,
        col_widths=col_widths,
        header_h=table_content_height_header,
        row_h=table_content_height_row,
        nrows=nrows,
        has_overflow=has_overflow,
        gutter_width=gutter_width,
    )

    return TableRenderResult(surface=surface, width=total_width, height=total_height)


# ---------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------

def _validate_table_block(
    table_block: Dict[str, Any],
) -> Tuple[List[str], List[List[str]], List[str], List[bool]]:
    """Valida el bloque y devuelve estructuras listas para render."""
    if table_block.get("type") != "table":
        raise ValueError("table_block debe tener type == 'table'")

    header = table_block.get("header")
    rows = table_block.get("rows")
    align = table_block.get("align")
    row_overflow = table_block.get("row_overflow")

    if not isinstance(header, list) or len(header) < 2:
        raise ValueError("table_block['header'] debe ser una lista con al menos 2 elementos")

    if not isinstance(rows, list) or len(rows) < 1:
        raise ValueError("table_block['rows'] debe ser una lista con al menos 1 fila")

    if not isinstance(align, list) or len(align) != len(header):
        raise ValueError("table_block['align'] debe ser una lista con longitud igual a header")

    if not isinstance(row_overflow, list) or len(row_overflow) != len(rows):
        raise ValueError("table_block['row_overflow'] debe ser una lista con longitud igual a rows")

    ncols = len(header)

    header_cells = [str(x) for x in header]

    body_rows: List[List[str]] = []
    for row in rows:
        if not isinstance(row, list) or len(row) != ncols:
            raise ValueError("Cada fila en table_block['rows'] debe ser una lista con len == ncols")
        body_rows.append([str(x) for x in row])

    body_align: List[str] = []
    for a in align:
        a_str = str(a)
        if a_str not in (_ALIGN_LEFT, _ALIGN_CENTER, _ALIGN_RIGHT):
            # Por prudencia: si llega algo raro, lo tratamos como left.
            a_str = _ALIGN_LEFT
        body_align.append(a_str)

    overflow_flags = [bool(x) for x in row_overflow]

    return header_cells, body_rows, body_align, overflow_flags


def _blit_text_centered(
    target_surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    fg_color: Tuple[int, int, int],
    cell_rect: pygame.Rect,
) -> None:
    """Dibuja texto centrado en el rectángulo de celda."""
    text_surface = font.render(text, True, fg_color)
    text_rect = text_surface.get_rect()

    text_rect.centerx = cell_rect.centerx
    text_rect.centery = cell_rect.centery

    target_surface.blit(text_surface, text_rect)


def _blit_text_aligned(
    target_surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    fg_color: Tuple[int, int, int],
    cell_rect: pygame.Rect,
    align_mode: str,
) -> None:
    """Dibuja texto dentro de la celda con alineación left/center/right."""
    text_surface = font.render(text, True, fg_color)
    text_rect = text_surface.get_rect()

    # Coordenada Y: centrado vertical simple
    text_rect.centery = cell_rect.centery

    if align_mode == _ALIGN_CENTER:
        text_rect.centerx = cell_rect.centerx
    elif align_mode == _ALIGN_RIGHT:
        text_rect.right = cell_rect.right - CELL_PAD_X
    else:
        # left por defecto
        text_rect.left = cell_rect.left + CELL_PAD_X

    target_surface.blit(text_surface, text_rect)


def _draw_grid(
    surface: pygame.Surface,
    table_x0: int,
    table_y0: int,
    col_widths: Sequence[int],
    header_h: int,
    row_h: int,
    nrows: int,
    has_overflow: bool,
    gutter_width: int,
) -> None:
    """Dibuja borde exterior y separadores de celdas."""
    table_width = sum(col_widths)
    table_height = header_h + nrows * row_h

    # Borde exterior de la tabla (solo la tabla, no incluye gutter)
    outer_rect = pygame.Rect(table_x0, table_y0, table_width, table_height)
    pygame.draw.rect(surface, GRID_COLOR, outer_rect, BORDER_THICKNESS)

    # Línea horizontal debajo de cabecera
    y_header_bottom = table_y0 + header_h
    pygame.draw.line(
        surface,
        GRID_COLOR,
        (table_x0, y_header_bottom),
        (table_x0 + table_width, y_header_bottom),
        BORDER_THICKNESS,
    )

    # Líneas horizontales entre filas
    for row_index in range(1, nrows):
        y = y_header_bottom + row_index * row_h
        pygame.draw.line(
            surface,
            GRID_COLOR,
            (table_x0, y),
            (table_x0 + table_width, y),
            BORDER_THICKNESS,
        )

    # Líneas verticales entre columnas
    x = table_x0
    for col_w in col_widths[:-1]:
        x += col_w
        pygame.draw.line(
            surface,
            GRID_COLOR,
            (x, table_y0),
            (x, table_y0 + table_height),
            BORDER_THICKNESS,
        )

    # Si hay gutter (overflow), dibujamos una línea separadora y un borde simple del gutter
    if has_overflow and gutter_width > 0:
        gutter_x0 = table_x0 + table_width

        # Línea separadora table|gutter
        pygame.draw.line(
            surface,
            GRID_COLOR,
            (gutter_x0, table_y0),
            (gutter_x0, table_y0 + table_height),
            BORDER_THICKNESS,
        )

        # Borde exterior del gutter (rectángulo completo del gutter alineado con tabla)
        gutter_rect = pygame.Rect(gutter_x0, table_y0, gutter_width, table_height)
        pygame.draw.rect(surface, GRID_COLOR, gutter_rect, BORDER_THICKNESS)

