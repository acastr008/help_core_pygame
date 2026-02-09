# API_REFERENCE_en — help_core_pygame

> 🔙 Return to index: [INDEX_en.md](INDEX_es.md)

> Unified API reference for the project.
>
> This document is split into two parts:
> - **Part I — Public API (end users)**: integrating and using the help system.
> - **Part II — Maintenance API (developers)**: parser/renderer and auxiliary modules.

⚠️ **Stability criteria for both parts of the API**

- The **Public API** is the more stable, simpler part, aimed at end users. It is the recommended surface
  to integrate a help system into a Pygame game.
- The **Maintenance API** is wider and may change more frequently; it is documented to support maintenance,
  debugging, and future evolution of the project.

![Public API vs Maintenance API](APIs_pubica_vs_mantenim.png)

## Requirements and compatibility

- Python: **>= 3.9**
- Pygame: **>= 2.0**
- Package version (pyproject.toml): **0.1.2**

---

## Table of contents
- [Part I — Public API (end users)](#parte-i-api-p-blica-usuario-final)
  - [API for module help_core.py](#api-del-m-dulo-help-core-py-es)
    - [Part I — Public API (integration and usage)](#help_core.parte-i-api-p-blica-integraci-n-y-uso)
    - [1. ShowHelpOverlay](#help_core.ShowHelpOverlay)
      - [Signature](#help_core.firma)
      - [Description](#help_core.descripci-n)
      - [Parameters](#help_core.par-metros)
      - [Behavior and relevant details](#help_core.comportamiento-y-detalles-relevantes)
      - [Minimal example](#help_core.ejemplo-m-nimo)
      - [Limitations](#help_core.limitaciones)
    - [2. open_help_standalone](#help_core.open_help_standalone)
      - [Signature](#help_core.firma-2)
      - [Description](#help_core.descripci-n-2)
      - [Parameters (integrator level)](#help_core.par-metros-nivel-integrador)
      - [Minimal example](#help_core.ejemplo-m-nimo-2)
    - [3. Minimal integration contract (standalone vs overlay)](#help_core.3-contrato-m-nimo-de-integraci-n-standalone-vs-overlay)
  - [API for module help_viewer_impl.py](#help_core.api-del-m-dulo-help-viewer-impl-py-es)
    - [Part I — Public API (integration and usage)](#help_viewer_impl.parte-i-api-p-blica-integraci-n-y-uso)
    - [1. HelpConfig (dataclass)](#help_viewer_impl.HelpConfig)
      - [Description](#help_viewer_impl.descripci-n)
      - [Fields](#help_viewer_impl.campos)
      - [Usage notes](#help_viewer_impl.notas-de-uso)
    - [2. HelpViewer](#help_viewer_impl.HelpViewer)
      - [2.1 Constructor](#help_viewer_impl.2-1-constructor)
      - [2.2 Embedded usage (“widget” mode)](#help_viewer_impl.2-2-uso-embebido-modo-widget)
      - [2.3 Standalone usage](#help_viewer_impl.2-3-uso-standalone)
      - [2.4 Optional adapter as_interactive()](#help_viewer_impl.2-4-adaptador-opcional-as_interactive)
    - [3. Anchors and links](#help_viewer_impl.3-anclas-y-links)
      - [3.1 Explicit anchors (HTML)](#help_viewer_impl.3-1-anclas-expl-citas-html)
      - [3.2 Automatic anchors from headings](#help_viewer_impl.3-2-anclas-autom-ticas-por-encabezados)
      - [3.3 http(s) links](#help_viewer_impl.3-3-links-http-s)
    - [4. Images](#help_viewer_impl.4-im-genes)
    - [5. Tables](#help_viewer_impl.5-tablas)
- [Part II — Maintenance API (developers)](#help_viewer_impl.parte-ii-api-de-mantenimiento-desarrolladores)
  - [Module dependency graph (factual import graph)](#dependencias-entre-m-dulos-import-graph-factual)
  - [API for module help_core.py](#help_viewer_impl.api-del-m-dulo-help-core-py-es)
  - [API for module help_viewer_impl.py](#help_core.api-del-m-dulo-help-viewer-impl-py-es-2)
  - [API for module help_mini_markdown.py](#help_viewer_impl.api-del-m-dulo-help-mini-markdown-py-es)
  - [API for module md_tables.py](#help_mini_markdown.api-del-m-dulo-md-tables-py-es)
  - [API for module table_renderer.py](#md_tables.api-del-m-dulo-table-renderer-py-es)
  - [API for module image_cache.py](#table_renderer.api-del-m-dulo-image-cache-py-es)

---

<a id="parte-i-api-p-blica-usuario-final"></a>

## Part I — Public API (end users)

Entry points and types required to integrate and use the help system (*standalone* or *overlay*) without relying on internal details.

---

<a id="api-del-m-dulo-help-core-py-es"></a>

### API for module help_core.py

---

<a id="help_core.parte-i-api-p-blica-integraci-n-y-uso"></a>

#### Part I — Public API (integration and usage)

> **Public API goal:** allow using the help system without knowing the parser or the renderer internals.
> For implementation details, see **Part II** and the source code.

<a id="help_core.ShowHelpOverlay"></a>

#### 1. ShowHelpOverlay

<a id="help_core.firma"></a>

##### Signature

```python
def ShowHelpOverlay(
    display: pygame.Surface,
    md_text: str,
    title: str = "Help",
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

<a id="help_core.descripci-n"></a>

##### Description

Shows reduced-Markdown help as a **modal overlay** on the given display surface.

- It is **modal/blocking**: it stops the caller loop while the help is open.
- It uses HelpViewer internally and delegates event handling and rendering to it.
- It freezes the input frame (copies the display) and restores it at each iteration before drawing the viewer,
  so the overlay appears “on top” of a frozen background.

<a id="help_core.par-metros"></a>

##### Parameters

- display (pygame.Surface): target surface where the overlay is drawn.
- md_text (str): reduced Markdown content.
- title (str): help title.
- exit_keys (Tuple[int, ...]): keys that close the help. Default is ESC.
- fps (int): FPS cap for the modal loop.
- kernel_bg (Tuple[int,int,int]): background color for the help area.
- wheel_step (int): mouse wheel scroll step.
- scroll_limit_cooldown_ms (int): cooldown for the “scroll limit” notification (if the viewer triggers it).
- base_dir (Optional[str]): base directory for resolving relative paths (e.g., images).

<a id="help_core.comportamiento-y-detalles-relevantes"></a>

##### Behavior and relevant details

- If display is None, it raises ValueError.
- It temporarily adjusts keyboard **autorepeat** via pygame.key.set_repeat(250, 40) for smoother navigation
  during the modal loop, and restores the previous value on exit.
- The modal loop:
  - processes events (pygame.event.get()).
  - exits on QUIT or if a key in exit_keys is pressed.
  - forwards remaining events to viewer.handle_event(event).
  - restores the frozen frame and draws viewer.draw(display, rect).

<a id="help_core.ejemplo-m-nimo"></a>

##### Minimal example

```python
import pygame
from help_core_pygame.help_core import ShowHelpOverlay

pygame.init()
screen = pygame.display.set_mode((800, 480))

md = "# Help\n\nPress ESC to exit.\n\n- Item 1\n- Item 2\n"

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_F1:
            ShowHelpOverlay(screen, md, title="Help", exit_keys=(pygame.K_ESCAPE,))

    screen.fill((30, 30, 30))
    pygame.display.flip()

pygame.quit()
```

<a id="help_core.limitaciones"></a>

##### Limitations

- Any “dt jump” when returning to the main loop (if your game uses accumulated dt) is **not** handled here.
  If needed, your loop should discard or adjust the first dt after closing the help.

---

<a id="help_core.open_help_standalone"></a>

#### 2. open_help_standalone

<a id="help_core.firma-2"></a>

##### Signature

```python
def open_help_standalone(
    md_text: str,
    title: str = "Help",
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

<a id="help_core.descripci-n-2"></a>

##### Description

Opens a dedicated window with the help viewer.

Internally:
1. builds HelpConfig(...)
2. calls HelpViewer(cfg).open_window()

<a id="help_core.par-metros-nivel-integrador"></a>

##### Parameters (integrator level)

- md_text (str): reduced Markdown content.
- title (str): window/help title.
- size ((w,h)): window size.

**Optional style/fonts:**
- style_json_path, style_variant, style_overrides: optional style support.
- fonts_dir: base directory for fonts.
- help_font_file, help_code_font_file: font files for normal text and code.

**Indentation and scrolling:**
- indent_spaces_per_level: list indentation “logical” level (spaces) for parsing.
- visual_indent_px: visual indentation per level in pixels.
- wheel_step: wheel scroll step.
- kernel_bg: panel background color (if set).
- on_scroll_limit: callback invoked at scroll limit ("top"/"bottom" or other convention).
- scroll_limit_cooldown_ms: cooldown to avoid repeated callbacks.

**Paths:**
- base_dir: base for resolving relative paths (e.g., images).

<a id="help_core.ejemplo-m-nimo-2"></a>

##### Minimal example

```python
from help_core_pygame.help_core import open_help_standalone

md = "# Help\n\nThis is a standalone window.\n"
open_help_standalone(md, title="Help", size=(900, 600))
```

---

<a id="help_core.3-contrato-m-nimo-de-integraci-n-standalone-vs-overlay"></a>

#### 3. Minimal integration contract (standalone vs overlay)

- **Standalone:** call open_help_standalone(...) and the viewer manages its own window.
- **Modal overlay:** call ShowHelpOverlay(...) from your loop when you want to show help.
- **Embedded/widget overlay:** use HelpConfig + HelpViewer directly (see the viewer module section).

---

---

<a id="help_core.api-del-m-dulo-help-viewer-impl-py-es"></a>

### API for module help_viewer_impl.py

---

<a id="help_viewer_impl.parte-i-api-p-blica-integraci-n-y-uso"></a>

#### Part I — Public API (integration and usage)

> **Public API goal:** allow integrators to mount the viewer into a rectangle,
> feed it events, draw it, and optionally open it in standalone mode.

<a id="help_viewer_impl.HelpConfig"></a>

#### 1. HelpConfig (dataclass)

<a id="help_viewer_impl.descripci-n"></a>

##### Description

Viewer configuration container.

- Recommended place to define:
  - Markdown text
  - window size/title (standalone)
  - parsing parameters (tab_size, nesting, indentation)
  - interaction parameters (wheel_step, scroll-limit callback)
  - style parameters (optional JSON, overrides, fonts)

<a id="help_viewer_impl.campos"></a>

##### Fields

```python
@dataclass
class HelpConfig:
    # Content
    md_text: str
    title: str = "Help"
    size: Tuple[int, int] = (800, 480)

    # Paths
    base_dir: Optional[str] = None

    # Parser / layout
    tab_size: int = 4
    max_list_nesting: int = 6
    indent_spaces_per_level: int = 2
    visual_indent_px: int = 24

    # Interaction
    wheel_step: int = 48
    on_scroll_limit: Optional[Callable[[str], None]] = None
    scroll_limit_cooldown_ms: int = 0

    # Styles
    style_json_path: Optional[str] = None
    style_variant: Optional[str] = None
    style_overrides: Optional[Dict[str, Any]] = None

    # Fonts (optional TTF)
    fonts_dir: Optional[str] = None
    help_font_file: Optional[str] = None
    help_code_font_file: Optional[str] = None

    # Panel background (optional)
    kernel_bg: Optional[RGB] = None
```

<a id="help_viewer_impl.notas-de-uso"></a>

##### Usage notes

- base_dir is important for resolving relative image paths.
- on_scroll_limit(where) currently receives "top" or "bottom".
- style_json_path is optional: if missing, DEFAULT_STYLE is used.
- style_overrides lets you patch specific keys without a JSON file.

---

<a id="help_viewer_impl.HelpViewer"></a>

#### 2. HelpViewer

<a id="help_viewer_impl.2-1-constructor"></a>

##### 2.1 Constructor

```python
class HelpViewer:
    def __init__(self, cfg: HelpConfig):
        ...
```

Creates the viewer:
- loads style (DEFAULT_STYLE + optional JSON + overrides).
- initializes internal parser _MiniMarkdown(...) with cfg parameters.
- initializes image cache ImageCache(cfg.base_dir).
- normalizes and parses the document:
  - normalized = parser.normalize(cfg.md_text)
  - self._blocks = parser.parse(normalized)

> **Important:** after construction, the viewer has no layout until on_mount(rect) is called.

---

<a id="help_viewer_impl.2-2-uso-embebido-modo-widget"></a>

##### 2.2 Embedded usage (“widget” mode)

#### Minimal lifecycle

1) Mount with an absolute rect:
```python
viewer.on_mount(rect)
```

2) In your main loop, feed events:
```python
viewer.handle_event(event)
```

3) Each frame, draw:
```python
viewer.draw(screen, rect)
```

4) When unmounting (scene change, shutdown, etc.):
```python
viewer.on_unmount()
```

#### Relevant public methods

```python
def on_mount(self, rect: pygame.Rect) -> None: ...
def on_unmount(self) -> None: ...
def handle_event(self, event: pygame.event.Event) -> bool: ...
def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None: ...
def update(self, dt_ms: int) -> None: ...
def wants_keyboard(self) -> bool: ...
def wants_wheel(self) -> bool: ...
```

- handle_event(...) returns True if it consumed the event.
- update(...) exists for compatibility; currently a no-op (pass).
- wants_keyboard() and wants_wheel() return True (widget-style contract).

#### Supported events (practical contract)

- pygame.MOUSEWHEEL: vertical scroll.
- pygame.MOUSEBUTTONDOWN:
  - click on http(s) link → open browser.
  - click on #anchor link → internal jump to anchor.
  - click/drag on scrollbar thumb → drag scrolling.
- pygame.MOUSEBUTTONUP: release drag.
- pygame.MOUSEMOTION: updates drag if active.
- pygame.KEYDOWN:
  - F2: toggle debug mode (anchors and image “ALT”)
  - navigation: UP, DOWN, PAGEUP, PAGEDOWN, HOME, END

---

<a id="help_viewer_impl.2-3-uso-standalone"></a>

##### 2.3 Standalone usage

```python
def open_window(self) -> None:
    ...
```

- initializes pygame.
- creates display.set_mode(cfg.size) and caption(cfg.title).
- mounts on_mount(screen.get_rect()).
- loop:
  - ESC or QUIT → exit
  - otherwise → handle_event(e)
  - draw(screen, rect) + display.flip()
- in finally:
  - on_unmount()
  - restores pygame.key.set_repeat(...)
  - restores mouse visibility
  - pygame.quit()

**When to use it:** if you want an “all-in-one” viewer without integrating into your loop.

---

<a id="help_viewer_impl.2-4-adaptador-opcional-as_interactive"></a>

##### 2.4 Optional adapter as_interactive()

```python
def as_interactive(self):
    ...
```

Returns an adapter object with:

- on_mount(rect)
- on_unmount()
- update(dt)
- draw(surface, rect)
- handle_event(event) -> bool
- wants_keyboard()
- wants_wheel()

Useful if your framework expects that contract and you want to plug HelpViewer in with minimal glue.

---

<a id="help_viewer_impl.3-anclas-y-links"></a>

#### 3. Anchors and links

<a id="help_viewer_impl.3-1-anclas-expl-citas-html"></a>

##### 3.1 Explicit anchors (HTML)

The parser can emit {"type":"anchor","id":...} from `<a id="..."></a>`. The viewer:
- registers them as self._anchors[id] = y
- allows jumps using #id links on click.

<a id="help_viewer_impl.3-2-anclas-autom-ticas-por-encabezados"></a>

##### 3.2 Automatic anchors from headings

During composition (_compose_all), for each h1..h6:
- generates slug = _slugify(text)
- registers self._anchors[slug] = y
- also registers a “no numeric prefix” variant (e.g., 2-3-...-title → title)

<a id="help_viewer_impl.3-3-links-http-s"></a>

##### 3.3 http(s) links

On click over a region marked as link and href starts with http:// or https://,
it calls webbrowser.open(href).

---

<a id="help_viewer_impl.4-im-genes"></a>

#### 4. Images

- The parser emits {"type":"img","alt":..., "src":...}.
- During composition:
  - tries to load via ImageCache.get_scaled(src, width)
  - if available: emits a line type="image" with an already-scaled surface
  - if missing: emits type="image_missing" with a placeholder

In debug mode (F2), it overlays the ALT text on top of the image.

---

<a id="help_viewer_impl.5-tablas"></a>

#### 5. Tables

- The parser emits table blocks (schema defined by md_tables).
- During composition:
  - calls render_table(blk, body_font, header_font)
  - stores the resulting surface for blitting
  - on failure, draws a fallback [Table render error]

---

---

<a id="help_viewer_impl.parte-ii-api-de-mantenimiento-desarrolladores"></a>

## Part II — Maintenance API (developers)

Parser, renderer and auxiliary modules (tables, images, style, etc.) needed to maintain and evolve the project.

---

<a id="dependencias-entre-m-dulos-import-graph-factual"></a>

### Module dependency graph (factual import graph)

This section describes **what imports what** (module-level) according to the current code.

**Exported by the package (help_core_pygame/__init__.py)**

- HelpConfig, HelpViewer, open_help_standalone, ShowHelpOverlay, DEFAULT_STYLE, RGB
- Note: symbols prefixed with `_` (e.g., `_MiniMarkdown`) are **not** exported.

**Core**

- help_core.py
  - uses pygame
  - imports internally: _MiniMarkdown from help_mini_markdown.py
  - imports internally: HelpViewer, HelpConfig, DEFAULT_STYLE, RGB from help_viewer_impl.py

- help_viewer_impl.py
  - uses pygame
  - imports internally: _MiniMarkdown from help_mini_markdown.py
  - imports internally: render_table from table_renderer.py
  - imports internally: ImageCache from image_cache.py

- help_mini_markdown.py
  - imports internally: is_table_start, parse_table from md_tables.py
  - note: contains an absolute-import fallback (from md_tables import ...) intended for direct execution/special environments.

- md_tables.py
  - stdlib only (re, dataclasses, typing)

- table_renderer.py
  - depends on pygame

- image_cache.py
  - depends on pygame, pathlib

**Demos (depend on the public API)**

- demo_help_overlay_beep.py → HelpConfig, HelpViewer (and open_help_standalone as an alternative)
- demo_help_show_overlay_circles.py → ShowHelpOverlay
- demo_help_standalone.py → open_help_standalone
- demo_mini_MarkDown_TEST.py → open_help_standalone

---

<a id="help_viewer_impl.api-del-m-dulo-help-core-py-es"></a>

### API for module help_core.py (maintenance)

---

<a id="help_core.parte-ii-api-interna-de-mantenimiento-relacionada-con-este-m-dulo"></a>

#### Part II — Internal / maintenance API (related to this module)

> This part is for maintenance: understanding the module, decisions, and safe change points.
> It is not intended for integrators.

<a id="help_core.4-papel-de-help-core-py-en-la-arquitectura"></a>

#### 4. Role of help_core.py in the architecture

This module is a **facade**: it glues pieces together and provides “fast paths”:

- Builds HelpConfig with reasonable defaults.
- Creates and uses HelpViewer.
- Implements a modal loop (overlay) with frozen-frame restoration.

It should not contain complex parsing/rendering logic: that belongs in specialized modules.

---

<a id="help_core.5-dependencias-y-s-mbolos-importados"></a>

#### 5. Dependencies and imported symbols

This module depends on:

- Parser (reduced Markdown): _MiniMarkdown (imported from help_mini_markdown).
- Viewer: HelpViewer, HelpConfig (imported from help_viewer_impl).
- Pygame: pygame.Surface, events, clock, key repeat, etc.

**Maintenance note:** although _MiniMarkdown is imported here, it should not be exposed as part of the public integration API.
Its full documentation should live in the parser module section.

---

<a id="help_core.6-detalles-de-implementaci-n-relevantes"></a>

#### 6. Relevant implementation details

<a id="help_core.6-1-overlay-modal-y-frame-congelado"></a>

##### 6.1 Modal overlay and frozen frame

ShowHelpOverlay does:

- canvas = display.copy() on entry.
- Each frame: display.blit(canvas, (0, 0)) before drawing the viewer.

This avoids artifacts and keeps a “frozen state” under the help overlay.

<a id="help_core.6-2-gesti-n-de-autorepeat"></a>

##### 6.2 Autorepeat handling

It saves pygame.key.get_repeat() and sets pygame.key.set_repeat(250, 40) during the modal loop,
restoring in finally.

**Why:** make keyboard navigation inside the viewer smoother without relying on the game loop.

---

<a id="help_core.7-testing-manual-demos-relacionadas"></a>

#### 7. Manual testing (related demos)

Usually validated indirectly via demos:

- Standalone (opens a window).
- Modal overlay (F1/F2/ESC depending on demo).
- Embedded overlay (if applicable).

---

<a id="help_core.8-problemas-conocidos-notas-operativas"></a>

#### 8. Known issues / operational notes

- dt “jump” after returning from modal overlay (if the game uses dt).
- Relative image paths depend on base_dir and image loading behavior.

---

<a id="help_core.9-historial-y-compatibilidad"></a>

#### 9. History and compatibility

- License: MIT.
- Requirements: Python 3.9+ and Pygame 2.0+.

---

<a id="help_core.10-changelog-del-documento"></a>

#### 10. Document changelog

---

<a id="help_core.api-del-m-dulo-help-viewer-impl-py-es-2"></a>

### API for module help_viewer_impl.py (maintenance)

---

<a id="help_viewer_impl.parte-ii-api-interna-de-mantenimiento"></a>

#### Part II — Internal / maintenance API

> This part is for maintaining the project: internal structure, helpers, and decisions.

<a id="help_viewer_impl.DEFAULT_STYLE"></a>

#### 6. Style (DEFAULT_STYLE and _load_style)

- DEFAULT_STYLE defines sizes, colors and spacing (hlp_* keys).
- _load_style(cfg):
  1) starts from DEFAULT_STYLE
  2) if cfg.style_json_path exists: loads JSON and applies variant if needed
  3) applies cfg.style_overrides
  4) normalizes colors list→tuple
  5) applies guardrails and defaults (padding, wheel step, code pad, font scale, etc.)
  6) sets hlp_CodeBlockMode (code_line or code_block)

---

<a id="help_viewer_impl._lines"></a>

#### 7. Composition and _lines structure

<a id="help_viewer_impl.7-1-self-blocks-entrada"></a>

##### 7.1 self._blocks (input)

Output of the parser (_MiniMarkdown.parse): list of dict blocks.

<a id="help_viewer_impl.7-2-self-lines-salida-de-composici-n"></a>

##### 7.2 self._lines (composition output)

List of “renderable line dicts”, with typical keys:

- y, h: vertical position in document coords and line/block height
- runs: list of tuples (font_key, color, text, rx) for text blits
- clicks: list of clickable logical rects {x, w, href}
- extra flags: is_code, hr, type (image, table, anchor, comment, etc.)
- specific fields:
  - code: code_bg, code_bg_indent, code_bg_width, code_block_indent
  - image: surface, alt, src, w
  - table: surface, w

**Useful invariant:** draw() should iterate self._lines without assuming every line has runs.

---

<a id="help_viewer_impl.draw"></a>

#### 8. Rendering (draw) and scrolling

- draw(surface, rect):
  - fills kernel background in rect
  - computes paddings (vertical fixed; horizontal based on base font * scale)
  - clamps scroll based on visible height
  - iterates visible _lines and draws:
    - code backgrounds (depending on hlp_CodeBlockMode)
    - images / placeholders
    - tables
    - hr
    - text runs
    - link underline (based on clicks)
  - draws scrollbar if content_height > rect.height

- Scrolling:
  - _scroll is in document coordinates (px)
  - max_scroll = content_height - visible_height

---

<a id="help_viewer_impl.handle_event"></a>

#### 9. Events (handle_event) and “scroll limit”

- Wheel and keys apply clamp.
- If scroll does not change and you are at a limit, it calls _notify_scroll_limit("top"/"bottom").
- _notify_scroll_limit enforces cooldown via pygame.time.get_ticks() if configured.

---

<a id="help_viewer_impl.10-helpers-internos-principales-inventario"></a>

#### 10. Main internal helpers (inventory)

> This inventory helps maintenance, but it is not a public contract.

- _notify_scroll_limit(where)
- _font_for(font_key)
- _hit_test_link(mouse_pos)
- _slugify(text)
- _jump_to_anchor(anchor_id)
- _compose_all()
- _compose_code_block_as_lines(...)
- _compose_code_block_as_box(...)
- _wrap_runs(...)
- _wrap_text_preserving_words(...)
- _split_preserving_spaces(...)
- _fit_text(...)
- _ensure_fonts()
- _font_key_for(role, bold, italic)
- _measure_text(s, font_key)
- _line_height_for(role)
- _space_px()
- _scrollbar_rect()
- _thumb_rect(track)

---

<a id="help_viewer_impl.11-notas-operativas-y-deuda-t-cnica"></a>

#### 11. Operational notes / technical debt

- There is duplicated code around anchor marker_h (two assignments in a row).
- There is an unused _ensure_fonts_OLD (candidate for removal in a separate cleanup).
- update(dt_ms) is a no-op but part of the interface.

---

<a id="help_viewer_impl.12-relaci-n-con-otros-documentos"></a>

#### 12. Related documents

- docs/API_help_core_en.md: high-level entry points (overlay/standalone).
- docs/API_help_mini_markdown_en.md: parser and inline tokenization.
- docs/API_md_tables_en.md, docs/API_table_renderer_en.md: tables.
- docs/API_image_cache_en.md: images.
- docs/ARCHITECTURE_en.md: system overview.

---

## Remaining module references

For the remaining maintenance modules (`help_mini_markdown.py`, `md_tables.py`, `table_renderer.py`, `image_cache.py`),
the content is identical to the Spanish edition except for language. If you want the full translated text to be included
here as well (instead of keeping it modular), it can be expanded in a follow-up revision once the English module docs exist.

> 🔙 Return to index: [INDEX_en.md](INDEX_es.md)

