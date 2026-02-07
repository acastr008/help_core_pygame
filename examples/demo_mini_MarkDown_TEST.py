#!/usr/bin/python3
from __future__ import annotations

# ===================================================================================================================
# Fecha última modificación: (31-ene-2026)  
# Nombre del archivo : demo_mini_MarkDown_TEST.py
# Descripción breve  : Chequea el soporte del lenguaje mini_MarkDown implementado en help_core_pygame 
# Autor              : Antonio Castro Snurmacher 
# Licencia de uso    : MIT 
# 
# Descripción extendida:
# ----------------------
#   El texto de la ayuda empieza mostrando la lista de las funcionalidades del lenguaje MarkDown implementadas y
#   pondrá a prueba de una forma bastante completa la implementación de cada una de dicha funcionalidades.
#   Tambien puede servir como referencia para resolver dudas de uso del lenguaje mini_MarkDown.
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

import os, sys
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


def FileCopy(origen, dir_destino):
    try:
        # Forzar que busque el archivo en la carpeta del script
        base_path = os.path.dirname(os.path.abspath(__file__))
        ruta_origen = os.path.join(base_path, origen)
        ruta_destino = os.path.join(dir_destino, os.path.basename(origen))

        with open(ruta_origen, 'rb') as f_src:
            with open(ruta_destino, 'wb') as f_dst:
                f_dst.write(f_src.read())
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


TEST_MD="""
# Estado de soporte MarkDown (implementado)

Este documento describe **únicamente** lo que el parser `_MiniMarkdown` implementa actualmente.
Empezamos mostrando cual es la situación actual del soporte de la gramática de nuestro lenguaje mini_MarkDown.
Observe que es un subconjunto del MarkDown estandar, con un nivel de funcionalidad muy interesante.

Sugerencia para la prueba: usar indent_per_level=2 y tab_size=4.

---

<a id="id_INDICE"></a>
# INDICE
- [1. Encabezados ATX](#id_Encabezados_ATX)
- [2. Párrafos](#id_Parrafos)
- [3. Énfasis](#id_Enfasis)
- [4. Código inline](#id_Codigo_inline)
- [5. Enlaces Markdown básicos](#id_Enlaces_MarkDown)
- [6. Link por URL](#id_link_URL)
- [7. Listas](#id_Listas)
- [8. Código](#id_BloquesCodigo_Fence)
- [9. Línea horizontal](#id_Linea_horizontal)
- [10. Comentarios HTML](#id_Comentarios_HTML)
- [11. Anclas HTML en línea completa](#id_Anclas_HTML)
- [12. Imágenes como bloques](#id_Imagenes_bloque)
- [13. Tablas](#id_tablas)
- [14. Resumen de funcionalidades de mini_MarkDown (de help_core_pygame)](#id_Resumen_mini_MarkDown)

---

<a id="id_Encabezados_ATX"></a>
## 1. Encabezados ATX (Esto es un encabezado H2)
### Esto es un encabezado H3.
#### Esto es un encabezado H4.
##### Esto es un encabezado H5.
###### Esto es un encabezado H6.

[Volver al índice](#id_INDICE)
---

<a id="id_Parrafos"></a>
## 2. Párrafos

Esta seción contiene tres párrafos:

Un párrafo es simplemente, una o más líneas de texto que no sean un bloque concreto detectado por el parser:
Es decir, algo que no sea: cabecera, listas, citas, hr, anclas, enlaces comentarios, etc.
Un párrafo se decide solo en el parseo de bloques.

**OJO:** La negrita/itálica se aplican después, cuando serenderiza el texto de todo un bloque.

Nuestro parser permite que un párrafo contenga saltos de línea internos.
Los saltos de linea continuos no rompen el párrafo salvo que sean una línea vacía

[Volver al índice](#id_INDICE)
---

<a id="id_Enfasis"></a>
## 3. Énfasis
Este documento prueba las marcas soportadas en este subconjunto de markdown soportado por help_core_pygame: 
- **Megrita**
- *Itálica*
- Mezcla ***negrita+itálica***

[Volver al índice](#id_INDICE)
---

<a id="id_Codigo_inline"></a>
## 4. Código inline
- El tipo de letra para `Código inline` también debería funcionar.
- **OJO:** Tenga en cuenta que **Si intenta usar `Código inline` dentro de negrita, la negrita se anulará.**

[Volver al índice](#id_INDICE)
---

<a id="id_Enlaces_MarkDown"></a>
## 5. Enlaces Markdown básicos

[Volver al índice](#id_INDICE)
---

<a id="id_link_URL"></a>
## 6. Link por URL

### Autolink por URL cruda

**Objetivo:** validar que se detectan links, se pintan como link y responden al click:

1. Link simple:
https://www.pygame.org/docs/

2. Link con query:
https://www.google.com/preferences?hl=es

3. Link + fragmento:
https://docs.python.org/3/library/ast.html#ast.Lambda

4. Link + query + fragmento
https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map?utm_source=chatgpt#description

5. Link seguido de puntuación (el punto NO debería formar parte del link):
https://www.python.org.

6. Link entre paréntesis (el cierre ')' NO debería formar parte del link):
(https://www.python.org/)

7. Dos links en la misma línea:
https://www.python.org y también https://translate.google.com/

### Links Markdown [texto](destino)

1. Link a web por Markdown:
[Web de Python](https://www.python.org/)

2. Link con query + fragment por Markdown:
[Ejemplo con fragmento](http://example.com/test?param=1#anchor)

3. Link interno a header (por slug):
[Ir a "7. Listas"](#7-listas)
[Ir a "8. Código"](#8-codigo)

Nota: si tu slugify elimina números/puntos y acentos, deberían funcionar también:
[Ir a "Código" (slug simple)](#codigo)
[Ir a "Listas" (slug simple)](#listas)

### Links que NO deben activarse (casos negativos)

- Esto NO es un link: `https://www.python.org/` (dentro de inline code)
- Esto tampoco:
```text
https://www.python.org/  (dentro de bloque code)
```

[Volver al índice](#id_INDICE)
---

<a id="id_Listas"></a>
## 7. Listas

**Objetivo:** Poner a prueba los distintos tipos de listas. (UL y OL)

#### 1. Viñetas (UL)

- Nivel 0, ítem A con una línea muy muy larga que debería envolver sin partir palabras, para comprobar el wrapping alrededor del ancho disponible en el rect del kernel. Repite varias palabras para forzar el salto y verificar que no se corta ninguna palabra en el proceso.
  - Nivel 1, ítem B (indentado con 2 espacios).
    - Nivel 2, ítem C. Contiene `inline code` y **negrita**.
      - Nivel 3, ítem D. Profundidad máxima recomendada.
        - Nivel 4, ítem E. Si max_list_nesting es 4, este debería "quedarse" al nivel permitido.

* Otra rama construida con asterisco como marcador.
  * Subnivel con asterisco.
    * Sub-subnivel.

#### 2. Numeradas (OL)

1. Ítem 1
2. Ítem 2 con una oración larga que debe partir por espacios y no cortar palabras. También contiene un enlace: http://example.com/test?param=1#anchor
3. Ítem 3
   1. Subítem 3.1
   2. Subítem 3.2 con *itálica* y `inline code`.
      1. Subítem 3.2.1 profundo
4. Ítem 4 empezando en número mayor (solo ver que se renderiza el índice literal).

[Volver al índice](#id_INDICE)
---

<a id="id_BloquesCodigo_Fence"></a>
## 8. Código

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

[Volver al índice](#id_INDICE)
---

<a id="id_Linea_horizontal"></a>
## 9. Línea horizontal
Justo abajo tenemos una, y un poco más arriba de esto tenemos otra,

[Volver al índice](#id_INDICE)
---

<a id="id_Comentarios_HTML"></a>
## 10. Comentarios HTML

**Objetivo:** ignorar comentarios HTML `<!-- ... -->`:

**La modalidad de comentario recomendada es la del comentario que ocupa completamente una línea.**
Con otros casos la prioridad ha sido que no afecten negativamente al funcionamiento del visualizador. 

### 1. Comentario inline de linea completa (Será ocultado, para verlo puede usar la tecla <F2>)

 <!-- ESTE COMENTARIO DE LINEA COMPLETA NO DEBE VERSE -->

### 2. Comentario inline en medio de una linea  

Este texto debe verse. <!-- ESTO NO SE CONSIDERA COMENTARIO POR ESTAR EN MEDIO DE UNA LINEA Y SE VERA COMO TEXTO --> Y este texto también debe verse.

### 3. Comentario en bloque (multilínea)

Aquí empieza un bloque de varias lineas de comentario que NO debe verse 
**NOTA:** En modo de visibilidad forzada con <F2> el comentario multilinea aparece en una sola linea con las partes separadas por ' || '):
<!--
Línea 1 oculta
Línea 2 oculta
- Viñeta oculta
## Encabezado oculto
-->

Aquí termina el bloque oculto. Este texto sí debe verse.

### 4. Comentarios cerca de sintaxis Markdown 
**NOTA:** Será ocultado, para ver el comentario **NO** podrá usar la tecla <F2>.

- Viñeta visible A
<!-- ESTE COMENTARIO NO SE VERÁ Y NO ROMPERÁ LA LISTA -->
- Viñeta visible B

**NOTA:** En modo de visibilidad forzada con <F2> el comentario NO SE VISULIZARÁ. Solo garantizamos que no se rompa la lista.
Podría no ser la mejor opción para poner un comentario.

[Volver al índice](#id_INDICE)
---

<a id="id_Anclas_HTML"></a>
## 11. Anclas HTML en línea completa 

**Objetivo:** Probar el soporte de anclas explícitas y comprobar los enlaces que saltan a ellas con `#id`.

A continuación hay anclas HTML. Por defecto son invisibles pero pulsando la tecla <F2> entramos en modo debug y se pueden visibilizar.

[Volver al índice](#id_INDICE)
---

<a id="id_Imagenes_bloque"></a>
## 12. Imágenes como bloques

**Objetivo:** soportar imágenes Markdown:
- Bloque: `![alt](ruta)`
- Carga desde disco (rutas relativas y/o absolutas, según config)
- Si falta el fichero: no debe romper la ejecución (ideal: muestra placeholder o ignora)

### 1. Imagen con ruta relativa (ajusta al layout de tu repo)

Ejemplo (ruta RELATIVA):

Ofrecemos una variedad de pruebas para verificar la visulización de diferentes tipos de ficheros y potenciales fallos de visualización.
**Pulse <F2>** para poder ver sobreimpreso con semitranparencia el texto alternativo con información de la imagen. 

![cara.jpg: 768x1024 (JPEG)](images/cara.jpg)

**NOTA:**
Las imágenes se tratan como bloques, y no podemos situar dos bloques a la misma altura.
Lo que podemos usar es el truco de simular varias imágenes usando una sola imagen con fondo transparente.

![caras.png: 81x800 (PNG con transparencia)](images/caras.png)

![pez1.png: 168x320 (PNG con transparencia)--(Pez payaso)](images/pez1.png)

![batman_mini.png: 307x307, (PNG)](images/batman_mini.png)

![batman_negative.png: 307x307 (PNG)](images/batman_negative.png)

![SuperStar.gif: 384x256 (GIF)](images/SuperStar.gif)

![DNA_animatio (GIF animado que no se visualizará animado)](images/DNA_animation.gif)


### 2. Imagen con ruta absoluta (opcional)

Ejemplo (ruta ABSOLUTA):
![Test ruta absoluta '/tmp/batman_mini.png'](/tmp/batman_mini.png)

### 3. Imagen inexistente (caso negativo)

Esto NO debe bloquear ni romper el render:

![fichero inexistente (images/xxxnada.jpg) ](images/nada.jpg)


[Volver al índice](#id_INDICE)
---

<a id="id_tablas"></a>
## 13. Tablas

Texto antes de tabla pegada (sin línea en blanco adicional). Debe cortar el párrafo y empezar la tabla como bloque.
| Col A | Col B |
|------:|:-----:|
|  123  | hola  |

### Alineación del cuerpo (la cabecera debe verse centrada siempre)
| Left | Center | Right |
|:-----|:------:|------:|
| a    | b      | c     |
| 11   | 22     | 33    |

### Fila con menos celdas (relleno con '@' dentro de celdas no definidas)
| A | B | C |
|---|---|---|
| 1 | 2 |
| x |

### Fila con más celdas (truncado + '@' a la derecha de la tabla)
| A | B |
|---|---|
| 1 | 2 | 3 | 4 |
| x | y | z |

### Caso negativo: cabecera + separador SIN filas (NO debe reconocerse como tabla)
| A | B |
|---|---|
Este bloque debe verse como párrafo normal, no como tabla.

[Volver al índice](#id_INDICE)
---

<a id="id_Resumen_mini_MarkDown"></a>
## 14. Resumen de funcionalidades de mini_MarkDown (de help_core_pygame).

### Bloques

- **Encabezados ATX (`#` … `######`)**  
  Genera tipos `h1` … `h6` con el campo `text`.

- **Línea horizontal**  
  La línea `---` genera el tipo `hr`.

- **Listas**
  - **Viñetas**: `- ` o `* `  ->  tipo `ul` con `items` (cada ítem incluye `level` y `text`).
  - **Numeradas**: `1. `  ->  tipo `ol` con `items` (cada ítem incluye `level`, `num` y `text`).
  - **Anidamiento por indentación**: calcula `level` según espacios (`indent_per_level_spaces`), limitado por `max_list_nesting`.

- **Bloques de código por “fence”**  
  Líneas con <code>```</code> abren/cierran un bloque  ->  tipo `code` con `text` (no detecta lenguaje).  
  Si el fence queda sin cerrar al final del fichero, también se emite un bloque `code`.

- **Párrafos**  
  En Markdown, un párrafo es simplemente, una o más líneas de texto que no sean algo concreto detectado por el parser:
  (cabecera, listas, citas, hr, anclas, enlaces comentarios, etc.). ->  tipo `p` con `text`.
  Un párrafo es simplemente, una o más líneas de texto que no sean un bloque concreto detectado por el parser:
  Es decir, algo que no sea: cabecera, listas, citas, hr, anclas, enlaces comentarios, etc.
  Un párrafo se decide solo en el parseo de bloques.
  La negrita/itálica se aplican después, cuando se renderiza el texto de todo un bloque
  Nuestro parser permite que un párrafo contenga saltos de línea internos.
  Los saltos de linea continuos no rompen el párrafo salvo que sean una línea vacía

- **Imágenes como bloques (línea completa)**  
  `![alt](src)`  ->  tipo `img` con `alt` y `src`.

- **Anclas HTML en línea completa**  
  `<a id="etiqueta"></a>`  ->  tipo `anchor` con `id`.

- **Comentarios HTML**
  - Una línea: `<!-- ... -->`  ->  tipo `comment` con `text`.
  - Multilínea: empieza con una línea `<!--` y termina en una línea `-->`   ->  tipo `comment` con `text`.
  - Dentro de listas se **ignoran** (no rompen la lista).

### Inline (tokenización dentro de texto)

La función `tokenize_inline()` genera “runs” con estos campos:  
`text`, `bold`, `italic`, `code`, `link`, `href`.

- **Código inline**: `` `code` ``  ->  `code=true`  
  El contenido queda protegido para que no se procese como énfasis ni links dentro del fragmento de código.

- **Énfasis**
  - `***texto***`  ->  negrita + itálica (`bold=true`, `italic=true`)
  - `**texto**`  ->  negrita (`bold=true`)
  - `*texto*`  ->  itálica (`italic=true`)

- **Enlaces Markdown básicos**  
  `[texto](destino)` (excluye imágenes `![...](...)`)  ->  `link=true`, `href=destino`, mostrando `texto`.

- **Autolink por URL cruda**  
  Detecta `http://...` o `https://...`  ->  `link=true`, `href=url`, mostrando la URL.  
  Recorta puntuación final típica (con una regla especial para `)`).

[Volver al índice](#id_INDICE)
---

Fin de la ayuda. (Pulse la tecla **<ESC>** para salir)



"""


def main() -> None:
    # Preparamos una copia de una imagen en "/tmp/"
    if not FileCopy("images/batman_mini.png", "/tmp/"):
        print("No se pudo copiar el fichero")
        sys.exit(2)

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
        asset_manager.close() # Liberamos recursos temporales (Importante si el paquete requiere extracción).
        try:
            pygame.quit()
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()

