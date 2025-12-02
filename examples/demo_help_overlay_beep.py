
########## Copyright (c) ##########################################################
# SPDX-FileCopyrightText: 2025 Antonio Castro Snurmacher <acastro0841@gmail.com>
# SPDX-License-Identifier: MIT
###################################################################################

"""
######################################################################################################################
Programa  : demo_help_overlay_beep.py
Versión   : 1.0  (22-nov-2025)
Licencia de uso MIT

Descripción breve:
    Demo de uso embebido de help_core con efecto de sonido al alcanzar
    los límites del scroll (top / bottom), espaciado 300 ms.

Requisitos:
    - Python 3.11
    - Pygame
    - Módulo help_core en el PYTHONPATH
    - Fichero de sonido: mp3/beep_scroll.mp3
######################################################################################################################
"""

from __future__ import annotations

import sys, os
from typing import Tuple

import pygame

from help_core_pygame import HelpConfig, HelpViewer


RGB = Tuple[int, int, int]


HELP_MD_TEXT = """# Demo de ayuda embebida

## Esta demo realizada usando pygame muestra:

- Una **pantalla de dibujo** con el ratón.
- Para pintar un trazos hay que:
   - Mantener el botón izquierdo del ratón pulsado.
   - Mover el ratón.
   - al levantar el ratón será como levantar el pincel pa poder pintar otro trazo en otro trazo en otro lado.
   - Para que el trazo sea contínuo coviene no desplazar demasiado rápido el ratón mientras se pinta.

- Al pulsar `F1`, se abre esta ayuda como *overlay*.
- Usa el modo embebido de `HelpViewer` (no `open_help_standalone`).
- Al salir de la ayuda se recupera el contenido de la pantalla y se puede continuar dibujando.

## Controles básicos:

- **Ratón botón izquierdo**: dibujar.
- **Ratón botón derecho**: borrar el lienzo.
- **F1**: abrir/cerrar ayuda.
- **ESC**: salir del programa.

## Observaciones:

- La demo solo pretende mostrar una aplicación que haga un uso básico de ratón.
- Se trata de un mero pretexto para ver como se integra este sistema de ayuda en un programa,
- Sirve para verificar el buen funcionamiento del sistema de ayuda.
- En especial conviene verificar el buen funcionamiento de:
   - El sistema de scroll del sistema de ayuda. (Por eso tanto bla, bla, bla, aquí)
      - Mediante uso de flechas arriba y abajo.
      - Mediante la ruedecita del ratón.
      - Mediante el arrastre del cursor en el margen derecho.
   - El efecto de sonido cuando se alcanza el limite del desplazamiento del texto arriba o abajo haciendo scroll.
   - El funcionamiento del analizador del texto en formato markdown,
   - Los eventos de ratón.
"""


def create_help_viewer(screen: pygame.Surface, beep_sound: pygame.mixer.Sound | None) -> tuple[HelpViewer, pygame.Rect]:
    """Crea y monta un HelpViewer a pantalla completa con callback de beep opcional."""

    def _on_scroll_limit(_where: str) -> None:
        # No diferenciamos top/bottom, simplemente sonamos el beep si existe.
        if beep_sound is not None:
            beep_sound.play()

    size = screen.get_size()
    cfg = HelpConfig(
        md_text=HELP_MD_TEXT,
        title="Ayuda demo overlay con beep",
        size=size,
        kernel_bg=(222, 222, 222),
        wheel_step=48,
        on_scroll_limit=_on_scroll_limit,
        scroll_limit_cooldown_ms=300,
    )
    viewer = HelpViewer(cfg)
    rect = screen.get_rect()
    viewer.on_mount(rect)
    return viewer, rect

def help_overlay_loop(screen: pygame.Surface, canvas: pygame.Surface) -> None:
    """Bucle modal de ayuda superpuesto al contenido, con beep de límite de scroll."""

    # --- CALCULAR RUTA DEL ASSET  ----------------------------------------------------------------------
    # 1. Obtener la ruta del directorio del script actual (examples/)
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    # 2. Definir la ruta base del proyecto subiendo un nivel
    PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')
    
    # 3. Construir la ruta absoluta al asset, siguiendo la estructura src/paquete/assets/mp3
    asset_path = os.path.join(PROJECT_ROOT, "src", "help_core_pygame", "assets", "mp3", "beep_scroll.mp3")
    # ----------------------------------------------------------------------------------------------------
    
    # Intentamos cargar el efecto de sonido. Si falla, la demo sigue sin beep.
    beep_sound: pygame.mixer.Sound | None
    try:
        # Usar la ruta absoluta
        beep_sound = pygame.mixer.Sound(asset_path)
    except pygame.error as exc:
        print(f"Error cargando 'mp3/beep_scroll.mp3' en demo_help_overlay_beep: {exc}")
        beep_sound = None

    viewer, rect = create_help_viewer(screen, beep_sound)

    clock = pygame.time.Clock()

    # Guardar estado previo de autorepeat de teclas
    prev_key_delay, prev_key_interval = pygame.key.get_repeat()

    # Activar autorepeat mientras está activa la ayuda
    pygame.key.set_repeat(250, 40)

    viewer, rect = create_help_viewer(screen, beep_sound)

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_F1):
                    running = False
                else:
                    viewer.handle_event(event)

            screen.blit(canvas, (0, 0))
            viewer.draw(screen, rect)
            pygame.display.flip()
            clock.tick(60)
    finally:
        viewer.on_unmount()

        # Restaurar configuración previa de autorepeat
        if prev_key_delay == 0 and prev_key_interval == 0:
            # Sin autorepeat antes: lo desactivamos explícitamente
            pygame.key.set_repeat()
        else:
            pygame.key.set_repeat(prev_key_delay, prev_key_interval)


def main() -> None:
    pygame.init()
    width, height = 1200, 900
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Demo help_core overlay con beep (dibujo con ratón)")

    clock = pygame.time.Clock()

    canvas = pygame.Surface((width, height))
    canvas.fill((255, 255, 255))

    drawing_color: RGB = (0, 0, 0)
    brush_radius: int = 6

    # Fuente para el mensaje inferior
    ui_font = pygame.font.Font(None, 28)
    ui_text = "Pulsa F1 para ver la ayuda. ESC para salir."
    ui_text_color: RGB = (0, 0, 0)
    ui_bg_color: RGB = (100, 100, 250)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F1:
                    help_overlay_loop(screen, canvas)

            elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                pygame.draw.circle(canvas, drawing_color, event.pos, brush_radius)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                canvas.fill((255, 255, 255))

        screen.blit(canvas, (0, 0))

        # Pintar banda inferior con el mensaje de ayuda (F1)
        text_surface = ui_font.render(ui_text, True, ui_text_color)
        text_rect = text_surface.get_rect()
        margin_y = 4
        margin_x = 10

        band_height = text_rect.height + 2 * margin_y
        band_rect = pygame.Rect(0, height - band_height, width, band_height)

        pygame.draw.rect(screen, ui_bg_color, band_rect)
        text_rect.midleft = (margin_x, band_rect.centery)
        screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(120)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()

