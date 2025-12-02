# Guía de uso de `popup_gui.help_core`

Este documento describe **la API pública** del módulo `popup_gui/help_core.py` y cómo integrarlo en tus aplicaciones Pygame.

Está pensado para dos escenarios:

1. Uso **standalone** (ventana de ayuda independiente).
2. Uso **embebido** en tu propia ventana/bucle de juego (como en `cardumen.py`).

---

## 1. Visión general

`help_core.py` proporciona:

- Un pequeño **parser Markdown reducido** (`_MiniMarkdown`) – interno.
- Una **estructura de configuración**: `HelpConfig`.
- Un **visor de ayuda** con scroll y barra: `HelpViewer`.
- Un **helper de alto nivel** para modo ventana propia: `open_help_standalone`.

Características principales:

- Soporte de:
  - cabeceras (`# .. ######`),
  - listas ordenadas y no ordenadas,
  - bloques de código con fences ```,
  - texto en negrita, itálica y negrita+itálica (`*`, `**`, `***`),
  - código inline con comillas invertidas `` `...` ``,
  - enlaces “clicables” (simplemente se pintan distinto).
- Scroll con:
  - rueda del ratón,
  - teclas (↑, ↓, PageUp, PageDown, Home, End),
  - arrastre del “thumb” de la barra.
- Modo especial de **bloques de código**:
  - líneas sueltas (“rayas blancas”), o
  - caja blanca envolvente.
- **Callback opcional** cuando se intenta rebasar el límite superior/inferior de scroll (útil para meter un beep).
- **Cooldown** configurable entre notificaciones de límite de scroll (para no saturar con beeps).

---

## 2. Estructura del módulo

El módulo define, para uso externo:

- La dataclass **`HelpConfig`**.
- La clase pública **`HelpViewer`**.
- La función de alto nivel **`open_help_standalone`**.

También hay utilidades internas (parser, helpers de composición) que **no** están pensadas para uso directo.

Convención de import recomendada:

```python
from popup_gui.help_core import HelpConfig, HelpViewer, open_help_standalone
```

---

## 3. `HelpConfig`: configuración del visor de ayuda

```python
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

RGB = Tuple[int, int, int]

@dataclass
class HelpConfig:
    md_text: str
    title: str = "Ayuda"
    size: Tuple[int, int] = (800, 480)

    # Estilo / fuentes
    style_json_path: Optional[str] = None
    style_variant: Optional[str] = None
    style_overrides: Optional[Dict[str, Any]] = None
    fonts_dir: Optional[str] = None
    help_font_file: Optional[str] = None
    help_code_font_file: Optional[str] = None

    # Parser
    tab_size: int = 4
    max_list_nesting: int = 6
    indent_spaces_per_level: int = 2
    visual_indent_px: int = 24

    # Fondo
    kernel_bg: Optional[RGB] = None

    # Interacción
    wheel_step: int = 48
    on_scroll_limit: Optional[Callable[[str], None]] = None
    scroll_limit_cooldown_ms: int = 0
```

### 3.1 Campos obligatorios

- `md_text`:  
  Texto de ayuda en formato Markdown reducido.  
  Puede venir de un fichero `.md` leído con `open(...).read()`.

### 3.2 Campos importantes opcionales

- `title`:  
  Título de la ventana (modo standalone) o título lógico del visor.

- `size`:  
  Tamaño de la ventana para modo standalone, o tamaño “ideal” para el visor embebido.

- `wheel_step`:  
  Número de píxeles que avanza/retrasa el scroll con un “tick” de rueda.

- `on_scroll_limit`:  
  Callback opcional llamado cuando el usuario intenta seguir haciendo scroll por encima del límite:
  - `on_scroll_limit("top")` si intenta subir más allá del inicio.
  - `on_scroll_limit("bottom")` si intenta bajar más allá del final.

  Útil para reproducir un efecto de sonido o mostrar alguna indicación visual.

- `scroll_limit_cooldown_ms`:  
  Tiempo mínimo en milisegundos entre dos llamadas consecutivas a `on_scroll_limit`.  
  Ejemplo típico: `scroll_limit_cooldown_ms=300` (300 ms).

### 3.3 Estilo y fuentes (opcional)

- `style_json_path` / `style_variant`:  
  Permiten cargar un JSON de estilos externo (colores, tamaños de fuente, padding, etc.).  
  Si no se especifican, se usan valores por defecto embebidos en el módulo.

- `style_overrides`:  
  Diccionario para sobreescribir claves concretas del estilo cargado.  
  Ejemplo:

  ```python
  style_overrides = {
      "hlp_FontScale": 1.2,
      "hlp_KernelBg": (230, 230, 230),
  }
  ```

- `fonts_dir`, `help_font_file`, `help_code_font_file`:  
  Se pueden usar para forzar TTF concretos (texto normal y texto de código).

### 3.4 Parser y formato de listas

- `tab_size`:  
  Cuántos espacios equivale cada tabulador `\t` al normalizar el texto.

- `max_list_nesting`:  
  Profundidad máxima de listas (listas anidadas).

- `indent_spaces_per_level`:  
  Cuántos espacios de indentación indican un nivel de lista más.

- `visual_indent_px`:  
  Cuántos píxeles de desplazamiento horizontal se aplican por nivel de lista.

---

## 4. `HelpViewer`: visor de ayuda embebible

### 4.1 Creación

Lo normal es construirlo a partir de un `HelpConfig`:

```python
cfg = HelpConfig(
    md_text=texto_md,
    title="Ayuda del juego",
    size=(1200, 900),
    wheel_step=48,
    scroll_limit_cooldown_ms=300,
    on_scroll_limit=mi_callback_beep,
)

viewer = HelpViewer(cfg)
```

### 4.2 Ciclo de vida básico

Si quieres integrarlo en tu propia ventana (no standalone):

1. **Montaje** en un rectángulo:

   ```python
   rect = pygame.Rect(x, y, w, h)
   viewer.on_mount(rect)
   ```

   Esto:
   - prepara las fuentes,
   - compone el texto en líneas,
   - calcula `content_height`.

2. **Bucle de eventos**: delegar los eventos relevantes:

   ```python
   for event in pygame.event.get():
       # ...
       viewer.handle_event(event)
   ```

   El visor se encarga de:
   - teclado de scroll,
   - rueda,
   - clicks en la barra,
   - arrastre del “thumb”.

3. **Dibujo**:

   ```python
   viewer.draw(pantalla, rect)
   ```

   Se llama cada frame, después de limpiar o dibujar el fondo que tú quieras.

4. **Desmontaje** (opcional pero recomendable):

   ```python
   viewer.on_unmount()
   ```

   Por ejemplo, al cerrar la ayuda o cambiar de escena/estado.

> Importante: `HelpViewer` **no** llama a `pygame.display.flip()` ni a `pygame.event.get()`. Es responsabilidad del código que lo integra.

### 4.3 Interacción con scroll y eventos

`HelpViewer.handle_event(event)` trata:

- `MOUSEWHEEL`: scroll hacia arriba/abajo.
- `MOUSEBUTTONDOWN`/`MOUSEBUTTONUP`:
  - detección de click sobre el “thumb”,
  - activación/desactivación de arrastre.
- `MOUSEMOTION`:
  - si `_dragging` está activo, mueve el scroll en función de la posición vertical.
- `KEYDOWN`:
  - `K_UP`, `K_DOWN`,
  - `K_PAGEUP`, `K_PAGEDOWN`,
  - `K_HOME`, `K_END`.

En todos los casos, si el usuario intenta rebasar el extremo superior/inferior y `on_scroll_limit` está configurado, se llama al callback respetando el `scroll_limit_cooldown_ms`.

---

## 5. `open_help_standalone`: modo ventana propia

Para muchos usos, no es necesario montar el visor a mano. El helper `open_help_standalone` hace todo por ti.

### 5.1 Firma simplificada

```python
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
    ...
```

### 5.2 Comportamiento

- Llama internamente a `pygame.init()` y crea una ventana con el tamaño `size`.
- Configura:
  - visibilidad del ratón (siempre visible),
  - `pygame.key.set_repeat(250, 40)` para que las flechas repitan.
- Crea un `HelpConfig` con todos los parámetros recibidos.
- Instancia un `HelpViewer` y llama a `open_window()`, que:
  - hace un bucle propio de eventos,
  - sale cuando:
    - se pulsa `ESC`, o
    - se cierra la ventana (`QUIT`).
- En el `finally`:
  - restaura la visibilidad del ratón,
  - restaura `key.set_repeat` a su estado anterior,
  - llama a `pygame.quit()`.

### 5.3 Ejemplo completo de uso standalone

```python
import pygame
from popup_gui.help_core import open_help_standalone

def main() -> None:
    pygame.init()

    # Texto de ayuda en Markdown (podría venir de un .md)
    md_text = open("help.md", encoding="utf-8").read()

    # Sonido opcional para el límite de scroll
    try:
        beep_sound = pygame.mixer.Sound("mp3/beep_scroll.mp3")
    except pygame.error:
        beep_sound = None

    def beep_on_limit(where: str) -> None:
        if beep_sound is not None:
            beep_sound.play()

    open_help_standalone(
        md_text,
        title="Ayuda standalone",
        size=(1200, 900),
        wheel_step=48,
        kernel_bg=(222, 222, 222),
        on_scroll_limit=beep_on_limit,
        scroll_limit_cooldown_ms=300,
    )

if __name__ == "__main__":
    main()
```

---

## 6. Integración típica en un juego (visión rápida)

Resumen de los pasos típicos para integrar la ayuda en un juego como `cardumen`:

1. **Preparar el texto de ayuda**:
   - `help.md` con tu contenido en Markdown reducido.

2. **Cargar el texto al abrir la ayuda**:

   ```python
   md_text = open("help.md", encoding="utf-8").read()
   ```

3. **Crear el `HelpConfig` y el `HelpViewer`** (si no usas `open_help_standalone`):

   ```python
   cfg = HelpConfig(
       md_text=md_text,
       title="Ayuda del juego",
       size=pantalla.get_size(),
       wheel_step=48,
       on_scroll_limit=beep_on_limit,
       scroll_limit_cooldown_ms=300,
   )
   viewer = HelpViewer(cfg)
   rect = pantalla.get_rect()
   viewer.on_mount(rect)
   ```

4. **Dentro de un bucle modal de ayuda**:

   ```python
   running = True
   reloj = pygame.time.Clock()

   while running:
       dt = reloj.tick(60)
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               running = False
           elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_F1):
               running = False
           else:
               viewer.handle_event(event)

       pantalla.fill((0, 0, 0))
       viewer.draw(pantalla, rect)
       pygame.display.flip()

   viewer.on_unmount()
   ```

5. **Opcional**: ajustar visibilidad del ratón y volumen de música, como tú ya haces en `cardumen.py`.

---

## 7. Subconjunto de Markdown soportado

Para escribir `md_text` o `help.md`, ten en cuenta:

- **Encabezados**:

  ```markdown
  # Título 1
  ## Título 2
  ### Título 3
  ...
  ```

- **Listas no ordenadas**:

  ```markdown
  - Item nivel 0
    - Subitem nivel 1
  * Otra lista
  ```

- **Listas numeradas**:

  ```markdown
  1. Primero
  2. Segundo
     1. Sublista
  ```

- **Reglas horizontales**:

  ```markdown
  ---
  ```

- **Negrita, itálica, negrita+itálica**:

  ```markdown
  *itálica*
  **negrita**
  ***negrita e itálica***
  ```

- **Código inline**:

  ```markdown
  Usa la función `mi_funcion()` para...
  ```

- **Bloques de código**:

  ```markdown
  ```python
  def algo():
      print("Hola")
  ```
  ```

  (El idioma después de ``` no se usa para coloreado, pero se ignora sin error.)

---

## 8. Resumen rápido de la API pública

- **Dataclass** `HelpConfig`  
  Configura contenido, estilo, fuentes y comportamiento del scroll.

- **Clase** `HelpViewer`  
  Visor de ayuda:
  - `__init__(cfg: HelpConfig)`
  - `on_mount(rect: pygame.Rect) -> None`
  - `on_unmount() -> None`
  - `handle_event(event: pygame.event.Event) -> bool`
  - `draw(surface: pygame.Surface, rect: pygame.Rect) -> None`
  - `open_window() -> None` (modo ventana propia desde una instancia existente)

- **Función helper** `open_help_standalone(...) -> None`  
  Atajo para abrir una ventana de ayuda standalone, con su propio bucle de eventos.

Con estos elementos puedes:

- Integrar una ayuda desplazable y razonablemente rica en cualquier proyecto Pygame.
- Reutilizar el mismo módulo en distintos proyectos simplemente copiando `help_core.py` (o incluyéndolo como módulo compartido).
