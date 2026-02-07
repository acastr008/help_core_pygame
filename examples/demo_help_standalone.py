#!/usr/bin/python3
from __future__ import annotations

# ===================================================================================================================
# Fecha última modificación: (31-ene-2026)  
# Nombre del archivo : demo_help_standalone.py
# Descripción breve  : Demo de uso Demo standalone de help_core
# Autor              : Antonio Castro Snurmacher 
# Licencia de uso    : MIT 
# 
# Descripción extendida:
# ----------------------
#    Demo de uso standalone de help_core con efecto de sonido al alcanzar los límites 
#    del scroll (top / bottom).
#    Permite visualizar en una pantalla un texto de ayuda en formato markdown. 
#    Carga assets empaquetados mediante importlib.resources.as_file() para obtener
#    una ruta REAL en disco (aunque el paquete esté dentro de un wheel/zip).
#    Incluye un pequeño gestor de assets y una demo de help_core_pygame.
#
# Requisitos:
# -----------
#   - Versión Python     : >_3.9 
#   - Pygame
#   - Módulo help_core en el PYTHONPATH
#   - Fichero de sonido: mp3/beep_scroll.mp3
# ===================================================================================================================

from contextlib import ExitStack
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Optional, Callable
from help_core_pygame import open_help_standalone

import os
import pygame


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
    _exit_stack: ExitStack = field(default_factory=ExitStack)


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

# Demostración autónoma (standalone) del módulo — help_core_pygame

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

Existe otra demo (demo_mini_MarkDown_TEST) muy similar a esta, pero con un contenido de texto de ayuda diferente centrada en la verificación detallada del funcionamiento del parser (analizador de la gramática de lenguaje MarkDown implementado) y del visualizador.

---

(Para forzar la visibilidad de elementos ocultos: <F2>)
(Para salir de esta ayuda: <F1>)

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
            base_dir=os.path.dirname(__file__),
            
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

