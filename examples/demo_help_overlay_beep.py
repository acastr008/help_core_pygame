########## Copyright (c) ##########################################################
# SPDX-FileCopyrightText: 2025 Antonio Castro Snurmacher <acastro0841@gmail.com>
# SPDX-License-Identifier: MIT
###################################################################################

"""
######################################################################################################################
Programa  : demo_help_overlay_beep.py
Versión   : 2.0  (17-dic-2025)
Licencia de uso MIT

Descripción breve:
    Demo de uso Demo embebido de help_core 

Descripción extendida:
    Demo de uso embebido de help_core con efecto de sonido al alcanzar los límites 
    del scroll (top / bottom).
    Permite visualizar en una pantalla un texto de ayuda en formato markdown. 
    Carga assets empaquetados mediante importlib.resources.as_file() para obtener
    una ruta REAL en disco (aunque el paquete esté dentro de un wheel/zip).
    Incluye un pequeño gestor de assets y una demo de help_core_pygame.

Requisitos:
    - Python 3.11
    - Pygame
    - Módulo help_core en el PYTHONPATH
    - Fichero de sonido: mp3/beep_scroll.mp3
######################################################################################################################
"""
from __future__ import annotations

import sys, os
from contextlib import ExitStack
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Optional, Callable, Tuple
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

try:
    # API típica de tu librería (ajusta si tu nombre o función cambia)
    from help_core_pygame import open_help_standalone
except Exception as exc:  # noqa: BLE001
    raise SystemExit(
        "No se pudo importar 'help_core_pygame'. "
        "Instala el paquete o ejecuta en un entorno donde esté disponible."
    ) from exc


@dataclass
class PackageAssetManager:
    """
    Gestor de assets empaquetados.

    Idea clave:
    - resources.files(...) devuelve un objeto "traversable" (navegable) que puede no ser un Path real.
    - resources.as_file(...) garantiza un Path REAL (en disco) mientras el contexto esté abierto.

    Este manager usa ExitStack para mantener vivos esos contextos durante toda la ejecución.
    """
    package_name: str
    _exit_stack: ExitStack = ExitStack()

    def close(self) -> None:
        """Cierra el ExitStack y libera recursos temporales."""
        self._exit_stack.close()

    def get_real_path(self, relative_path: str) -> Path:
        """
        Devuelve un Path REAL del sistema de archivos para un asset.

        :param relative_path: Ruta relativa dentro del paquete (ej. "assets/mp3/beep_scroll.mp3")
        :return: Path real en disco válido para librerías externas (pygame, etc.)
        :raises FileNotFoundError: Si el recurso no existe en el paquete instalado.
        """
        resource_entry = resources.files(self.package_name).joinpath(relative_path)

        # Hacemos exists() que es la comprobación correcta a nivel de "recurso dentro del paquete".
        if not resource_entry.exists():
            raise FileNotFoundError(
                f"Asset no encontrado en el paquete '{self.package_name}': {relative_path}"
            )

        # as_file(...) garantiza un Path real incluso si el paquete está en zip/wheel.
        real_path = self._exit_stack.enter_context(resources.as_file(resource_entry))
        print ("Path Asset OK= ", real_path)
        return Path(real_path)


def load_sound(asset_manager: PackageAssetManager, relative_path: str) -> Optional[pygame.mixer.Sound]:
    """
    Carga un sonido desde assets empaquetados, devolviendo None si no se puede.

    :param asset_manager: Gestor de assets del paquete.
    :param relative_path: Ruta relativa del mp3 dentro del paquete.
    :return: pygame.mixer.Sound o None si falla.
    """
    try:
        sound_path = asset_manager.get_real_path(relative_path)
        return pygame.mixer.Sound(str(sound_path))
    except FileNotFoundError as exc:
        print(f"ADVERTENCIA: {exc}")
        return None
    except Exception as exc:  # noqa: BLE001
        # Captura genérica para evitar que una demo se caiga por audio/SDL.
        print(f"ADVERTENCIA: No se pudo cargar el sonido '{relative_path}': {exc}")
        return None



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

    asset_manager = PackageAssetManager("help_core_pygame")

    # Carga robusta del beep desde el paquete instalado.
    beep_sound = load_sound(asset_manager, "assets/mp3/beep_scroll.mp3")

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
    tab=' '*10
    ui_text = f"{tab}1) Prueba a dibujar algo con el ratón.{tab}2) Pulsa F1 para ver la ayuda.{tab}3) Pulsa ESC para salir."
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

