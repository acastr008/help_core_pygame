from __future__ import annotations

# En esta nueva versión número 10 refactorizacion pasar la clase la clase _MiniMarkdown  a help_mini_markdown 

########## Copyright (c) ##########################################################
# SPDX-FileCopyrightText: 2025 Antonio Castro Snurmacher <acastro0841@gmail.com>
# SPDX-License-Identifier: MIT
###################################################################################

"""
######################################################################################################################
Programa  : help_core.py
Licencia de uso MIT

Descripción breve:
    Visor de ayuda independiente, basado únicamente en Pygame, con soporte de Markdown reducido.

Descripción detallada:
    Permite visualizar en una pantalla un texto de ayuda en formato markdown.
     - Sin dependencias de PopupDialogWindow ni de tu GUI.
     - Puede abrir su propia ventana (open_window) o renderizar en una surface/rect.
     - Estilos opcionales vía JSON + variant y/o style_overrides.

LIMITACIONES:
    Es un diseño basado en un subconjunto de Markdown. Dicho subconjunto está descrito en help_core_api_uso.md.
    Dicho diseño cubre los elementos más necesarios para poder ofrecer una visualización bien estructurada
    de la información.

Uso:
    Veasé la documentación: help_core_api_uso.md,  help_core_chuleta_rapida.md,  help_core_doc_actualizado.md

Requisitos:
    - Python 3.11
    - Pygame
######################################################################################################################
"""

"""
-----------------------------------------------------------------------------
_MiniMarkdown – Lenguaje soportado (Markdown reducido)
-----------------------------------------------------------------------------
Configuración:
  - tab_size (int): nº de espacios que sustituye a cada tabulador en normalize().
  - max_list_nesting (int): profundidad máxima de indentación para listas.
      *Internamente los niveles van de 0 a (max_list_nesting - 1).*
  - indent_per_level_spaces (int): nº de espacios que equivalen a 1 nivel de
      indentación para listas (PARSEO, no px en render).
#
Normalización:
  - normalize(text):
      · Reemplaza '\\t' por ' ' * tab_size.
      · Convierte CRLF/CR a LF.
    (parse() NO llama a normalize() automáticamente; úsala si necesitas unificar saltos/tabs.)
#
BLOQUES SOPORTADOS
------------------
1) Regla horizontal
   Sintaxis: una línea que contenga exactamente tres guiones (con o sin espacios alrededor)
      --- 
   Regex: r'^\\s*---\\s*$'
   Emite: {"type": "hr"}
#
2) Encabezados (h1..h6)
   Sintaxis: '# ' | '## ' | ... | '###### ' seguido del texto del título
      # Título 1
      ## Título 2
      ...
      ###### Título 6
   Regex: r'^(#{1,6})\\s+(.*)$'
   Emite: {"type": "h1"|...|"h6", "text": "..."}
#
3) Bloques de código "fence"
   Sintaxis: líneas con ``` para abrir/cerrar. No se detecta lenguaje.
      ```
      cualquier texto (se preserva tal cual, incluidas líneas vacías)
      ```
   Regex apertura/cierre: r'^\\s*```.*$'
   Emite: {"type": "code", "text": "<contenido tal cual>"}
   Nota: si el EOF llega con fence abierto, también se emite como bloque de código.
#
4) Bloques de código indentado  (DESACTIVADO EN ESTA IMPLEMENTACIÓN)
   En esta implementación se ha desactivado la detección automática de
   "bloques de código indentado" (líneas que comienzan con 4 espacios)
   porque:

     - pandoc genera listas con líneas de continuación sangradas con
       cuatro espacios (no son bloques de código reales).
     - Eso producía parches blancos indeseados en la ayuda al tratar
       esas líneas de continuación como código.

   Recomendación: generar el manual con pandoc usando fences ``` para
   los bloques de código reales y evitar confiar en indentaciones para
   indicar código.

   En consecuencia, actualmente no se emiten bloques de tipo "code"
   basados en indentación; los bloques de código se obtienen sólo a
   partir de fences ``` (ver sección 3).
#
5) Listas
   • Listas no ordenadas (UL):
        - Item uno
        * Item dos
      Regex: r'^(\\s*)([-*])\\s+(.*)$'
      Emite: {"type": "ul", "items": [{"level": L, "text": "..."} ...]}
#
   • Listas ordenadas (OL):
        1. Primer item
        2. Segundo item
      Regex: r'^(\\s*)(\\d+)\\.\\s+(.*)$'
      Emite: {"type": "ol", "items": [{"level": L, "num": N, "text": "..."} ...]}
#
   Nivel de indentación en ambos casos:
      L = min( len(espacios_previos) // indent_per_level_spaces,
               max_list_nesting - 1 )
     (No se parsean subpárrafos dentro de items; solo se acumulan líneas consecutivas
      que sigan siendo del mismo tipo de lista. No hay checkboxes, blockquotes ni imágenes.)
#
6) Párrafos
   Cualquier bloque de líneas consecutivas que no encaje en las reglas anteriores,
   separado por líneas en blanco. Se emite con saltos '\\n' internos si los hay.
   Emite: {"type": "p", "text": "..."}
#
ORDEN DE DETECCIÓN DE BLOQUES en parse():
  1) Saltos de línea vacíos (se ignoran entre bloques, excepto dentro de fence)
  2) Fence ```
  3) (Si in_fence) → acumular literal
  4) Regla horizontal (---)
  5) Encabezados (#..######)
  6) Código indentado (≥4 espacios)
  7) Listas (UL/OL)
  8) Párrafo
#
INLINE (tokenize_inline)
------------------------
1) Código en línea
   Sintaxis: `contenido`
   Regex: r'`([^`]+)`'
   Comportamiento:
     - Se "protege" primero: el contenido de `...` NO se procesa para negrita/itálica/links.
   Emite runs con: {"text": "...", code: True, bold: False, italic: False, link: False}
#
2) Énfasis
   • Negrita+itálica: ***texto***
      Regex: r'(?<!\\w)\\*\\*\\*(.+?)\\*\\*\\*(?!\\w)'
   • Negrita: **texto**
      Regex: r'(?<!\\w)\\*\\*(.+?)\\*\\*(?!\\w)'
   • Itálica: *texto*
      Regex: r'(?<!\\w)\\*(.+?)\\*(?!\\w)'
#
   Notas importantes:
     - Se aplican en este orden: *** → ** → *
     - Se exigen límites de “no-palabra” en ambos lados (negative lookbehind/ahead con \\w):
         · 'precio*2' NO activa itálica
         · '**negrita**,' SÍ (la coma no rompe el match)
     - Flags resultantes por run:
         · bold = True si (b OR bi)
         · italic = True si (i OR bi)
#
3) URLs
   Sintaxis: http://... o https://... (sin corchetes)
   Regex: r'(https?://\\S+)'
   Comportamiento:
     - Se marcan como link=True (y code=False).
     - Dentro de `code` NO se linka.
     - Nota: \\S+ captura hasta el siguiente espacio; si hay puntuación pegada
             al final (p. ej. una coma), se incluirá en el enlace.
#
Salida de tokenize_inline(text) → List[run]
   Cada run es un dict con claves:
     { "text": str, "bold": bool, "italic": bool, "code": bool, "link": bool }
#
LIMITACIONES/Diseño intencionado:
  - Títulos solo h1..h6.
  - No hay blockquotes, imágenes, tablas, ni enlaces estilo [texto](url).
  - Items de lista: solo texto plano por línea; no hay subbloques dentro del item.
  - El análisis inline no se realiza dentro de bloques de código (fence o indentado).
  - Los "límites de palabra" para * ** *** evitan falsos positivos dentro de tokens alfanuméricos.
-----------------------------------------------------------------------------

"""


"""NOTA1:
La instrucción from __future__ import annotations en Python 3.12 sirve para habilitar la evaluación diferida de las 
anotaciones de tipo. Esto significa que, en lugar de evaluar las anotaciones en el momento en que se define una 
función o clase, se evalúan como cadenas de texto (strings). Esta característica es útil para evitar problemas con 
referencias circulares y para permitir que las anotaciones hagan referencia a nombres que aún no se han definido

NOTA2:
Se puede generar un fichero con LibreOffice y pasarlo a formato markdown luego con:
    pandoc archivo.odt -t markdown -o archivo.md
"""
# Programa  : help_core.py
import os
import re
import json
import webbrowser
import unicodedata
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from .help_mini_markdown import _MiniMarkdown
except Exception:
    import traceback
    traceback.print_exc()
    raise

try:
    from .help_viewer_impl import HelpViewer, HelpConfig, DEFAULT_STYLE, RGB 
except Exception:
    import traceback
    traceback.print_exc()
    raise

import pygame


# ---------------------------------------------------------------------------------
# Función de conveniencia para mostrar ayuda Markdown como overlay modal en Pygame
# ---------------------------------------------------------------------------------
def ShowHelpOverlay(
    display: pygame.Surface,
    md_text: str,
    title: str = "Ayuda",
    *,
    exit_keys: Tuple[int, ...] = (pygame.K_ESCAPE,),
    fps: int = 60,
    kernel_bg: Tuple[int, int, int] = (200, 200, 200),
    wheel_step: int = 48,
    scroll_limit_cooldown_ms: int = 300,
) -> None:
    """
    Muestra una ayuda en formato Markdown como overlay modal sobre el display.

    Parameters
    ----------
    display:
        Surface principal de Pygame donde se dibujará el overlay.
    md_text:
        Contenido en Markdown a mostrar.
    title:
        Título de la ayuda.
    exit_keys:
        Teclas que cierran la ayuda (por defecto ESC).
    fps:
        Límite de FPS del bucle modal.
    kernel_bg:
        Color de fondo del área de ayuda.
    wheel_step:
        Paso de scroll por rueda.
    scroll_limit_cooldown_ms:
        Cooldown del “límite” de scroll (si está implementado en el viewer).

    Returns
    -------
    None
    """
    if display is None:
        raise ValueError("display no puede ser None")

    rect = display.get_rect()

    # Guardamos el frame actual para restaurar por debajo del overlay
    canvas = display.copy()

    # Construimos configuración de ayuda
    cfg = HelpConfig(
        md_text=md_text,
        title=title,
        size=display.get_size(),
        kernel_bg=kernel_bg,
        wheel_step=wheel_step,
        scroll_limit_cooldown_ms=scroll_limit_cooldown_ms,
    )

    viewer = HelpViewer(cfg)
    viewer.on_mount(rect)

    clock = pygame.time.Clock()

    # Guardar y ajustar autorepeat durante el modal (mejora navegación con teclas)
    prev_delay, prev_interval = pygame.key.get_repeat()
    pygame.key.set_repeat(250, 40)

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                if event.type == pygame.KEYDOWN and event.key in exit_keys:
                    running = False
                    continue

                viewer.handle_event(event)

            # Restaurar y dibujar overlay
            display.blit(canvas, (0, 0))
            viewer.draw(display, rect)
            pygame.display.flip()
            clock.tick(fps)
    finally:
        viewer.on_unmount()

        # Restaurar autorepeat al estado anterior
        if prev_delay == 0 and prev_interval == 0:
            pygame.key.set_repeat()
        else:
            pygame.key.set_repeat(prev_delay, prev_interval)


def open_help_standalone(
    md_text: str,
    title: str = "Ayuda",
    size: Tuple[int, int] = (800, 480),
    *,
    style_json_path: Optional[str] = None,
    style_variant: Optional[str] = None,
    style_overrides: Optional[Dict[str, Any]] = None,
    fonts_dir: Optional[str] = None,
    help_font_file: Optional[str] = None,
    help_code_font_file: Optional[str] = None,
    indent_spaces_per_level: int = 2,
    visual_indent_px: int = 24,
    wheel_step: int = 48,
    kernel_bg: Optional[RGB] = None,
    on_scroll_limit: Optional[Callable[[str], None]] = None,
    scroll_limit_cooldown_ms: int = 0,
) -> None:
    cfg = HelpConfig(
        md_text=md_text,
        title=title,
        size=size,
        style_json_path=style_json_path,
        style_variant=style_variant,
        style_overrides=style_overrides,
        fonts_dir=fonts_dir,
        help_font_file=help_font_file,
        help_code_font_file=help_code_font_file,
        indent_spaces_per_level=indent_spaces_per_level,
        visual_indent_px=visual_indent_px,
        wheel_step=wheel_step,
        kernel_bg=kernel_bg,
        on_scroll_limit=on_scroll_limit,
        scroll_limit_cooldown_ms=scroll_limit_cooldown_ms,
    )
    HelpViewer(cfg).open_window()


def ShowHelpOverlay(
    display: pygame.Surface,
    md_text: str,
    title: str = "Ayuda",
    *,
    exit_keys: Tuple[int, ...] = (pygame.K_ESCAPE,),
    fps: int = 60,
    kernel_bg: Tuple[int, int, int] = (200, 200, 200),
    wheel_step: int = 48,
    scroll_limit_cooldown_ms: int = 300,
) -> None:
    cfg = HelpConfig(
        md_text=md_text,
        title=title,
        size=(display.get_width(), display.get_height()),
        kernel_bg=kernel_bg,
        wheel_step=wheel_step,
        scroll_limit_cooldown_ms=scroll_limit_cooldown_ms,
    )
    viewer = HelpViewer(cfg)
    viewer.on_mount(display.get_rect())

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(fps)
        viewer.update(dt)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN and e.key in exit_keys:
                running = False
            else:
                viewer.handle_event(e)

        viewer.draw(display, display.get_rect())
        pygame.display.flip()

    viewer.on_unmount()

