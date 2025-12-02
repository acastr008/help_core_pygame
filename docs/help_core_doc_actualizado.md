# Documentación interna de `popup_gui/help_core.py`

## 1. Visión general del flujo

El visor de ayuda hace, a grandes rasgos, esto:

1. **Texto Markdown** (`md_text` en `HelpConfig`).
2. → **Parser `_MiniMarkdown`**: recorre el texto línea a línea y lo convierte en una lista de **bloques lógicos**:
   - párrafos,
   - cabeceras,
   - listas,
   - bloques de código (fenced con ```),
   - reglas horizontales.
3. → **Composición** (`_compose_all` y helpers): a partir de esos bloques, construye una lista de **líneas físicas**:
   - posición vertical lógica (`y`),
   - altura (`h`),
   - lista de “runs” de texto ya tokenizados (fuente, color, texto, x relativo),
   - metadatos de código (caja de fondo, indentación, etc.).
4. → **Dibujo** (`draw`):
   - calcula márgenes, zona visible y scroll,
   - recorta por `viewport_top`/`viewport_bottom`,
   - pinta fondos de código,
   - pinta texto renglón a renglón,
   - pinta barra de scroll y “thumb”.

Las estructuras clave son:

- `self._blocks`: lista de bloques lógicos (vista “documento”).
- `self._lines`: lista de líneas ya preparadas para dibujar (vista “pantalla”).

El scroll se basa en:

- `self._content_height`: altura lógica total del documento.
- `self._scroll`: desplazamiento vertical actual en píxeles.

---

## 2. Parser `_MiniMarkdown`

### 2.1 Configuración principal

El parser se crea desde `HelpViewer.__init__` con los parámetros de `HelpConfig`:

```python
self.parser = _MiniMarkdown(
    tab_size=cfg.tab_size,
    max_list_nesting=cfg.max_list_nesting,
    indent_per_level_spaces=cfg.indent_spaces_per_level,
)
```

Parámetros principales:

- `tab_size`: número de espacios por tabulador al normalizar.
- `max_list_nesting`: profundidad máxima de listas.
- `indent_per_level_spaces`: nº de espacios que cuentan como 1 nivel de indentación en listas.

La normalización (`normalize`) hace:

- sustituir `\t` por espacios (`tab_size`),
- normalizar saltos de línea a `\n`.

> Nota: `parse()` **no** llama a `normalize()` automáticamente; es el `HelpViewer` quien normaliza antes de parsear.

### 2.2 Bloques soportados

El método `parse(text: str) -> List[Dict[str, Any]]` genera una lista de bloques con un campo `type` y otros campos según el tipo:

- **Regla horizontal** (`---`):
  - Regex: `r"^\s*---\s*$"`.
  - Emite: `{"type": "hr"}`.

- **Encabezados H1..H6**:
  - Regex: `r"^(#{1,6})\s+(.*)$"`.
  - Emite: `{"type": "h1" | ... | "h6", "text": "..."}`.

- **Bloques de código “fenced”**:
  - Líneas con ``` para abrir y cerrar.
  - Emite: `{"type": "code", "text": "<contenido tal cual>"}`.
  - Si el EOF llega con fence abierto, emite el bloque igualmente.
  - La detección de *código indentado* por 4 espacios está desactivada en esta implementación para evitar confundir continuaciones de listas con código.

- **Listas no ordenadas (UL)**:
  - Regex: `r"^(\s*)([-*])\s+(.*)$"`.
  - Cada item añade:
    ```python
    {"level": L, "text": "..."}
    ```
  - El parser agrupa líneas consecutivas del mismo tipo de lista en un bloque:
    ```python
    {"type": "ul", "items": [ ... ]}
    ```

- **Listas numeradas (OL)**:
  - Regex: `r"^(\s*)(\d+)\.\s+(.*)$"`.
  - Cada item añade:
    ```python
    {"level": L, "num": N, "text": "..."}
    ```
  - Bloque:
    ```python
    {"type": "ol", "items": [ ... ]}
    ```

- **Párrafos (`p`)**:
  - Cualquier secuencia de líneas que no encaja en los casos anteriores.
  - Se separan por líneas en blanco (fuera de fences).
  - Emite:
    ```python
    {"type": "p", "text": "línea1\nlínea2\n..."}
    ```

Orden de detección esencial: fence → hr → heading → listas → párrafos.

### 2.3 Análisis inline (`tokenize_inline`)

Sobre el texto de párrafos, listas y cabeceras:

- **Código inline**: `` `texto` ``  
  → run con `code=True`, sin negrita ni itálica.

- **Énfasis**:

  ```text
  ***texto***  → negrita+itálica
  **texto**    → negrita
  *texto*      → itálica
  ```

  Se aplican en este orden: `***` → `**` → `*`.  
  El patrón de `***` no usa límites de palabra estrictos; `**` y `*` sí, para evitar falsos positivos tipo `precio*2`.

- **URLs**: `http://...` o `https://...`  
  → run con `link=True`, se pinta con color de enlace, salvo dentro de código inline.

Salida de `tokenize_inline`:

```python
{
    "text": str,
    "bold": bool,
    "italic": bool,
    "code": bool,
    "link": bool,
}
```

---

## 3. Estructura de bloques (`self._blocks`)

Ejemplos resumidos de bloques típicos:

```python
{"type": "p", "text": "Texto con\nsaltos manuales."}

{"type": "h2", "text": "Título de sección"}

{"type": "ul", "items": [
    {"level": 0, "text": "Item nivel 0"},
    {"level": 1, "text": "Item nivel 1"},
]}

{"type": "ol", "items": [
    {"level": 0, "num": 1, "text": "Primero"},
    {"level": 0, "num": 2, "text": "Segundo"},
]}

{"type": "code", "text": "línea1\nlínea2\n"}
```

`self._blocks` es una lista en orden de aparición, sin información de layout (no hay `y` ni alturas).

---

## 4. Composición: de bloques a líneas (`_compose_all`)

El método `_compose_all` convierte `self._blocks` en `self._lines`.

Pasos principales:

1. Calcula márgenes laterales:

   ```python
   base_size = float(self.style.get("hlp_BaseFontSize", 20))
   scale = float(self.style.get("hlp_FontScale", 1.0))
   base_unit = base_size * scale

   padding = int(self.style["hlp_Padding"])
   pad_left = int(self.style.get("hlp_PaddingLeft", 3.0 * base_unit))
   pad_right = int(self.style.get("hlp_PaddingRight", 5.0 * base_unit))

   width = max(0, self._w - (pad_left + pad_right))
   ```

   `width` es el ancho útil máximo para texto.

2. Recorre cada bloque y va incrementando una coordenada vertical lógica `y`.

3. Para **cabeceras** (`h1..h6`):
   - Se aplica espaciado superior/inferior configurable (`hlp_H?SpacingTop/Bottom`).
   - Se tokeniza inline y se llama a `_wrap_runs` con el rol de fuente `head_H?`.

4. Para **párrafos (`p`)**:
   - El texto del bloque puede contener `\n` explícitos; se tratan como “subpárrafos”.
   - Cada subpárrafo se tokeniza y se envuelve con `_wrap_runs`.
   - Entre subpárrafos se añade un pequeño espacio vertical, y entre bloques `p` se usa `hlp_ParaSpacing`.

5. Para **reglas horizontales (`hr`)**:
   - Se añade una entrada con bandera `hr=True` y altura de línea de párrafo.

6. Para **listas (`ul` / `ol`)**:
   - Se calcula la sangría por nivel a partir de `hlp_IndentPerLevelPx`.
   - Para `ul` se usan símbolos de viñeta (`•`, `º`, …) según el nivel.
   - Para `ol` se usa texto `"{num}. "`.
   - Se construye un run de prefijo (viñeta o número) y se pasa el resto del texto a `_wrap_runs` con `base_indent` desplazado.

7. Para **bloques de código (`code`)**:
   - El modo se controla con `hlp_CodeBlockMode`:
     - `"code_line"` → `_compose_code_block_as_lines`
     - `"code_block"` → `_compose_code_block_as_box`

Al final:

```python
self._content_height = max(0, y)
```

`self._lines` queda ordenada por `y` ascendente.

---

## 5. Bloques de código

### 5.1 Modo `"code_line"` → `_compose_code_block_as_lines`

Comportamiento clásico:

- Cada línea cruda del bloque se parte en renglones con `_wrap_text_preserving_words`.
- Cada renglón se convierte en una entrada de `self._lines` con:

```python
{
    "y": y,
    "h": h_code,
    "is_code": True,
    "runs": [("code", hlp_ColorCodeText, wline, codepad)],
    "code_rect": pygame.Rect(0, 0, width, h_code),
}
```

- Las líneas vacías de código generan entradas con `runs=[]` pero `is_code=True`, reservando altura.
- Después de procesar el bloque se suma el espaciado `para_sp`.

En dibujo (`draw`), en modo `"code_line"`:

- Cada línea con `is_code=True` y `code_rect` produce un rectángulo de fondo blanco que ocupa todo el ancho disponible.

### 5.2 Modo `"code_block"` → `_compose_code_block_as_box`

Modo “caja blanca envolvente”:

1. Divide `blk["text"]` en líneas crudas.
2. Calcula una unidad de tamaño `base_unit` a partir de `hlp_BaseFontSize` y `hlp_FontScale`.
3. Define márgenes internos del bloque de código:
   - `block_inset_left` y `block_inset_right` (en píxeles).
4. Calcula `inner_width = width - (block_inset_left + block_inset_right)`.
5. Recorre las líneas:
   - Para cada línea no vacía:
     - Envuelve con `_wrap_text_preserving_words(raw, inner_width, "code")`.
     - Mide el ancho de cada renglón para ajustar la anchura de la caja.
     - Construye entradas temporales con:
       ```python
       {
           "y": y,
           "h": h_code,
           "is_code": True,
           "runs": [("code", hlp_ColorCodeText, wline, codepad)],
           "code_block_indent": block_inset_left,
       }
       ```
   - Para líneas vacías:
     - Crea entradas con `is_code=True`, `runs=[]`, misma `code_block_indent`.
6. Calcula:
   - `block_top_y`, `block_bottom_y`, `block_height`.
   - `block_width` en función del texto más ancho, limitado por `inner_width` y por un mínimo razonable.
7. Crea una entrada “fondo de bloque”:

```python
self._lines.append(
    {
        "y": block_top_y,
        "h": block_height,
        "code_bg": True,
        "code_bg_indent": block_inset_left,
        "code_bg_width": int(block_width),
        "runs": [],
    }
)
```

8. Añade todas las líneas temporales al `self._lines`, copiando `code_bg_width`.

En dibujo, en modo `"code_block"`:

- Las entradas con `code_bg=True` generan una caja blanca con borde redondeado.
- Las líneas con `is_code=True` se pintan con `code_block_indent` para alinear dentro de la caja.

---

## 6. Wrapping de texto (`_wrap_runs` y `_wrap_text_preserving_words`)

### 6.1 `_wrap_runs`

Se usa para párrafos, listas y cabeceras.

Entrada:

- `runs`: lista de runs de `tokenize_inline`.
- `width`: ancho máximo en píxeles.
- `font_role`: rol lógico de fuente (`"para"`, `"head_H2"`, etc.).
- `color`: color base.
- `base_indent`: sangría inicial.
- `prefix`: (opcional) texto de prefijo para listas (viñetas o números).

Salida:

- `lines`: lista de diccionarios, cada uno con:
  ```python
  {"h": altura, "runs": [(font_key, color, texto, x_rel), ...]}
  ```
- `total_h`: altura total sumada.

La función:

- Convierte los runs lógicos en tokens `(texto, font_key, color)`.
- Divide cada texto en sub-tokens preservando espacios (`_split_preserving_spaces`).
- Encaja cada token en la línea actual midiendo el ancho con `_measure_text`.
- Si no cabe:
  - Cierra la línea y comienza otra,
  - o fragmenta el token con `_fit_text` si es más ancho que el propio `width`.

> Importante: `_wrap_runs` nunca pierde texto; sólo lo divide entre renglones.

### 6.2 `_wrap_text_preserving_words`

Diseñada para código:

- Recibe una sola línea (`text`), un `max_width` y un `font_role`.
- Si `max_width <= 0` devuelve el texto en un solo elemento.
- Separa en tokens espacios/no-espacios con:
  ```python
  tokens = re.findall(r"\s+|\S+", text)
  ```
- Construye `lines` acumulando tokens mientras el ancho cabe.
- La primera pieza de una línea se acepta aunque se desborde, para no perder indentación en código.
- Si un token no cabe:
  - cierra la línea actual,
  - empieza una nueva con ese token.

Resultado:

```python
List[str]  # cada elemento es un renglón listo para pintarse con fuente "code"
```

---

## 7. Estructura de `self._lines`

Piensa en `self._lines` como “lista de renglones físicos” del documento.

### 7.1 Campos básicos

Cada entrada tiene siempre:

- `y`: coordenada vertical lógica dentro del contenido (0 en la primera línea).
- `h`: altura de la línea en píxeles.
- `runs`: lista de tuplas:

  ```python
  (font_key: str, color: RGB, text: str, rx: int)
  ```

Ejemplo de línea de párrafo:

```python
{
    "y": 240,
    "h": 22,
    "runs": [
        ("para", (20, 20, 24), "Texto de ejemplo envuelto.", 0),
    ],
}
```

### 7.2 Campos adicionales

Según el tipo de línea:

- Código (modo `"code_line"`):
  - `is_code: True`
  - `code_rect: pygame.Rect`

- Código (modo `"code_block"`):
  - línea de fondo:
    - `code_bg: True`
    - `code_bg_indent`, `code_bg_width`
  - línea de texto:
    - `is_code: True`
    - `code_block_indent`
    - `code_bg_width`

- Regla horizontal:
  - `hr: True`

Las líneas se añaden a `self._lines` en orden; la última entrada corresponde al final lógico del documento.

---

## 8. Dibujo (`draw`)

Firma:

```python
def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
```

Responsabilidades:

1. Rellenar el fondo del panel de ayuda (`kernel_bg`).
2. Calcular márgenes, ancho útil (`max_w`) y `visible_height`.
3. Ajustar `self._scroll` para que no se salga de `[0, max_scroll]`.
4. Calcular el “viewport”:

   ```python
   viewport_top = self._scroll
   viewport_bottom = self._scroll + visible_height
   ```

5. Determinar el modo de código:

   ```python
   code_mode = str(self.style.get("hlp_CodeBlockMode", "code_block")).lower()
   ```

6. Recorrer `self._lines`:
   - Si una línea cae fuera de `[viewport_top, viewport_bottom]`, se omite.
   - Para líneas de código:
     - En modo `"code_line"`: fondo por línea (ancho completo).
     - En modo `"code_block"`: fondo sólo en entradas `code_bg=True`.
   - Para `hr=True`: línea horizontal.
   - Para texto: pintar cada run con la fuente adecuada (`_font_for`).

7. Dibujar la barra de scroll si `self._content_height > rect.height`:
   - `track = _scrollbar_rect()`
   - `thumb = _thumb_rect(track)`
   - Se dibujan ambos rectángulos.

---

## 9. Scroll, barra y eventos

### 9.1 Coordenadas de scroll

- `self._content_height`: calculado en `_compose_all`.
- `self._scroll`: desplazamiento actual.
- El rango válido es `[0, max_scroll]`, donde:
  ```python
  max_scroll = max(0, self._content_height - visible_height)
  ```

### 9.2 Barra de scroll

- `_scrollbar_rect()`:
  - Devuelve el rectángulo del “track” a la derecha del `rect` principal, respetando `hlp_Padding`.
- `_thumb_rect(track)`:
  - Calcula la altura proporcional del “thumb” según `view_h / content_h`.
  - Posiciona el thumb según `self._scroll / max_scroll`.

### 9.3 Gestión de eventos (`handle_event`)

Firma:

```python
def handle_event(self, event: pygame.event.Event) -> bool:
```

Eventos soportados:

- **Rueda del ratón (`MOUSEWHEEL`)**:
  - Usa `hlp_WheelStep` como paso base.
  - Actualiza `self._scroll` hacia arriba/abajo.
  - Si tras aplicar el límite `self._scroll` no cambia y ya está en el tope, se considera intento de rebasar y se notifica el límite (ver 9.4).

- **Click en el thumb y arrastre (`MOUSEBUTTONDOWN` / `MOUSEMOTION` / `MOUSEBUTTONUP`)**:
  - `MOUSEBUTTONDOWN`:
    - Si el click cae dentro del thumb, activa `_dragging` y guarda:
      - `self._drag_start_y` (posición inicial del ratón),
      - `self._scroll_start` (scroll inicial).
  - `MOUSEMOTION` con `_dragging=True`:
    - Ajusta `self._scroll` en función del desplazamiento vertical dentro del “track”.
    - Si el ratón intenta arrastrar más allá del inicio o fin **y** ya estábamos en el límite, se notifica el límite.
  - `MOUSEBUTTONUP`:
    - Desactiva `_dragging`.

- **Teclado (`KEYDOWN`)**:
  - Flechas ↑/↓: paso de media rueda (`step // 2`).
  - PageUp/PageDown: saltos de una “pantalla” (`self._h`) menos un pequeño margen.
  - Home/End: salto al principio o final.
  - Si la tecla no cambia `self._scroll` porque ya estamos en el límite, se notifica el límite.

El método devuelve `True` si el evento ha sido consumido por el visor; `False` en caso contrario.

---

## 10. Notificación de límite de scroll y cooldown

### 10.1 Campos en `HelpConfig`

```python
@dataclass
class HelpConfig:
    ...
    # Interacción
    wheel_step: int = 48
    # Callback opcional para notificar límite de scroll ("top" / "bottom").
    on_scroll_limit: Optional[Callable[[str], None]] = None
    # Tiempo mínimo entre notificaciones consecutivas (ms). 0 = sin límite.
    scroll_limit_cooldown_ms: int = 0
```

- `on_scroll_limit(where: str)`:
  - `where` es `"top"` o `"bottom"`.
- `scroll_limit_cooldown_ms`:
  - si es `> 0`, limita la frecuencia de llamadas a `on_scroll_limit`.

### 10.2 Implementación interna (`_notify_scroll_limit`)

`HelpViewer` mantiene `self._last_scroll_limit_ms` y expone:

```python
def _notify_scroll_limit(self, where: str) -> None:
    if self.cfg.on_scroll_limit is None:
        return

    cooldown_ms = self.cfg.scroll_limit_cooldown_ms
    if cooldown_ms <= 0:
        self.cfg.on_scroll_limit(where)
        return

    now_ms: int = pygame.time.get_ticks()
    if self._last_scroll_limit_ms > 0:
        elapsed = now_ms - self._last_scroll_limit_ms
        if elapsed < cooldown_ms:
            return

    self._last_scroll_limit_ms = now_ms
    self.cfg.on_scroll_limit(where)
```

`handle_event` llama a `_notify_scroll_limit(where)` en los casos de:

- rueda (`MOUSEWHEEL`),
- arrastre del thumb (`MOUSEMOTION` con `_dragging=True`),
- teclado (`KEYDOWN`),

cuando se detecta intento de rebasar el límite superior o inferior.

Esto permite implementar, por ejemplo, un beep de scroll en los límites, espaciado cada 300 ms.

---

## 11. Modo standalone y helper `open_help_standalone`

### 11.1 `HelpViewer.open_window`

Método para abrir una ventana propia de Pygame y mostrar la ayuda sin integrarla en otra GUI:

- Inicializa Pygame y crea la ventana con el tamaño de `HelpConfig.size`.
- Guarda el estado previo:
  - visibilidad del ratón,
  - configuración de `key.set_repeat`.
- Fuerza:
  - `pygame.mouse.set_visible(True)` para ver el cursor,
  - `pygame.key.set_repeat(250, 40)` para tener autorepeat en las teclas.
- Monta el visor (`on_mount(rect)` con todo el `screen.get_rect()`).
- Bucle principal:
  - procesa eventos (ESC / QUIT cierran),
  - llama a `handle_event`,
  - repinta con `draw`.
- En el `finally`:
  - llama a `on_unmount()`,
  - restaura `key.set_repeat` a su estado anterior,
  - restaura la visibilidad del ratón,
  - hace `pygame.quit()`.

### 11.2 Helper `open_help_standalone`

Función de conveniencia al final del módulo:

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

- Construye un `HelpConfig` con los parámetros proporcionados.
- Configura:
  - parser (indentación y niveles de lista),
  - estilo (JSON, overrides, fuentes),
  - interacción (`wheel_step`, `on_scroll_limit`, `scroll_limit_cooldown_ms`),
  - color de fondo (`kernel_bg`).
- Instancia un `HelpViewer` y llama a `open_window()`.

Ejemplo de uso típico (como en la demo):

```python
import pygame
from help_core import open_help_standalone

def main() -> None:
    pygame.init()
    beep_sound = pygame.mixer.Sound("mp3/beep_scroll.mp3")

    def beep_on_limit(where: str) -> None:
        beep_sound.play()

    open_help_standalone(
        TEST_MD,
        title="Demo Help Standalone",
        size=(1200, 900),
        indent_spaces_per_level=2,
        visual_indent_px=24,
        wheel_step=48,
        kernel_bg=(222, 222, 222),
        on_scroll_limit=beep_on_limit,
        scroll_limit_cooldown_ms=300,
    )
```

Con esto, tanto la demo como otros proyectos que usen `help_core.py` pueden aprovechar:

- parser Markdown reducido,
- layout con bloques y líneas,
- scroll con rueda, teclado y arrastre del thumb,
- caja de código en modo línea o bloque,
- notificación de límites de scroll con antirrebote configurable,
- modo standalone listo para usar.
