from __future__ import annotations
########## Copyright (c) ##########################################################
# SPDX-FileCopyrightText: 2026 Antonio Castro Snurmacher <acastro0841@gmail.com>
# SPDX-License-Identifier: MIT
###################################################################################

"""
Fichero: demo_help_show_overlay_circles.py
Descripción Breve: Demo de ShowHelpOverlay() invocable desde una aplicación en marcha (animación con círculos rebotando)
"""

from dataclasses import dataclass
from typing import Tuple, List

import pygame
import random


from help_core_pygame import ShowHelpOverlay


Color = Tuple[int, int, int]


@dataclass
class BouncingCircle:
    """
    Círculo con movimiento (velocidad) que rebota en los límites de la ventana.
    """
    position: pygame.Vector2
    velocity: pygame.Vector2
    radius_small: int
    radius_big: int
    color: Color
    is_big: bool = False

    @property
    def radius(self) -> int:
        """
        Radio actual en función del modo (pequeño/grande).
        """
        return self.radius_big if self.is_big else self.radius_small

    def toggle_size(self) -> None:
        """
        Alterna el tamaño del círculo.
        """
        self.is_big = not self.is_big

    def update(self, dt_seconds: float, bounds: pygame.Rect) -> None:
        """
        Actualiza posición y aplica rebote con los bordes.

        Parameters
        ----------
        dt_seconds:
            Delta de tiempo en segundos desde el último frame.
        bounds:
            Rectángulo de límites (normalmente display.get_rect()).
        """
        self.position += self.velocity * dt_seconds

        r = self.radius

        # Rebote horizontal
        if self.position.x - r < bounds.left:
            self.position.x = bounds.left + r
            self.velocity.x *= -1
        elif self.position.x + r > bounds.right:
            self.position.x = bounds.right - r
            self.velocity.x *= -1

        # Rebote vertical
        if self.position.y - r < bounds.top:
            self.position.y = bounds.top + r
            self.velocity.y *= -1
        elif self.position.y + r > bounds.bottom:
            self.position.y = bounds.bottom - r
            self.velocity.y *= -1

    def draw(self, surface: pygame.Surface) -> None:
        """
        Dibuja el círculo en pantalla.
        """
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.position.x), int(self.position.y)),
            self.radius
        )


def build_help_markdown() -> str:
    """
    Texto de ayuda en Markdown, usado por ShowHelpOverlay().

    Returns
    -------
    str
        Texto Markdown.
    """
    return """
# Ayuda: ShowHelpOverlay() invocable en ejecución

Esta demo demuestra como **una aplicación ya en marcha** (con animación) puede invocar un overlay de ayuda, y al salir de la ayuda la ejecución **continúa** donde estaba.
Es ideal como complemento para cualquier programa de Pygame.

## Controles
- **ESC**: terminar la demo
- **SPACE**: alternar el tamaño de los círculos
- **F1**: abrir/cerrar ayuda (overlay modal)

## Qué observar
1. La animación está activa antes de invocar la ayuda.
2. Al pulsar **F1**, la ayuda aparece como overlay modal.
3. Al pulsar la barra espciadora cambiara de estado de grande a pequeña y viceversa
4. Al salir desde la ayuda con (ESC o F1), vuelves a ver la animación.
5. Al pulsar la tecla ESC desde la animación se termina la ejecucion del programa.
6. Si activamos y desactivamos la ayuda con pocos segundos de diferencia observaremos que la animación no queda congelada sino que aparece como si hubiera estado funcionando todo el rato.

### NOTA:
(Es mejo entrar y salir de la ayuda con F1 ya que pulsar por error ESC dos veces seguidas se sale de la animación)

## Conclusión:
Este patrón permite añadir ayuda contextual a cualquier demo o aplicación de forma bastante cómoda.
"""


def draw_hud(surface: pygame.Surface, font: pygame.font.Font) -> None:
    """
    Dibuja instrucciones mínimas en la pantalla principal.

    Parameters
    ----------
    surface:
        Surface principal.
    font:
        Fuente para renderizado del HUD.
    """
    lines = [
        "Demo: ShowHelpOverlay() invocable en ejecución",
        "<ESC>: salir   |   <Barra espaciadora>: alternar tamaño   |   <F1>: ayuda (on/off)",
    ]

    x_pos = 18
    y_pos = 14

    for line in lines:
        text_surface = font.render(line, True, (20, 20, 20))
        surface.blit(text_surface, (x_pos, y_pos))
        y_pos += 28


def create_circles(
    bounds: pygame.Rect,
    num_circles: int = 8,
    *,
    offset_range: int = 300,
    radius_small_min: int = 25,
    radius_small_max: int = 40,
    velocity_min: int = -200,
    velocity_max: int = 200,
    rng: random.Random | None = None,
) -> List["BouncingCircle"]:
    """
    Crea una lista de círculos con posiciones, velocidades, radios y colores aleatorios.

    Parameters
    ----------
    bounds:
        Rectángulo de límites (normalmente display.get_rect()).
    num_circles:
        Número de círculos a generar.
    offset_range:
        Rango máximo de descentramiento respecto al centro: [-offset_range, +offset_range].
    radius_small_min:
        Radio mínimo (modo pequeño).
    radius_small_max:
        Radio máximo (modo pequeño).
    velocity_min:
        Velocidad mínima por componente (x, y).
    velocity_max:
        Velocidad máxima por componente (x, y).
    rng:
        Generador aleatorio opcional para reproducibilidad.

    Returns
    -------
    list[BouncingCircle]
        Lista de círculos generados.
    """
    if rng is None:
        rng = random.Random()

    circles: List["BouncingCircle"] = []

    for _ in range(num_circles):
        radius_small = rng.randint(radius_small_min, radius_small_max)
        radius_big = radius_small * 3

        offset_x = rng.randint(-offset_range, offset_range)
        offset_y = rng.randint(-offset_range, offset_range)

        # Posición base en el centro, descentrada según rango solicitado
        position = pygame.Vector2(bounds.centerx + offset_x, bounds.centery + offset_y)

        velocity_x = rng.randint(velocity_min, velocity_max)
        velocity_y = rng.randint(velocity_min, velocity_max)

        # Evitar círculo “parado” por casualidad (0,0) si no lo quieres
        if velocity_x == 0 and velocity_y == 0:
            velocity_x = velocity_max if velocity_max != 0 else 1

        velocity = pygame.Vector2(velocity_x, velocity_y)

        # Color aleatorio RGB
        color = (rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))

        circles.append(
            BouncingCircle(
                position=position,
                velocity=velocity,
                radius_small=radius_small,
                radius_big=radius_big,
                color=color,
            )
        )
    return circles


def main() -> int:
    """
    Punto de entrada de la demo.

    Returns
    -------
    int
        Código de retorno del proceso.
    """
    pygame.init()

    window_width = 1200
    window_height = 750
    display = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("demo_help_show_overlay_circles - ShowHelpOverlay()")

    bounds = display.get_rect()
    font = pygame.font.SysFont(None, 26)
    clock = pygame.time.Clock()

    circles = create_circles(bounds)
    help_text = build_help_markdown()

    running = True
    while running:
        dt_ms = clock.tick(60)
        dt_seconds = dt_ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    continue

                if event.key == pygame.K_SPACE:
                    # Alternar tamaño de todos los círculos
                    for circle in circles:
                        circle.toggle_size()

                if event.key == pygame.K_F1:
                    # Importante: ShowHelpOverlay() es modal y retorna.
                    # Al retornar, el bucle principal sigue y la animación continúa.
                    ShowHelpOverlay(
                        display=display,
                        md_text=help_text,
                        title="Ayuda de la demo",
                        exit_keys=(pygame.K_ESCAPE, pygame.K_F1),
                        fps=60,
                        kernel_bg=(222, 222, 222),
                        wheel_step=48,
                        scroll_limit_cooldown_ms=300,
                    )

        # Actualizar simulación
        for circle in circles:
            circle.update(dt_seconds, bounds)

        # Dibujar escena
        display.fill((170, 170, 170))
        for circle in circles:
            circle.draw(display)

        draw_hud(display, font)
        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
