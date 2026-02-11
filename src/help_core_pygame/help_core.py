from __future__ import annotations

# ====================================================================================================
# Proyecto : help_core_pygame
# Archivo  : help_core.py
# Autor    : Antonio Castro Snurmacher 
# Licencia : MIT 
#
# Fecha última modificación: (4-feb-2026) 
#
# Descripción:
# ------------
#   Visor de ayuda independiente, basado únicamente en Pygame, con soporte de Markdown reducido.
#     - Puede abrir su propia ventana (open_window) o renderizar en una surface/rect.
#     - Estilos opcionales vía JSON + variant y/o style_overrides.
#
# Requisitos:
# -----------
#   - Versión Python     : >_3.9 
#   - Pygame
#
# Documentación en español: https://github.com/acastr008/help_core_pygame/blob/main/docs/INDEX_es.md 
# Documentation in English: https://github.com/acastr008/help_core_pygame/blob/main/docs/INDEX_en.md 
# ====================================================================================================


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
# NOTA (ShowHelpOverlay - variante activa):
# - Esta es la implementación “oficial” en el módulo: al ser la última definición efectiva,
#   es la que realmente se exporta y ejecutan las demos.
# - Modal/bloqueante: detiene el loop llamador mientras la ayuda está abierta.
# - En este proyecto la ventana de ayuda solo cambia por scroll; por tanto no depende de
#   animaciones ni de update(dt) para refrescarse (redibuja en cada iteración del bucle).
# - Punto importante: el “salto” de tiempo al volver al loop principal (si el juego usa dt)
#   NO se resuelve aquí; debe gestionarlo el llamador reseteando su Clock o descartando el
#   primer dt tras cerrar la ayuda.
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
    base_dir: Optional[str] = None,
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
        base_dir=base_dir,        
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
    base_dir: Optional[str] = None,
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
        base_dir=base_dir,
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

