########## Copyright (c) ##########################################################
# SPDX-FileCopyrightText: 2025 Antonio Castro Snurmacher <acastro0841@gmail.com>
# SPDX-License-Identifier: MIT
###################################################################################

"""
######################################################################################################################
Programa  : demo_help_standalone.py
Versión   : 2.0  (17-dic-2025)
Licencia de uso MIT

Descripción breve:
    Demo de uso Demo standalone de help_core 

Descripción extendida:
    Demo de uso standalone de help_core con efecto de sonido al alcanzar los límites 
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

from contextlib import ExitStack
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Optional, Callable

import pygame

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



TEST_MD="""
# Ayuda para *demo_help_standalone* 

(Pulse la tecla **F1** para salir)

### 1 · Descripción del Programa: *demo_help_standalone.py*
Este programa es una demostración autónoma del módulo *help_core_pygame* (una librería de ayuda o documentación para aplicaciones Pygame). 
Su función principal es mostrar cómo se renderiza y se presenta un texto de ayuda formateado en Markdown reducido dentro de una ventana sin depender de otros componentes de interfaz de usuario.
Muestra la forma más sencilla de invocar la funcionalidad de ayuda (open_help_standalone) directamente desde una aplicación Pygame, sin necesidad de encapsularla en un widget o ventana emergente más complejo.

### 2 . Prueba de Configuración: 
Permite probar varias opciones de configuración del motor de renderizado, como el tamaño de la ventana (size), el fondo (kernel_bg), el manejo de la indentación (indent_spaces_per_level, visual_indent_px) y el comportamiento al límite del desplazamiento (on_scroll_limit, scroll_limit_cooldown_ms).


---

# Test de Markdown reducido — help_core_pygame

Este documento prueba las marcas soportadas en este subconjunto de markdown soportado por help_core_pygame: 
- Encabezados (H1/H2/H3) 
- **Megrita**
- *Itálica*
- Mezcla ***negrita+itálica***
- `Código inline`
- Listas (viñetas OL • y numeradas UL 1.)
- Líneas separadoras horizontale horizontales
- URLs como https://www.pygame.org/docs/ (solo cambia el color de negro a azul)
- Bloques de código (fenced) (``` y 4 espacios). Se muestra resaltado sobre un rectángulo más claro.

Sugerencia para la prueba: usar indent_per_level=2 y tab_size=4.

---

## 1. Encabezados (H2)

Texto normal bajo H2. Debe aplicar espaciados verticales superiores e inferiores.

### 1.1. Subtítulo (H3)

Línea tras H3. Comprobar interlineado (hlp_LineHeightPct) y que **negrita** / *itálica* funcionen aquí también.

Párrafo con énfasis mixto:
- Solo **negrita**.
- Solo *itálica*.
- Combinado ***negrita+itálica*** en una misma palabra.
- Asteriscos literales: este*texto no debería activar itálica dentro*de*palabras*.
- Inline code con asteriscos: `**esto no es negrita**` y con tildes: `áéíóú`.

Separador:

---

## 2. Listas

### 2.1. Viñetas (UL)

- Nivel 0, ítem A con una línea muy muy larga que debería envolver sin partir palabras, para comprobar el wrapping alrededor del ancho disponible en el rect del kernel. Repite varias palabras para forzar el salto y verificar que no se corta ninguna palabra en el proceso.
  - Nivel 1, ítem B (indentado con 2 espacios).
    - Nivel 2, ítem C. Contiene `inline code` y **negrita**.
      - Nivel 3, ítem D. Profundidad máxima recomendada.
        - Nivel 4, ítem E. Si max_list_nesting es 4, este debería "quedarse" al nivel permitido.

* Otra rama con asterisco como marcador.
  * Subnivel con asterisco.
    * Sub-subnivel.

### 2.2. Numeradas (OL)

1. Ítem 1
2. Ítem 2 con una oración larga que debe partir por espacios y no cortar palabras. También contiene un enlace: http://example.com/test?param=1#anchor
3. Ítem 3
   1. Subítem 3.1
   2. Subítem 3.2 con *itálica* y `inline code`.
      1. Subítem 3.2.1 profundo
4. Ítem 4 empezando en número mayor (solo ver que se renderiza el índice literal).

---

## 3. Código

### 3.1. Código en bloque (fenced)

```python
# Comentario: este bloque está dentro de triple backtick.
import pygame

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 30))  # azul muy oscuro
        pygame.display.flip()

```

Fin de la ayuda. (Pulse la tecla **F1** para salir)




"""


def main() -> None:
    # Inicialización básica de pygame (audio incluido).
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception as exc:  # noqa: BLE001
        # Si audio no está disponible, la demo debe seguir funcionando sin beep.
        print(f"ADVERTENCIA: No se pudo inicializar pygame.mixer: {exc}")

    asset_manager = PackageAssetManager("help_core_pygame")

    # Carga robusta del beep desde el paquete instalado.
    beep_sound = load_sound(asset_manager, "assets/mp3/beep_scroll.mp3")

    def on_scroll_limit(_where: str) -> None:
        # _where suele indicar top/bottom si tu API lo pasa; aquí no lo necesitamos.
        if beep_sound is not None:
            try:
                beep_sound.play()
            except Exception as exc:  # noqa: BLE001
                print(f"ADVERTENCIA: No se pudo reproducir el beep: {exc}")

    try:
        # Ajusta parámetros según tu firma real de open_help_standalone.
        open_help_standalone(
            TEST_MD,
            title="Help Standalone - Asset safe",
            size=(1200, 900),
            on_scroll_limit=on_scroll_limit,
            scroll_limit_cooldown_ms=300,
        )
    finally:
        # Importante: libera recursos temporales (si el paquete requiere extracción).
        asset_manager.close()
        try:
            pygame.quit()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()

