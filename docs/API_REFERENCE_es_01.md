# API_REFERENCE_es — help_core_pygame

> Referencia unificada de la API del proyecto.
>
> Este documento se divide en dos partes:
> - **Parte I — API pública (usuario final)**: integración y uso del sistema de ayuda.
> - **Parte II — API de mantenimiento (desarrolladores)**: parser/render y módulos auxiliares.

⚠️ **Criterio de estabilidad**

- La **API pública** se considera estable y orientada al integrador.
- La **API de mantenimiento** puede cambiar con más frecuencia; se documenta para facilitar evolución y debugging.

## Requisitos y compatibilidad

- Python: **>= 3.9**
- Pygame: **>= 2.0**
- Versión del paquete (pyproject.toml): **0.1.2**

---
---

## Índice

- [Parte I — API pública (usuario final)](#part-001)
- [Parte II — API de mantenimiento (desarrolladores)](#part-002)
- [Anexo — Notas internas y decisiones](#annex-003)

---

<a id="part-001"></a>
## Parte I — API pública (usuario final)

Puntos de entrada y tipos necesarios para integrar y usar el sistema de ayuda (*standalone* u *overlay*) sin depender de los detalles internos.

---

<a id="mod-004"></a>
### API del módulo `help_core.py` (ES)

---

<a id="help_core-elem-001"></a>
#### [help_core-elem-001] Parte I — API pública (integración y uso)

> **Objetivo de la API pública:** permitir usar el sistema de ayuda sin conocer el parser ni los detalles
> internos del renderer.  
> Para más detalles de implementación, ver la **Parte II** y el código fuente.

<a id="help_core-elem-002"></a>
#### [help_core-elem-002] 1. `ShowHelpOverlay`

<a id="help_core-elem-003"></a>
##### [help_core-elem-003] Firma

```python
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
    ...
```

<a id="help_core-elem-004"></a>
##### [help_core-elem-004] Descripción

Muestra una ayuda en formato Markdown reducido como **overlay modal** sobre el `display` proporcionado.

- Es **modal/bloqueante**: detiene el loop del llamador mientras la ayuda está abierta.
- Usa `HelpViewer` internamente y delega en él el manejo de eventos y el render.
- Congela el frame de entrada (copia `display`) y lo restaura en cada iteración antes de dibujar el visor,
  de modo que el overlay se vea “encima” del estado congelado.

<a id="help_core-elem-005"></a>
##### [help_core-elem-005] Parámetros

- `display` (`pygame.Surface`): surface principal donde se dibujará el overlay.
- `md_text` (`str`): contenido Markdown reducido.
- `title` (`str`): título para la ayuda.
- `exit_keys` (`Tuple[int, ...]`): teclas que cierran la ayuda. Por defecto `ESC`.
- `fps` (`int`): límite de FPS del bucle modal.
- `kernel_bg` (`Tuple[int,int,int]`): color de fondo del área de ayuda.
- `wheel_step` (`int`): paso de scroll por rueda.
- `scroll_limit_cooldown_ms` (`int`): cooldown para el evento de “límite” de scroll (si el viewer lo usa).
- `base_dir` (`Optional[str]`): directorio base para resolver rutas relativas (p.ej. imágenes).

<a id="help_core-elem-006"></a>
##### [help_core-elem-006] Comportamiento y detalles relevantes

- Si `display` es `None`, lanza `ValueError`.
- Ajusta temporalmente el **autorepeat** del teclado con `pygame.key.set_repeat(250, 40)` para mejorar la navegación
  durante el modal, y lo restaura al salir.
- El bucle modal:
  - Procesa eventos (`pygame.event.get()`).
  - Sale con `QUIT` o si se pulsa una tecla en `exit_keys`.
  - Pasa el resto de eventos a `viewer.handle_event(event)`.
  - Restaura el frame congelado y dibuja `viewer.draw(display, rect)`.

<a id="help_core-elem-007"></a>
##### [help_core-elem-007] Ejemplo mínimo

```python
import pygame
from help_core_pygame.help_core import ShowHelpOverlay

pygame.init()
screen = pygame.display.set_mode((800, 480))

md = "# Ayuda\n\nPulsa ESC para salir.\n\n- Item 1\n- Item 2\n"

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_F1:
            ShowHelpOverlay(screen, md, title="Ayuda", exit_keys=(pygame.K_ESCAPE,))

    screen.fill((30, 30, 30))
    pygame.display.flip()

pygame.quit()
```

<a id="help_core-elem-008"></a>
##### [help_core-elem-008] Limitaciones

- El “salto” de tiempo al volver al loop principal (si tu juego usa `dt` acumulado) **no se corrige aquí**.
  Si lo necesitas, tu loop debe descartar o reajustar el primer `dt` tras cerrar la ayuda.

---

<a id="help_core-elem-009"></a>
#### [help_core-elem-009] 2. `open_help_standalone`

<a id="help_core-elem-010"></a>
##### [help_core-elem-010] Firma

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
    ...
```

<a id="help_core-elem-011"></a>
##### [help_core-elem-011] Descripción

Abre una ventana propia con el visor de ayuda.

Internamente:
1. Construye `HelpConfig(...)`
2. Ejecuta `HelpViewer(cfg).open_window()`

<a id="help_core-elem-012"></a>
##### [help_core-elem-012] Parámetros (nivel integrador)

- `md_text` (`str`): contenido Markdown reducido.
- `title` (`str`): título de ventana/ayuda.
- `size` (`(w,h)`): tamaño de la ventana.

**Opciones de estilo/fuentes (opcionales):**
- `style_json_path`, `style_variant`, `style_overrides`: soporte opcional de estilos.
- `fonts_dir`: directorio base para fuentes.
- `help_font_file`, `help_code_font_file`: archivos de fuente para texto normal y código.

**Opciones de indentación y scroll:**
- `indent_spaces_per_level`: sangría “lógica” por nivel (en espacios) para listas.
- `visual_indent_px`: sangría visual por nivel en píxeles.
- `wheel_step`: paso de scroll por rueda.
- `kernel_bg`: color de fondo del área de ayuda (si se especifica).
- `on_scroll_limit`: callback cuando se alcanza límite (“top”/“bottom” u otro convenio).
- `scroll_limit_cooldown_ms`: cooldown para no disparar continuamente el callback.

**Rutas:**
- `base_dir`: base para resolver rutas relativas (p.ej. imágenes).

<a id="help_core-elem-013"></a>
##### [help_core-elem-013] Ejemplo mínimo

```python
from help_core_pygame.help_core import open_help_standalone

md = "# Ayuda\n\nEsto es una ventana standalone.\n"
open_help_standalone(md, title="Ayuda", size=(900, 600))
```

---

<a id="help_core-elem-014"></a>
#### [help_core-elem-014] 3. Contrato mínimo de integración (standalone vs overlay)

- **Standalone:** tú llamas a `open_help_standalone(...)` y el visor gestiona su ventana.
- **Overlay modal:** tú llamas a `ShowHelpOverlay(...)` desde tu loop cuando quieras mostrar ayuda.
- **Overlay embebido/widget:** se recomienda usar directamente `HelpConfig` + `HelpViewer` (ver módulo del visor).
  Este patrón se documenta en el fichero de API del viewer.


---

---

<a id="mod-005"></a>
### API del módulo `help_viewer_impl.py` (ES)

---

<a id="help_viewer_impl-elem-001"></a>
#### [help_viewer_impl-elem-001] Parte I — API pública (integración y uso)

> **Objetivo de la API pública:** que un integrador pueda montar el visor en un rectángulo,
> pasarle eventos, dibujarlo y, opcionalmente, abrirlo en modo standalone.

<a id="help_viewer_impl-elem-002"></a>
#### [help_viewer_impl-elem-002] 1. `HelpConfig` (dataclass)

<a id="help_viewer_impl-elem-003"></a>
##### [help_viewer_impl-elem-003] Descripción

Contenedor de configuración para el visor.

- Es el lugar recomendado para definir:
  - Texto Markdown
  - Tamaño/título (standalone)
  - Parámetros de parseo (tab_size, nesting, indentación)
  - Parámetros de interacción (wheel_step, callback de límite)
  - Parámetros de estilo (JSON opcional, overrides, fuentes)

<a id="help_viewer_impl-elem-004"></a>
##### [help_viewer_impl-elem-004] Campos

```python
@dataclass
class HelpConfig:
    # Contenido
    md_text: str
    title: str = "Ayuda"
    size: Tuple[int, int] = (800, 480)

    # Rutas
    base_dir: Optional[str] = None

    # Parser / composición
    tab_size: int = 4
    max_list_nesting: int = 6
    indent_spaces_per_level: int = 2
    visual_indent_px: int = 24

    # Interacción
    wheel_step: int = 48
    on_scroll_limit: Optional[Callable[[str], None]] = None
    scroll_limit_cooldown_ms: int = 0

    # Estilos
    style_json_path: Optional[str] = None
    style_variant: Optional[str] = None
    style_overrides: Optional[Dict[str, Any]] = None

    # Fuentes (TTF opcionales)
    fonts_dir: Optional[str] = None
    help_font_file: Optional[str] = None
    help_code_font_file: Optional[str] = None

    # Fondo del panel (opcional)
    kernel_bg: Optional[RGB] = None
```

<a id="help_viewer_impl-elem-005"></a>
##### [help_viewer_impl-elem-005] Notas de uso

- `base_dir` es importante para resolver imágenes relativas en Markdown.
- `on_scroll_limit(where)` recibe `"top"` o `"bottom"` (convenio actual).
- `style_json_path` es opcional: si no existe, se usa `DEFAULT_STYLE`.
- `style_overrides` permite ajustar claves específicas sin JSON.


---

<a id="help_viewer_impl-elem-006"></a>
#### [help_viewer_impl-elem-006] 2. `HelpViewer`

<a id="help_viewer_impl-elem-007"></a>
##### [help_viewer_impl-elem-007] 2.1 Constructor

```python
class HelpViewer:
    def __init__(self, cfg: HelpConfig):
        ...
```

Crea el visor:
- Carga estilo (`DEFAULT_STYLE` + JSON opcional + overrides).
- Inicializa parser `_MiniMarkdown(...)` con parámetros de `cfg`.
- Inicializa caché de imágenes `ImageCache(cfg.base_dir)`.
- Normaliza y parsea el documento:
  - `normalized = parser.normalize(cfg.md_text)`
  - `self._blocks = parser.parse(normalized)`

> **Importante:** después de construir, el visor todavía no tiene layout hasta que se llame a `on_mount(rect)`.

---

<a id="help_viewer_impl-elem-008"></a>
##### [help_viewer_impl-elem-008] 2.2 Uso embebido (modo “widget”)

#### Ciclo de vida mínimo

1) Montar con un rectángulo absoluto:
```python
viewer.on_mount(rect)
```

2) En el loop principal, pasar eventos:
```python
viewer.handle_event(event)
```

3) En cada frame, dibujar:
```python
viewer.draw(screen, rect)
```

4) Al desmontar (cambio de escena, cierre, etc.):
```python
viewer.on_unmount()
```

#### Métodos públicos relevantes

```python
def on_mount(self, rect: pygame.Rect) -> None: ...
def on_unmount(self) -> None: ...
def handle_event(self, event: pygame.event.Event) -> bool: ...
def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None: ...
def update(self, dt_ms: int) -> None: ...
def wants_keyboard(self) -> bool: ...
def wants_wheel(self) -> bool: ...
```

- `handle_event(...)` devuelve `True` si consumió el evento.
- `update(...)` existe por compatibilidad, actualmente no hace nada (`pass`).
- `wants_keyboard()` y `wants_wheel()` devuelven `True` (interfaz tipo “widget”).

#### Eventos soportados (contrato práctico)

- `pygame.MOUSEWHEEL`: scroll vertical.
- `pygame.MOUSEBUTTONDOWN`:
  - click en link `http(s)://...` → abre navegador.
  - click en link `#anchor` → salto interno a ancla.
  - click y arrastre sobre el thumb de scrollbar → drag scroll.
- `pygame.MOUSEBUTTONUP`: suelta drag.
- `pygame.MOUSEMOTION`: actualiza drag si activo.
- `pygame.KEYDOWN`:
  - `F2`: alterna modo depuración (anclas e “ALT” de imágenes)
  - Navegación: `UP`, `DOWN`, `PAGEUP`, `PAGEDOWN`, `HOME`, `END`


---

<a id="help_viewer_impl-elem-009"></a>
##### [help_viewer_impl-elem-009] 2.3 Uso standalone

```python
def open_window(self) -> None:
    ...
```

- Inicializa pygame.
- Crea `display.set_mode(cfg.size)` y `caption(cfg.title)`.
- Monta `on_mount(screen.get_rect())`.
- Loop:
  - ESC o QUIT → salir
  - resto → `handle_event(e)`
  - `draw(screen, rect)` + `display.flip()`
- En `finally`:
  - `on_unmount()`
  - restaura `pygame.key.set_repeat(...)`
  - restaura visibilidad del ratón
  - `pygame.quit()`

**Cuándo usarlo:** si quieres un visor “auto-contenido” sin integrarlo en tu loop.

---

<a id="help_viewer_impl-elem-010"></a>
##### [help_viewer_impl-elem-010] 2.4 Adaptador opcional `as_interactive()`

```python
def as_interactive(self):
    ...
```

Devuelve un objeto adaptador con interfaz:

- `on_mount(rect)`
- `on_unmount()`
- `update(dt)`
- `draw(surface, rect)`
- `handle_event(event) -> bool`
- `wants_keyboard()`
- `wants_wheel()`

Útil si tu GUI/framework espera ese contrato y quieres enchufar `HelpViewer` sin acoplar dependencias.

---

<a id="help_viewer_impl-elem-011"></a>
#### [help_viewer_impl-elem-011] 3. Anclas y links

<a id="help_viewer_impl-elem-012"></a>
##### [help_viewer_impl-elem-012] 3.1 Anclas explícitas (HTML)
El parser puede producir bloques `{"type":"anchor","id":...}` desde `<a id="..."></a>`.
El viewer:
- las registra en `self._anchors[id] = y`
- permite saltar con links `#id` al hacer click.

<a id="help_viewer_impl-elem-013"></a>
##### [help_viewer_impl-elem-013] 3.2 Anclas automáticas por encabezados
En composición (`_compose_all`), para cada `h1..h6`:
- genera `slug = _slugify(texto)`
- registra `self._anchors[slug] = y`
- registra una variante “sin prefijo numérico” (p.ej. `2-3-...-titulo` → `titulo`)

<a id="help_viewer_impl-elem-014"></a>
##### [help_viewer_impl-elem-014] 3.3 Links http(s)
Si se hace click sobre una zona marcada como link y el `href` empieza por `http://` o `https://`,
se llama a `webbrowser.open(href)`.


---

<a id="help_viewer_impl-elem-015"></a>
#### [help_viewer_impl-elem-015] 4. Imágenes

- El parser emite `{"type":"img","alt":..., "src":...}`.
- En composición:
  - intenta cargar con `ImageCache.get_scaled(src, width)`
  - si existe: crea una línea `type="image"` con `surface` ya escalada
  - si falta: crea `type="image_missing"` con placeholder

En modo depuración (F2), se sobreimprime el `alt` como etiqueta sobre la imagen.


---

<a id="help_viewer_impl-elem-016"></a>
#### [help_viewer_impl-elem-016] 5. Tablas

- El parser emite bloques de tipo `table` (esquema definido por `md_tables`).
- En composición:
  - llama a `render_table(blk, body_font, header_font)`
  - almacena una `surface` de tabla para blit
  - si falla, dibuja un fallback `[Table render error]`


---

---

<a id="part-002"></a>
## Parte II — API de mantenimiento (desarrolladores)

Parser, render y módulos auxiliares (tablas, imágenes, estilo, etc.) necesarios para mantenimiento y evolución del proyecto.

---

### Dependencias entre módulos (import graph factual)

Esta sección describe **qué importa a qué** (nivel de módulo) según el código actual.

**Exportado por el paquete (`help_core_pygame/__init__.py`)**

- `HelpConfig`, `HelpViewer`, `open_help_standalone`, `ShowHelpOverlay`, `DEFAULT_STYLE`, `RGB`
- Nota: símbolos con prefijo `_` (por ejemplo `_MiniMarkdown`) **no** se exportan.

**Núcleo**

- `help_core.py`
  - usa `pygame`
  - importa internamente: `_MiniMarkdown` desde `help_mini_markdown.py`
  - importa internamente: `HelpViewer`, `HelpConfig`, `DEFAULT_STYLE`, `RGB` desde `help_viewer_impl.py`

- `help_viewer_impl.py`
  - usa `pygame`
  - importa internamente: `_MiniMarkdown` desde `help_mini_markdown.py`
  - importa internamente: `render_table` desde `table_renderer.py`
  - importa internamente: `ImageCache` desde `image_cache.py`

- `help_mini_markdown.py`
  - importa internamente: `is_table_start`, `parse_table` desde `md_tables.py`
  - nota: contiene un fallback de import absoluto (`from md_tables import ...`) pensado para ejecución directa/entornos especiales.

- `md_tables.py`
  - solo stdlib (`re`, `dataclasses`, `typing`)

- `table_renderer.py`
  - depende de `pygame`

- `image_cache.py`
  - depende de `pygame`, `pathlib`

**Demos (dependen de la API pública)**

- `demo_help_overlay_beep.py` → `HelpConfig`, `HelpViewer` (y `open_help_standalone` como alternativa)
- `demo_help_show_overlay_circles.py` → `ShowHelpOverlay`
- `demo_help_standalone.py` → `open_help_standalone`
- `demo_mini_MarkDown_TEST.py` → `open_help_standalone`

---

<a id="mod-006"></a>
### API del módulo `help_core.py` (ES)

---

<a id="help_core-elem-001"></a>
#### [help_core-elem-001] Parte II — API interna / de mantenimiento (relacionada con este módulo)

> Esta parte es para mantenimiento: comprensión del módulo, decisiones, y puntos de cambio seguros.
> No está pensada para integradores.

<a id="help_core-elem-002"></a>
#### [help_core-elem-002] 4. Papel de `help_core.py` en la arquitectura

Este módulo es una **fachada**: junta piezas del sistema y ofrece rutas rápidas:

- Construye `HelpConfig` con defaults razonables.
- Crea y usa `HelpViewer`.
- Implementa un loop modal (en overlay) con restauración del frame.

No debería contener lógica compleja de parseo/render: eso pertenece a módulos especializados.


---

<a id="help_core-elem-003"></a>
#### [help_core-elem-003] 5. Dependencias y símbolos importados

Este módulo depende de:

- Parser (Markdown reducido): `_MiniMarkdown` (importado de `help_mini_markdown`).
- Visor: `HelpViewer`, `HelpConfig` (importados de `help_viewer_impl`).
- Pygame: `pygame.Surface`, eventos, reloj, key repeat, etc.

**Nota de mantenimiento:** aunque `_MiniMarkdown` se importe aquí, este módulo no debería exponerlo como parte de la API
pública de integración. Su documentación completa debe vivir en el módulo del parser.


---

<a id="help_core-elem-004"></a>
#### [help_core-elem-004] 6. Detalles de implementación relevantes

<a id="help_core-elem-005"></a>
##### [help_core-elem-005] 6.1 Overlay modal y frame congelado

`ShowHelpOverlay` hace:

- `canvas = display.copy()` al entrar.
- En cada frame: `display.blit(canvas, (0, 0))` antes de dibujar el visor.

Esto evita artefactos y permite “ver” el estado congelado bajo la ayuda.

<a id="help_core-elem-006"></a>
##### [help_core-elem-006] 6.2 Gestión de autorepeat

Se guarda `pygame.key.get_repeat()` y se configura `pygame.key.set_repeat(250, 40)` durante el modal,
restaurando en `finally`.

**Motivo:** facilitar navegación por teclas dentro del visor sin depender del loop del juego.


<a id="help_core-elem-007"></a>
##### [help_core-elem-007] 6.3 Variante legacy de `ShowHelpOverlay` (comentada)

El fichero conserva una variante “legacy/backup” comentada.

- Se mantiene como referencia temporal.
- No debe considerarse API.
- Si se elimina, hacerlo en un commit separado para que sea trazable.


---

<a id="help_core-elem-008"></a>
#### [help_core-elem-008] 7. Testing manual (demos relacionadas)

Este módulo suele validarse indirectamente con demos:

- Standalone (abre ventana).
- Overlay modal (F1/F2/ESC según demo).
- Overlay embebido (si aplica).


---

<a id="help_core-elem-009"></a>
#### [help_core-elem-009] 8. Problemas conocidos / notas operativas

- “Salto de tiempo” al volver del modal (si el juego usa `dt`).
- Rutas relativas para imágenes: dependen de `base_dir` y del módulo de imágenes.


---

<a id="help_core-elem-010"></a>
#### [help_core-elem-010] 9. Historial y compatibilidad

- Licencia: MIT.
- Requisitos: Python 3.11+ y Pygame.


---

<a id="help_core-elem-011"></a>
#### [help_core-elem-011] 10. Changelog del documento

---

<a id="mod-007"></a>
### API del módulo `help_viewer_impl.py` (ES)

---

<a id="help_viewer_impl-elem-001"></a>
#### [help_viewer_impl-elem-001] Parte II — API interna / de mantenimiento

> Esta parte es para mantener el proyecto: estructura interna, helpers y decisiones.

<a id="help_viewer_impl-elem-002"></a>
#### [help_viewer_impl-elem-002] 6. Estilo (`DEFAULT_STYLE` y `_load_style`)

- `DEFAULT_STYLE` define tamaños, colores y espaciados (`hlp_*`).
- `_load_style(cfg)`:
  1) parte de `DEFAULT_STYLE`
  2) si existe `cfg.style_json_path`: carga JSON y aplica `variant` si procede
  3) aplica `cfg.style_overrides`
  4) normaliza colores list→tuple
  5) aplica “guardarraíles” y defaults (padding, wheel step, code pad, font scale, etc.)
  6) fija `hlp_CodeBlockMode` (`code_line` o `code_block`)


---

<a id="help_viewer_impl-elem-003"></a>
#### [help_viewer_impl-elem-003] 7. Composición y estructura de `_lines`

<a id="help_viewer_impl-elem-004"></a>
##### [help_viewer_impl-elem-004] 7.1 `self._blocks` (entrada)
Salida del parser (`_MiniMarkdown.parse`): lista de dicts por bloque.

<a id="help_viewer_impl-elem-005"></a>
##### [help_viewer_impl-elem-005] 7.2 `self._lines` (salida de composición)
Lista de dicts “renderizables”, con claves típicas:

- `y`, `h`: posición vertical en coordenadas de documento y altura de línea/bloque
- `runs`: lista de tuplas `(font_key, color, text, rx)` para blit de texto
- `clicks`: lista de rectángulos lógicos clicables `{x, w, href}`
- flags adicionales: `is_code`, `hr`, `type` (`image`, `table`, `anchor`, `comment`, etc.)
- campos específicos:
  - código: `code_bg`, `code_bg_indent`, `code_bg_width`, `code_block_indent`
  - imagen: `surface`, `alt`, `src`, `w`
  - tabla: `surface`, `w`

**Invariante útil:** `draw()` debe poder iterar `self._lines` sin asumir que todas tienen `runs` con contenido.


---

<a id="help_viewer_impl-elem-006"></a>
#### [help_viewer_impl-elem-006] 8. Render (`draw`) y scroll

- `draw(surface, rect)`:
  - `surface.fill(kernel_bg, rect)`
  - calcula paddings (vertical fijo, laterales dependientes de base font * scale)
  - clampa scroll según `visible_height`
  - recorre `_lines` en ventana visible y dibuja:
    - fondos de código (según `hlp_CodeBlockMode`)
    - imágenes / placeholders
    - tablas
    - hr
    - runs de texto
    - subrayado de links (usando `clicks`)
  - dibuja scrollbar si `content_height > rect.height`

- Scroll:
  - `_scroll` es coordenada de documento (px)
  - `max_scroll = content_height - visible_height`

---

<a id="help_viewer_impl-elem-007"></a>
#### [help_viewer_impl-elem-007] 9. Eventos (`handle_event`) y “scroll limit”
- Wheel y teclas aplican clamp.
- Si el scroll no cambia y ya estabas en el límite, llama `_notify_scroll_limit("top"/"bottom")`.
- `_notify_scroll_limit` aplica cooldown con `pygame.time.get_ticks()` si se configuró.

---

<a id="help_viewer_impl-elem-008"></a>
#### [help_viewer_impl-elem-008] 10. Helpers internos principales (inventario)

> Este inventario ayuda a mantenimiento, pero no es contrato público.

- `_notify_scroll_limit(where)`
- `_font_for(font_key)`
- `_hit_test_link(mouse_pos)`
- `_slugify(text)`
- `_jump_to_anchor(anchor_id)`
- `_compose_all()`
- `_compose_code_block_as_lines(...)`
- `_compose_code_block_as_box(...)`
- `_wrap_runs(...)`
- `_wrap_text_preserving_words(...)`
- `_split_preserving_spaces(...)`
- `_fit_text(...)`
- `_ensure_fonts()`
- `_font_key_for(role, bold, italic)`
- `_measure_text(s, font_key)`
- `_line_height_for(role)`
- `_space_px()`
- `_scrollbar_rect()`
- `_thumb_rect(track)`


---

<a id="help_viewer_impl-elem-009"></a>
#### [help_viewer_impl-elem-009] 11. Notas operativas y deuda técnica

- Hay código duplicado en el caso de `anchor` marker_h (dos asignaciones seguidas).
- Existe `_ensure_fonts_OLD` sin uso (candidato a eliminar en limpieza separada).
- `update(dt_ms)` está vacío pero forma parte de la interfaz.


---

<a id="help_viewer_impl-elem-010"></a>
#### [help_viewer_impl-elem-010] 12. Relación con otros documentos

- `docs/API_help_core.md`: entradas de alto nivel overlay/standalone.
- `docs/API_help_mini_markdown.md`: parser y tokenización inline.
- `docs/API_md_tables.md`, `docs/API_table_renderer.md`: tablas.
- `docs/API_image_cache.md`: imágenes.
- `docs/ARCHITECTURE_es.md`: visión general del sistema.

---

<a id="mod-008"></a>
### API del módulo `help_mini_markdown.py` (ES)

---

<a id="help_mini_markdown-elem-001"></a>
#### [help_mini_markdown-elem-001] Parte II — API interna / de mantenimiento

<a id="help_mini_markdown-elem-002"></a>
#### [help_mini_markdown-elem-002] 1. Clase `_MiniMarkdown`

<a id="help_mini_markdown-elem-003"></a>
##### [help_mini_markdown-elem-003] 1.1 Constructor

```python
class _MiniMarkdown:
    def __init__(
        self,
        tab_size: int = 4,
        max_list_nesting: int = 4,
        indent_per_level_spaces: int = 2,
    ):
        ...
```

#### Parámetros

- `tab_size`: número de espacios para expandir `\t` durante la normalización.
- `max_list_nesting`: profundidad máxima de anidamiento lógico para listas.
- `indent_per_level_spaces`: cuántos espacios equivalen a 1 nivel de lista **en parseo** (no en render).

#### Atributos relevantes (internos)

- `self.tab_size`
- `self.max_list_nesting`
- `self.spaces_per_level`

Además inicializa expresiones regulares para:
- bloques: hr, headers h1..h6, ul/ol, fences ``` y detección de imagen/anchor/comment
- inline: ***bold+italic***, **bold**, *italic*, `inline code`, URLs, links `[txt](url)`

---

<a id="help_mini_markdown-elem-004"></a>
#### [help_mini_markdown-elem-004] 2. `normalize(text)`

<a id="help_mini_markdown-elem-005"></a>
##### [help_mini_markdown-elem-005] Firma

```python
def normalize(self, text: str) -> str:
    ...
```

<a id="help_mini_markdown-elem-006"></a>
##### [help_mini_markdown-elem-006] Descripción

Normaliza saltos de línea y tabs:
- `\t` → espacios según `tab_size`
- `\r\n` y `\r` → `\n`

<a id="help_mini_markdown-elem-007"></a>
##### [help_mini_markdown-elem-007] Devuelve

`str`: texto normalizado.


---

<a id="help_mini_markdown-elem-008"></a>
#### [help_mini_markdown-elem-008] 3. `parse(text)`

<a id="help_mini_markdown-elem-009"></a>
##### [help_mini_markdown-elem-009] Firma

```python
def parse(self, text: str) -> List[Dict[str, Any]]:
    ...
```

<a id="help_mini_markdown-elem-010"></a>
##### [help_mini_markdown-elem-010] Descripción

Convierte un Markdown reducido en una **lista de bloques tipados** (dicts).  
El parser es “por líneas” y reconoce bloques en este orden (simplificado):

1. Vacías (se saltan entre bloques; dentro de fence se preservan)
2. Fences ``` (abre/cierra bloque de código)
3. Imagen como bloque: `![alt](src)` (línea completa)
4. Comentarios HTML:
   - en una línea: `<!-- ... -->`
   - multilínea: línea `<!--` y cierre en `-->`
5. Ancla HTML: `<a id="etiqueta"></a>`
6. Regla horizontal: `---`
7. Encabezados: `#`..`######`
8. Listas: ul (`-` o `*`) / ol (`1.`)
9. Tablas: detectadas por `md_tables.is_table_start` y parseadas por `md_tables.parse_table`
10. Párrafos: acumulación de líneas hasta encontrar un “corte” (otro bloque)

<a id="help_mini_markdown-elem-011"></a>
##### [help_mini_markdown-elem-011] Tipos de bloque emitidos (dict)

> **Importante:** este listado describe la estructura **tal y como se emite hoy**; si se cambian claves, hay que
> actualizar el visor y los tests.

#### 3.1 Párrafo

```python
{"type": "p", "text": "<texto>"}
```

- `text`: puede contener saltos de línea internos (join con `\n`).

#### 3.2 Encabezados

```python
{"type": "h1", "text": "..."}
{"type": "h2", "text": "..."}
...
{"type": "h6", "text": "..."}
```

#### 3.3 Regla horizontal

```python
{"type": "hr"}
```

#### 3.4 Código (fenced)

```python
{"type": "code", "text": "<contenido>"}
```

- Se preservan líneas vacías **dentro del fence**.
- Si el fence no se cierra antes de EOF, se emite igualmente un bloque `code`.

> Nota: en este parser se eliminó la regla antigua “4 espacios → bloque de código”.  

#### 3.5 Listas (`ul` / `ol`)

```python
{
  "type": "ul",
  "items": [{"level": 0, "text": "..."}, ...]
}
```

```python
{
  "type": "ol",
  "items": [{"level": 0, "num": 1, "text": "..."}, ...]
}
```

- `level`: nivel calculado como `indent_spaces // spaces_per_level`, con tope por `max_list_nesting - 1`.
- En `ol`, además:
  - `num`: número detectado (entero)

**Comentarios dentro de listas:**  
- Los comentarios HTML de línea completa y los bloques `<!-- ... -->` multilínea se ignoran dentro de listas sin romper la lista.

#### 3.6 Tabla (`table`)

El bloque exacto lo construye `parse_table(...)` del módulo `md_tables`.

- Se detecta antes de párrafos para que no sea absorbida como texto.
- **PENDIENTE DE:** documentar el esquema exacto del dict de tabla cuando se redacte `API_md_tables.md`.

#### 3.7 Imagen (`img`)

```python
{"type": "img", "alt": "<alt>", "src": "<src>"}
```

- Solo se detecta como bloque si la línea completa coincide con `![...](...)`.
- No se soporta inline (dentro de párrafos).
- No se soporta dentro de listas (se evita por diseño y por cómo se detecta).

#### 3.8 Comentario (`comment`)

```python
{"type": "comment", "text": "<texto>"}
```

- Comentario en una línea: el interior de `<!-- ... -->`.
- Comentario multilínea: se guarda el contenido entre `<!--` y `-->`.

> **Nota:** el viewer puede decidir ignorar estos nodos o usarlos como metadata.

#### 3.9 Ancla (`anchor`)

```python
{"type": "anchor", "id": "<etiqueta>"}
```

- Detecta `<a id="etiqueta"></a>` (con espacios tolerados alrededor).

---

<a id="help_mini_markdown-elem-012"></a>
#### [help_mini_markdown-elem-012] 4. `tokenize_inline(text)`

<a id="help_mini_markdown-elem-013"></a>
##### [help_mini_markdown-elem-013] Firma

```python
def tokenize_inline(self, text: str) -> List[Dict[str, Any]]:
    ...
```

<a id="help_mini_markdown-elem-014"></a>
##### [help_mini_markdown-elem-014] Descripción

Tokeniza un texto (normalmente el contenido de un `p`, `h*`, item de lista, etc.) en una lista de “runs”
para render: cada run es un dict con flags.

La tokenización sigue estas fases:

1. **Proteger inline code** (se separa por backticks y los segmentos `code` quedan fuera de procesamiento de énfasis y links)
2. Aplicar énfasis en texto normal:
   - `***texto***` → bold+italic (sin límites estrictos de palabra)
   - `**texto**` → bold (con límites de palabra para evitar falsos positivos tipo `precio*2`)
   - `*texto*` → italic (también con límites)
3. Expandir enlaces Markdown básicos `[texto](destino)` fuera de inline code  
   - Se excluyen imágenes `![...](...)` por regex negativa.
4. Autodetectar URLs `http://` / `https://` en texto normal (no en runs ya marcadas como link)
   - Recorta puntuación final típica (.,;:!?)]}"')  
   - Caso especial para `)` evitando recortar si el balance de paréntesis no “sobra”.

<a id="help_mini_markdown-elem-015"></a>
##### [help_mini_markdown-elem-015] Formato de salida (“run”)

Cada run tiene esta forma:

```python
{
  "text": "<texto>",
  "bold": bool,
  "italic": bool,
  "code": bool,
  "link": bool,
  "href": "<url o ''>"
}
```

<a id="help_mini_markdown-elem-016"></a>
##### [help_mini_markdown-elem-016] Reglas importantes

- Un run con `code=True` **no** se procesa para énfasis ni para links/URLs.
- Un run con `link=True` **no** se re-procesa para detectar URLs dentro (evita duplicar enlazado).
- Los links `[texto](destino)` generan:
  - run con `text=texto`, `link=True`, `href=destino`, `code=False`
- Las URLs crudas generan:
  - run con `text=url`, `link=True`, `href=url`, `code=False`
  - además se separa la puntuación final como run normal si fue recortada.


---

<a id="help_mini_markdown-elem-017"></a>
#### [help_mini_markdown-elem-017] 5. Detalles y decisiones de mantenimiento

<a id="help_mini_markdown-elem-018"></a>
##### [help_mini_markdown-elem-018] 5.1 Regex de énfasis y límites de palabra

- `***texto***` se detecta sin restricciones de palabra.
- `**texto**` y `*texto*` usan lookbehind/lookahead para exigir no estar “pegados” a caracteres de palabra.

Objetivo: evitar falsos positivos del estilo `precio*2`.

<a id="help_mini_markdown-elem-019"></a>
##### [help_mini_markdown-elem-019] 5.2 Código fence sin lenguaje

- Se detecta cualquier línea que empiece por ``` (regex: `^\s*```.*$`).
- No se detecta/almacena el “lenguaje”.


<a id="help_mini_markdown-elem-020"></a>
##### [help_mini_markdown-elem-020] 5.3 Doble bloque de cierre de fence al EOF (nota)

El código contiene una duplicación al final:

```python
if in_fence and fence_buf:
    out.append({"type": "code", "text": "\n".join(fence_buf)})

if in_fence and fence_buf:
    out.append({"type": "code", "text": "\n".join(fence_buf)})
```

- Esto podría emitir **dos** bloques `code` al EOF si un fence queda abierto.
- Si el comportamiento actual “no molesta” porque `in_fence` ya fue limpiado antes, igualmente merece revisión.


---

<a id="help_mini_markdown-elem-021"></a>
#### [help_mini_markdown-elem-021] 6. Interacción con tablas (`md_tables`)

- `parse` llama a `is_table_start(lines, i)` y, si es cierto, intenta `parse_table`.
- Si `parse_table` devuelve `None`, continúa con el parseo normal.


---

<a id="help_mini_markdown-elem-022"></a>
#### [help_mini_markdown-elem-022] 7. Relación con otros documentos

- `docs/API_help_core.md`: entrada de alto nivel para mostrar ayuda (overlay/standalone).
- `docs/API_help_viewer_impl.md`: render + eventos + scroll (pendiente).
- `docs/API_md_tables.md` / `docs/API_table_renderer.md`: tablas (pendiente).
- `docs/ARCHITECTURE_es.md`: visión global del sistema.

---

<a id="mod-009"></a>
### API del módulo `md_tables.py` (ES)

---

<a id="md_tables-elem-001"></a>
#### [md_tables-elem-001] Parte II — API interna / de mantenimiento

<a id="md_tables-elem-002"></a>
#### [md_tables-elem-002] 5. Constantes internas

```python
_ALIGN_LEFT = "left"
_ALIGN_CENTER = "center"
_ALIGN_RIGHT = "right"
```

Regex de celda separadora:

```python
_RE_SEPARATOR_CELL = re.compile(r"^\s*:?-{3,}:?\s*$")
```

---

<a id="md_tables-elem-003"></a>
#### [md_tables-elem-003] 6. `TableParseResult` (dataclass)

```python
@dataclass(frozen=True)
class TableParseResult:
    # Resultado del parseo de una tabla.
    #
    # Attributes:
    #   block: Diccionario con la estructura de tabla acordada.
    #   next_index: Índice de línea desde el que continuar el parseo global.
    block: Dict[str, Any]
    next_index: int
```

<a id="md_tables-elem-004"></a>
##### [md_tables-elem-004] Uso

`parse_table(...)` devuelve una instancia con:

- `block`: modelo de tabla normalizado
- `next_index`: índice para que el parseo global continúe desde ahí

---

<a id="md_tables-elem-005"></a>
#### [md_tables-elem-005] 7. `is_table_start(lines, index)`

<a id="md_tables-elem-006"></a>
##### [md_tables-elem-006] Firma

```python
def is_table_start(lines: Sequence[str], index: int) -> bool:
    # Indica si en `lines[index]` comienza un bloque de tabla válido.
    ...
```

<a id="md_tables-elem-007"></a>
##### [md_tables-elem-007] Reglas exactas (tal y como están implementadas)

- Requiere al menos 3 líneas disponibles: `index`, `index+1`, `index+2`.
- `header_cells = _parse_table_row(lines[index])`:
  - debe existir y tener `len >= 2`.
- `align = _parse_separator_row(lines[index + 1], expected_cols=len(header_cells))`:
  - debe existir y tener exactamente `expected_cols`.
- `first_row_cells = _parse_table_row(lines[index + 2])`:
  - debe existir y tener `len >= 2`.

Si todo se cumple: `True`; en caso contrario: `False`.

---

<a id="md_tables-elem-008"></a>
#### [md_tables-elem-008] 8. `parse_table(lines, index)`

<a id="md_tables-elem-009"></a>
##### [md_tables-elem-009] Firma

```python
def parse_table(lines: Sequence[str], index: int) -> Optional[TableParseResult]:
    # Parseo de un bloque de tabla a partir de `index`.
    ...
```

<a id="md_tables-elem-010"></a>
##### [md_tables-elem-010] Contrato del bloque devuelto

El diccionario `block` tiene este esquema **exacto**:

```python
{
  "type": "table",
  "header": [...],           # len = ncols
  "align":  [...],           # len = ncols (alineación cuerpo)
  "rows":   [[...], ...],    # cada fila normalizada a ncols
  "row_overflow": [bool, ...]
}
```

- `header`: lista de strings (celdas recortadas) de longitud `ncols`.
- `align`: lista de strings (`"left"|"center"|"right"`) de longitud `ncols`.
- `rows`: lista de filas, cada una lista de strings de longitud `ncols`.
- `row_overflow`: lista paralela a `rows`, con `True` si esa fila tenía más celdas que `ncols`.

<a id="md_tables-elem-011"></a>
##### [md_tables-elem-011] Reglas de parseo relevantes

- Si `is_table_start(...)` falla, devuelve `None`.
- Itera filas desde `i = index + 2` mientras:
  - la línea no sea vacía, y
  - `_parse_table_row(line)` devuelva al menos 2 celdas.
- Cada fila se normaliza con `_normalize_row(row_cells, ncols)`:
  - rellena con `"@"` si faltan celdas
  - trunca y marca overflow si sobran
- Requiere al menos 1 fila de datos (`rows` no vacía), si no devuelve `None`.
- `next_index` es el índice `i` donde paró el bucle (primera línea no perteneciente a la tabla).

---

<a id="md_tables-elem-012"></a>
#### [md_tables-elem-012] 9. Helpers internos

<a id="md_tables-elem-013"></a>
##### [md_tables-elem-013] 9.1 `_parse_table_row(line)`

```python
def _parse_table_row(line: str) -> Optional[List[str]]:
    # Convierte una línea con pipes en lista de celdas.
    ...
```

- Devuelve `None` si no hay `|` en la línea.
- Hace `strip()` de la línea y `split("|")`.
- Si hay pipe inicial o final, elimina el elemento vacío asociado.
- Recorta cada celda con `strip()`.
- Si quedan < 2 celdas, devuelve `None`.
- No soporta escapado de `|` dentro de celdas.

<a id="md_tables-elem-014"></a>
##### [md_tables-elem-014] 9.2 `_parse_separator_row(line, expected_cols)`

```python
def _parse_separator_row(line: str, expected_cols: int) -> Optional[List[str]]:
    # Parsea la fila separadora y produce la alineación por columna.
    ...
```

- Usa `_parse_table_row` para extraer celdas.
- Exige `len(cells) == expected_cols` (estricto).
- Cada celda debe cumplir `_RE_SEPARATOR_CELL`.
- Determina alineación por `:`:
  - `:...:` → center
  - `:...` → left
  - `...:` → right
  - `...` → left

<a id="md_tables-elem-015"></a>
##### [md_tables-elem-015] 9.3 `_normalize_row(row_cells, ncols)`

```python
def _normalize_row(row_cells: List[str], ncols: int) -> Tuple[List[str], bool]:
    # Normaliza una fila respecto al número de columnas de cabecera.
    ...
```

Reglas acordadas (exactas):

- Si `len(row_cells) < ncols`:
  - añade `"@"` hasta completar, `overflow=False`
- Si `len(row_cells) > ncols`:
  - trunca a `ncols`, `overflow=True`
- Si `len(row_cells) == ncols`:
  - devuelve tal cual, `overflow=False`

---

<a id="md_tables-elem-016"></a>
#### [md_tables-elem-016] 10. Notas de mantenimiento / decisiones

- **Detector estricto**: exige 2 columnas mínimo, separador válido y al menos 1 fila de datos.
  - Ventaja: menos falsos positivos.
  - Inconveniente: algunas tablas “flexibles” de Markdown no se reconocerán.
- **Sin escapado de `|`**: si se necesita a futuro, hay que introducir un parser de filas más sofisticado
  (y eso afecta a compatibilidad).
- **Marcador `"@"`**: es un convenio de normalización; el renderer debe documentar y respetar cómo lo representa.

---

<a id="md_tables-elem-017"></a>
#### [md_tables-elem-017] 11. Relación con otros módulos / docs

- `help_mini_markdown.py`: llama a `is_table_start` y `parse_table` dentro del parseo de bloques.
- `help_viewer_impl.py`: recibe bloques `type="table"` y los pasa al renderer.
- `table_renderer.py`: consume `block` y `row_overflow` para renderizar (incluyendo marcador `"@"`).

---

<a id="mod-010"></a>
### API del módulo `table_renderer.py` (ES)

---

<a id="table_renderer-elem-001"></a>
#### [table_renderer-elem-001] Parte II — API interna / de mantenimiento

<a id="table_renderer-elem-002"></a>
#### [table_renderer-elem-002] 5. Constantes internas

```python
HEADER_BG_COLOR = (50, 50, 180)
HEADER_FG_COLOR = (255, 255, 255)

BODY_BG_COLOR = (255, 255, 255)
BODY_FG_COLOR = (0, 0, 0)

GRID_COLOR = (0, 0, 0)

CELL_PAD_X = 8
CELL_PAD_Y = 4

BORDER_THICKNESS = 1
```

Alineaciones permitidas:

```python
_ALIGN_LEFT = "left"
_ALIGN_CENTER = "center"
_ALIGN_RIGHT = "right"
```

---

<a id="table_renderer-elem-003"></a>
#### [table_renderer-elem-003] 6. `TableRenderResult` (dataclass)

```python
@dataclass(frozen=True)
class TableRenderResult:
    \"\"\"Resultado del renderizado de una tabla.

    Attributes:
        surface: Superficie renderizada con la tabla completa.
        width: Ancho en píxeles.
        height: Alto en píxeles.
    \"\"\"
    surface: pygame.Surface
    width: int
    height: int
```

---

<a id="table_renderer-elem-004"></a>
#### [table_renderer-elem-004] 7. `render_table(table_block, body_font, header_font)`

<a id="table_renderer-elem-005"></a>
##### [table_renderer-elem-005] Firma

```python
def render_table(
    table_block: Dict[str, Any],
    body_font: pygame.font.Font,
    header_font: pygame.font.Font,
) -> TableRenderResult:
    ...
```

<a id="table_renderer-elem-006"></a>
##### [table_renderer-elem-006] Contrato del bloque de entrada (`table_block`)

Debe cumplir exactamente:

```python
{
  "type": "table",
  "header": ["Col A", "Col B", ...],      # len = ncols >= 2
  "align":  ["left|center|right", ...],   # len = ncols (solo cuerpo)
  "rows": [
    ["r1c1", "r1c2", ...],                # cada fila normalizada a ncols
    ...
  ],
  "row_overflow": [False, True, ...]      # len = len(rows)
}
```

<a id="table_renderer-elem-007"></a>
##### [table_renderer-elem-007] Comportamiento

1) Valida el bloque con `_validate_table_block`:
- Si falla, lanza `ValueError` con un mensaje específico.

2) Mide anchos por columna:
- usa `header_font.size(text)` para cabecera
- usa `body_font.size(text)` para filas

3) Calcula geometría:
- `col_width = max_text_width + 2*CELL_PAD_X`
- altura cabecera: `header_font.get_linesize() + 2*CELL_PAD_Y`
- altura fila: `body_font.get_linesize() + 2*CELL_PAD_Y`

4) Calcula gutter de overflow:
- Si existe cualquier `True` en `row_overflow`, crea gutter con:
  - `gutter_width = width("@") + 2*CELL_PAD_X`

5) Crea la `Surface`:
- `pygame.Surface((total_width, total_height), pygame.SRCALPHA)`
- Hace `surface.fill(BODY_BG_COLOR)`
- Dibuja cabecera con `surface.fill(HEADER_BG_COLOR, header_rect)`

6) Dibuja texto:
- Cabecera centrada (`_blit_text_centered`)
- Filas según `align` (`_blit_text_aligned`)
- Si overflow en la fila: dibuja `@` centrado en el gutter.

7) Dibuja rejilla y bordes encima (`_draw_grid`):
- Borde exterior de tabla (no incluye gutter)
- separadores horizontal bajo cabecera
- separadores horizontales entre filas
- separadores verticales entre columnas
- si hay gutter: línea separadora y rectángulo borde del gutter

<a id="table_renderer-elem-008"></a>
##### [table_renderer-elem-008] Devuelve

`TableRenderResult(surface=<Surface>, width=<int>, height=<int>)`

---

<a id="table_renderer-elem-009"></a>
#### [table_renderer-elem-009] 8. Helpers privados

<a id="table_renderer-elem-010"></a>
##### [table_renderer-elem-010] 8.1 `_validate_table_block(table_block)`

Valida:

- `type == "table"`
- `header` es lista con `len >= 2`
- `rows` es lista con `len >= 1`
- `align` es lista con `len == len(header)`
- `row_overflow` es lista con `len == len(rows)`
- Cada fila de `rows` es lista con `len == ncols`

Normaliza:
- `header_cells`: `str(x)` por celda
- `body_rows`: `str(x)` por celda
- `body_align`: valida valores, fallback a `"left"`
- `overflow_flags`: `bool(x)` por elemento

<a id="table_renderer-elem-011"></a>
##### [table_renderer-elem-011] 8.2 `_blit_text_centered(...)`

- Renderiza texto y lo centra dentro de la celda.

<a id="table_renderer-elem-012"></a>
##### [table_renderer-elem-012] 8.3 `_blit_text_aligned(...)`

- Centrado vertical simple.
- Horizontal:
  - center: `text_rect.centerx = cell_rect.centerx`
  - right: `text_rect.right = cell_rect.right - CELL_PAD_X`
  - left: `text_rect.left = cell_rect.left + CELL_PAD_X`

<a id="table_renderer-elem-013"></a>
##### [table_renderer-elem-013] 8.4 `_draw_grid(...)`

- Dibuja borde exterior y separadores.
- Si hay gutter, dibuja borde del gutter alineado con la tabla.

---

<a id="table_renderer-elem-014"></a>
#### [table_renderer-elem-014] 9. Notas de mantenimiento

- El estilo fijo está documentado como decisión explícita (“NO configurable por diseño”).
  Si se decide parametrizar estilos, lo más limpio sería:
  - introducir una estructura de estilo de tabla (dataclass/dict)
  - pasarla desde el viewer
  - mantener defaults actuales para compatibilidad visual

- No hay control de ancho máximo:
  - si se necesita, hay que introducir wrap/truncado o escalado (con cuidado de legibilidad).

---

<a id="table_renderer-elem-015"></a>
#### [table_renderer-elem-015] 10. Relación con otros módulos / docs

- `docs/API_md_tables.md`: define el esquema de `table_block` y el convenio `row_overflow`.
- `help_viewer_impl.py`: llama a `render_table(...)` y blitea `result.surface`.
- `docs/API_tables.md`: visión del subsistema de tablas (sintaxis, comportamiento global).

---

<a id="mod-011"></a>
### API del módulo `image_cache.py` (ES)

---

<a id="image_cache-elem-001"></a>
#### [image_cache-elem-001] Parte II — API interna / de mantenimiento

<a id="image_cache-elem-002"></a>
#### [image_cache-elem-002] 4. Tipos internos

<a id="image_cache-elem-003"></a>
##### [image_cache-elem-003] 4.1 `SurfaceInfo`

```python
SurfaceInfo = Tuple[pygame.Surface, int, int]
```

Representa:
- surface resultante (posiblemente escalada)
- `w`, `h`: tamaño final

<a id="image_cache-elem-004"></a>
##### [image_cache-elem-004] 4.2 `_ImageKey` (dataclass)

```python
@dataclass(frozen=True)
class _ImageKey:
    abs_path: str
    target_width: int
```

Se usa como clave de diccionario de caché.

---

<a id="image_cache-elem-005"></a>
#### [image_cache-elem-005] 5. Clase `ImageCache`

<a id="image_cache-elem-006"></a>
##### [image_cache-elem-006] 5.1 Constructor

```python
def __init__(self, base_dir: Optional[str] = None) -> None:
    ...
```

- `base_dir` se normaliza con `Path(base_dir).resolve()`.
- La caché se inicializa vacía: `Dict[_ImageKey, SurfaceInfo]`.

<a id="image_cache-elem-007"></a>
##### [image_cache-elem-007] 5.2 `set_base_dir(base_dir)`

```python
def set_base_dir(self, base_dir: Optional[str]) -> None:
    ...
```

Actualiza el `base_dir` (p.ej. si la configuración cambia).

> Nota de diseño: este método **no** invalida caché.
> - Si cambias `base_dir`, algunas rutas relativas podrían resolver a otro fichero.
> - Como la clave de caché es `abs_path` (resuelta) + `target_width`, en la práctica no hay colisión,
>   pero sí puede quedar basura de caché de rutas antiguas.


<a id="image_cache-elem-008"></a>
##### [image_cache-elem-008] 5.3 `resolve_src_to_abs_path(src)`

```python
def resolve_src_to_abs_path(self, src: str) -> Optional[Path]:
    ...
```

Resuelve un `src` a `Path` absoluto:

- `src` vacío/solo espacios → `None`
- si `Path(src).is_absolute()` → devuelve ese `Path`
- si `base_dir` es `None` y `src` es relativo → `None`
- si `base_dir` existe → `(base_dir / src).resolve()`

<a id="image_cache-elem-009"></a>
##### [image_cache-elem-009] 5.4 `get_scaled(src, target_width)`

```python
def get_scaled(self, src: str, target_width: int) -> Optional[SurfaceInfo]:
    ...
```

Flujo:

1. `abs_path = resolve_src_to_abs_path(src)`  
   si `None` → devuelve `None`

2. Construye `key = _ImageKey(str(abs_path), int(target_width))`  
   si existe en caché → devuelve cached

3. `loaded = _load_image(abs_path)`  
   si falla → `None`

4. `scaled = _scale_to_width(loaded, target_width)`  
   si falla → `None`

5. Guarda en caché y devuelve.

---

<a id="image_cache-elem-010"></a>
#### [image_cache-elem-010] 6. Métodos privados

<a id="image_cache-elem-011"></a>
##### [image_cache-elem-011] 6.1 `_load_image(abs_path)`

```python
def _load_image(self, abs_path: Path) -> Optional[pygame.Surface]:
    ...
```

- Si `abs_path` no existe → `None`
- Carga con `pygame.image.load(str(abs_path))`
- Intento de `convert()` / `convert_alpha()` **solo si hay display inicializado**:
  - `pygame.display.get_init()` y `pygame.display.get_surface() is not None`
  - Si hay alpha (`surface.get_alpha() is not None` o flags `SRCALPHA`) → `convert_alpha()`
  - En caso contrario → `convert()`
  - Captura `pygame.error` y continúa devolviendo surface sin convertir.

Motivación: `convert/convert_alpha` aceleran blits pero requieren display; si no hay display,
la surface sigue siendo usable.

<a id="image_cache-elem-012"></a>
##### [image_cache-elem-012] 6.2 `_scale_to_width(surface, target_width)`

```python
def _scale_to_width(self, surface: pygame.Surface, target_width: int) -> Optional[SurfaceInfo]:
    ...
```

- Obtiene tamaño original `src_w, src_h`
- Si tamaño inválido → `None`
- `max_w = max(1, int(target_width))`
- Si `src_w <= max_w`:
  - devuelve `(surface, src_w, src_h)` sin reescalar
- Si necesita escala:
  - `scale = max_w / src_w`
  - calcula `dst_w`, `dst_h` redondeando
  - intenta `pygame.transform.smoothscale(...)`
  - si falla, hace fallback a `pygame.transform.scale(...)`
  - devuelve `(scaled, dst_w, dst_h)`

Errores atrapados: `ValueError`, `pygame.error`.

---

<a id="image_cache-elem-013"></a>
#### [image_cache-elem-013] 7. Consideraciones de mantenimiento

<a id="image_cache-elem-014"></a>
##### [image_cache-elem-014] 7.1 Política de caché

- La caché se mantiene en memoria y crece con combinaciones `(abs_path, target_width)`.
- Si la aplicación cambia mucho el ancho objetivo (por resizes), puede crecer bastante.


<a id="image_cache-elem-015"></a>
##### [image_cache-elem-015] 7.2 Cambios mínimos recomendados

- Evitar cambiar el contrato `None` en fallo: es clave para que el viewer degrade con seguridad.
- Mantener la resolución de paths simple (y documentada).

---

<a id="image_cache-elem-016"></a>
#### [image_cache-elem-016] 8. Relación con otros documentos

- `docs/API_help_viewer_impl.md`: integración de imágenes (bloques `img`) y placeholders.
- `docs/API_help_mini_markdown.md`: sintaxis de imagen como bloque `![alt](src)`.
- `docs/ARCHITECTURE_es.md`: visión global del pipeline.

---

<a id="annex-003"></a>
## Anexo — Notas internas y decisiones

Listado de anotaciones internas que estaban embebidas en las APIs (tipo **PENDIENTE DE:**). Se agrupan aquí, indicando su **estado** y el **criterio** aplicado.

> Nota: el inventario de demos y escenarios de prueba se documenta en OVERVIEW (no en la referencia de API).

- 🟨 PENDIENTE — **help_core** — referencia: `help_core-elem-011`
  - Nota: documentar las dependencias exactas (import graph) cuando se consoliden nombres definitivos.
  - Criterio: Requiere decisión o verificación.
- ✅ RESUELTA — **help_core** — referencia: `help_core-elem-011`
  - Nota: acordar si se re-exporta o no `_MiniMarkdown` desde `__init__.py`.
  - Criterio: No se expone: el prefijo `_` indica API interna; se documenta como interno.
- 🟨 PENDIENTE — **help_core** — referencia: `help_core-elem-011`
  - Nota: validar si el viewer depende de autorepeat o si se puede limitar esta lógica al ejemplo.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_core** — referencia: `help_core-elem-011`
  - Nota: decidir fecha/criterio de eliminación.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_core** — referencia: `help_core-elem-011`
  - Nota: documentar convención de valores para `on_scroll_limit` (p.ej. `"top"`, `"bottom"`).
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_core** — referencia: `help_core-elem-011`
  - Nota: confirmar versiones objetivo actuales desde `pyproject.toml` y actualizar este apartado.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_core** — referencia: `help_core-elem-011`
  - Nota: integrar este fichero en un sistema de docs por módulos y concatenación hacia `docs/API_REFERENCE_es.md`.
  - Criterio: Requiere decisión o verificación.
- ✅ RESUELTA — **help_core** — referencia: `help_core-elem-014`
  - Nota: enlazar a `API_help_viewer_impl.md` cuando exista.
  - Criterio: El documento existe; se enlaza en la referencia.
- 🟨 PENDIENTE — **help_mini_markdown** — referencia: `help_mini_markdown-elem-022`
  - Nota: confirmar si el flujo principal (help_core / viewer) llama siempre a `normalize` antes de `parse`.
  - Criterio: Requiere decisión o verificación.
- ✅ RESUELTA — **help_mini_markdown** — referencia: `help_mini_markdown-elem-022`
  - Nota: documentar si esto fue una decisión definitiva (y si hay compat con indented code en algún punto).
  - Criterio: No se soporta (diseño minimalista); se usan fences ``` para bloques de código.
- 🟨 PENDIENTE — **help_mini_markdown** — referencia: `help_mini_markdown-elem-022`
  - Nota: fijar el comportamiento contractual del viewer con `type="comment"`.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_mini_markdown** — referencia: `help_mini_markdown-elem-022`
  - Nota: documentar cómo el viewer representa visualmente `link=True` (color, subrayado, click, etc.). (Es parte del viewer, no del parser.)
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_mini_markdown** — referencia: `help_mini_markdown-elem-022`
  - Nota: decidir si se añadirá soporte opcional de lenguaje (solo metadata) sin cambiar render.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_mini_markdown** — referencia: `help_mini_markdown-elem-022`
  - Nota: revisar si es un bug real o código muerto por flujo; si es bug, corregir con cambio mínimo y test.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_mini_markdown** — referencia: `help_mini_markdown-elem-022`
  - Nota: documentar condiciones exactas de `is_table_start` y el esquema del bloque devuelto por `parse_table` en el fichero `API_md_tables.md`.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_viewer_impl** — referencia: `help_viewer_impl-elem-010`
  - Nota: decidir qué claves son “estables” y cuáles “experimentales”.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_viewer_impl** — referencia: `help_viewer_impl-elem-010`
  - Nota: formalizar el esquema de `_lines` (tipo/clave) en una sección fija para mantenedores.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_viewer_impl** — referencia: `help_viewer_impl-elem-010`
  - Nota: limpiar duplicados/pequeñas inconsistencias detectadas (sin cambios funcionales).
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_viewer_impl** — referencia: `help_viewer_impl-elem-010`
  - Nota: registrar estos puntos en `TASKS.md` o tickets, y tratarlo con cambios mínimos y tests.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_viewer_impl** — referencia: `help_viewer_impl-elem-016`
  - Nota: documentar el conjunto de claves `hlp_*` consideradas estables (schema de estilo).
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_viewer_impl** — referencia: `help_viewer_impl-elem-016`
  - Nota: fijar “API de interacción” estable: teclas soportadas y comportamiento exacto (por ejemplo, step).
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_viewer_impl** — referencia: `help_viewer_impl-elem-016`
  - Nota: documentar política de seguridad / sandboxing (si aplica) y qué hacer en entornos sin navegador.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_viewer_impl** — referencia: `help_viewer_impl-elem-016`
  - Nota: definir contrato exacto del placeholder (texto, altura, colores) como parte de la API interna.
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **help_viewer_impl** — referencia: `help_viewer_impl-elem-016`
  - Nota: documentar el esquema del bloque tabla (ver `API_md_tables.md`).
  - Criterio: Requiere decisión o verificación.
- 🟨 PENDIENTE — **image_cache** — referencia: `image_cache-elem-016`
  - Nota: decidir si conviene ofrecer `clear()` para mantenimiento o debugging.
  - Criterio: Requiere decisión o verificación.
- ✅ RESUELTA — **image_cache** — referencia: `image_cache-elem-016`
  - Nota: evaluar límite de caché o política LRU si se hace necesario.
  - Criterio: No se implementa por ahora; se deja para cuando haya necesidad real (evidencia de consumo).
