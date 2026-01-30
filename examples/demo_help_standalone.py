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

## Nuevas ampliaciones


Este documento está diseñado para validar, en orden incremental, las ampliaciones:
1) Links clicables (URLs, [texto](url), y saltos a headers por #slug)
2) Anclas HTML (<a id="etiqueta"></a>) y links a esas anclas (#etiqueta)
3) Comentarios HTML (<!-- ... -->) que NO deben renderizarse
4) Imágenes (![alt](ruta)) con carga desde disco

Sugerencia: prueba con una ventana suficientemente ancha y con scroll.
(Para forzar la visibilidad de elementos ocultos: <F2>)
(Para salir: <F1>)

---

## 1. Links clicables (web + internos a headers)

Objetivo: validar que se detectan links, se pintan como link y responden al click:
- `http(s)://...` abre el navegador
- `#...` hace scroll interno (a headers en esta fase; a anchors HTML en la fase 2)

### 1.1. Autolinks (URL “en crudo”)

1) Link simple:
https://www.pygame.org/docs/

2) Link con query:
https://www.google.com/preferences?hl=es

3) Link + fragmento:
https://docs.python.org/3/library/ast.html#ast.Lambda

4) Link + query + fragmento
https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map?utm_source=chatgpt#description

5) Link seguido de puntuación (el punto NO debería formar parte del link):
https://www.python.org.

6) Link entre paréntesis (el cierre ')' NO debería formar parte del link):
(https://www.python.org/)

7) Dos links en la misma línea:
https://www.python.org y también https://translate.google.com/

### 1.2. Links Markdown [texto](destino)

Estos deben ser clicables cuando implementes soporte de `[texto](destino)`:

- Link a web por Markdown:
[Web de Python](https://www.python.org/)

- Link con query + fragment por Markdown:
[Ejemplo con fragmento](http://example.com/test?param=1#anchor)

- Link interno a header (por slug):
[Ir a "2. Listas"](#2-listas)
[Ir a "3. Código"](#3-codigo)

Nota: si tu slugify elimina números/puntos y acentos, deberían funcionar también:
[Ir a "Código" (slug simple)](#codigo)
[Ir a "Listas" (slug simple)](#listas)

### 1.3. Links que NO deben activarse (casos negativos)

- Esto NO es un link: `https://www.python.org/` (dentro de inline code)
- Esto tampoco:
```text
https://www.python.org/  (dentro de bloque code)
```

---

## 2. HTML anchors (anclas explícitas) + links a #ancla

Objetivo: soportar anclas explícitas y saltar a ellas con `#id`.

A continuación hay anclas HTML. NO deben ocupar espacio visible (no deben renderizar texto).

<a id="ancla_inicio_seccion_2"></a>

Este texto está justo después de la ancla `ancla_inicio_seccion_2`.
Cuando esté implementado, este link debe saltar aquí:
[Ir a ancla_inicio_seccion_2](#ancla_inicio_seccion_2)

### 2.1. Ancla antes de un encabezado

<a id="ancla_pre_header"></a>
#### 2.1.1 Encabezado después de ancla

Este link debe saltar al punto marcado por `ancla_pre_header` (no al header):
[Ir a ancla_pre_header](#ancla_pre_header)

### 2.2. Ancla en medio del texto

Texto antes de ancla.

<a id="ancla_en_medio"></a>

Texto después de ancla. Este link debe saltar aquí:
[Ir a ancla_en_medio](#ancla_en_medio)

### 2.3. Caso negativo (ancla inexistente)

Este link NO debería romper nada (ideal: no hace nada):
[Ir a ancla_inexistente](#ancla_inexistente)

---

## 3. Comentarios HTML

Objetivo: ignorar comentarios HTML `<!-- ... -->`:
- No deben renderizarse
- Deben poder aparecer inline y en bloque
- No deben romper el resto del parseo

**La modalidad de comentario recomendada es la del comentario que ocupa completamente una línea.**
Con otros casos la prioridad ha sido que no afecten negativamente al funcionamiento del visualizador. 

### 3.1. Comentario inline de linea completa

 <!-- ESTE COMENTARIO DE LINEA COMPLETA NO DEBE VERSE -->

### 3.2. Comentario inline en medio de una linea

Este texto debe verse. <!-- ESTO NO SE CONSIDERA COMENTARIO POR ESTAR EN MEDIO DE UNA LINEA Y SE VERA COMO TEXTO --> Y este texto también debe verse.


### 3.3. Comentario en bloque (multilínea)

Aquí empieza un bloque de varias lineas de comentario que NO debe verse 
NOTA: En modo de visibilidad forzada con <F2> el comentario multilinea aparece en una sola linea con las partes separadas por ' || '):
<!--
Línea 1 oculta
Línea 2 oculta
- Viñeta oculta
## Encabezado oculto
-->

Aquí termina el bloque oculto. Este texto sí debe verse.

### 3.4. Comentarios cerca de sintaxis Markdown

- Viñeta visible A
<!-- ESTE COMENTARIO NO SE VERÁ Y NO ROMPERÁ LA LISTA -->
- Viñeta visible B

NOTA: En modo de visibilidad forzada con <F2> el comentario NO SE VISULIZARÁ. Solo garantizamos que no se rompa la listaa.
---

## 4. Imágenes

Objetivo: soportar imágenes Markdown:
- Bloque: `![alt](ruta)`
- Carga desde disco (rutas relativas y/o absolutas, según config)
- Si falta el fichero: no debe crashear (ideal: muestra placeholder o ignora)

### 4.1. Imagen con ruta relativa (ajusta al layout de tu repo)

Ejemplo (ruta RELATIVA):
![Cara](images/cara.jpg)

![Cara](images/cara.jpg)

![pez payaso con transparencia](images/pez1.png)

![DNA animation](images/batman_mini.png)

![DNA animation](images/batman_negative.png)

![DNA animation](images/batman.png)

![Vara](images/vara.jpg)

Si ese fichero no existe en tu repo, crea uno o cambia la ruta una sola vez,
y ya no tendrás que tocar este TEST_MD nunca más.

### 4.2. Imagen con ruta absoluta (opcional)

Ejemplo (ruta ABSOLUTA):
![Test absoluto](/tmp/help_core_test_image.png)

### 4.3. Imagen inexistente (caso negativo)

Esto NO debe bloquear ni romper el render:
![No existe](examples/assets/__no_existe__.png)


---

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

