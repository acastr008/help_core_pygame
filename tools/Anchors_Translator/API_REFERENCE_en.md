# API_REFERENCE_en — help_core_pygame

> 🔙 Back to index: [INDEX_en.md](INDEX_en.md)

> Unified API reference for the project.
>
> This document is split into two parts:
> - **Part I — Public API (end user)**: integration and use of the help system.
> - **Part II — Maintenance API (developers)**: parser/renderer and auxiliary modules.

⚠️ **Stability criteria for both API parts**

- The **public API** is the part of the API considered more stable and easier to use, oriented to the end user. Ideal to add a solid help system to a Pygame game.
- The **maintenance API** is a much broader part of the API and may change more frequently; it is documented to facilitate maintenance and the addition of improvements and extensions, as well as to debug errors or deficiencies in the code.

![Public API vs Maintenance API](APIs_pubica_vs_mantenim.png)

## Requirements and compatibility

- Python: **>= 3.9**
- Pygame: **>= 2.0**
- Package version (pyproject.toml): **0.1.2**

---

## Table of contents
- [Part I — Public API (end user)](#part-i-public-api-end-user)
  - [API for module help_core.py (EN)](#api-for-module-help_core-py)
    - [Part I — Public API (integration and usage)](#help_core.part-i-public-api-integration-and-usage)
    - [1. ShowHelpOverlay](#help_core.ShowHelpOverlay)
      - [Signature](#help_core.signature)
      - [Description](#help_core.description)
      - [Parameters](#help_core.parameters)
      - [Behavior and relevant details](#help_core.behavior-and-relevant-details)
      - [Minimal example](#help_core.minimal-example)
      - [Limitations](#help_core.limitations)
    - [2. open_help_standalone](#help_core.open_help_standalone)
      - [Signature](#help_core.signature-2)
      - [Description](#help_core.description-2)
      - [Parameters (integrator level)](#help_core.parameters-integrator-level)
      - [Minimal example](#help_core.minimal-example-2)
    - [3. Minimal integration contract (standalone vs overlay)](#help_core.3-minimal-integration-contract-standalone-vs-overlay)
  - [API for module help_viewer_impl.py (EN)](#help_core.api-for-module-help_viewer_impl-py)
    - [Part I — Public API (integration and usage)](#help_viewer_impl.part-i-public-api-integration-and-usage)
    - [1. HelpConfig (dataclass)](#help_viewer_impl.HelpConfig)
      - [Description](#help_viewer_impl.description)
      - [Fields](#help_viewer_impl.fields)
      - [Usage notes](#help_viewer_impl.usage-notes)
    - [2. HelpViewer](#help_viewer_impl.HelpViewer)
      - [2.1 Constructor](#help_viewer_impl.2-1-constructor)
      - [2.2 Embedded usage (“widget” mode)](#help_viewer_impl.2-2-embedded-usage-widget-mode)
      - [2.3 Standalone usage](#help_viewer_impl.2-3-standalone-usage)
      - [2.4 Optional adapter as_interactive()](#help_viewer_impl.2-4-optional-adapter-as_interactive)
    - [3. Anchors and links](#help_viewer_impl.3-anchors-and-links)
      - [3.1 Explicit anchors (HTML)](#help_viewer_impl.3-1-explicit-anchors-html)
      - [3.2 Automatic anchors from headings](#help_viewer_impl.3-2-automatic-anchors-from-headings)
      - [3.3 http(s) links](#help_viewer_impl.3-3-http-s-links)
    - [4. Images](#help_viewer_impl.4-images)
    - [5. Tables](#help_viewer_impl.5-tables)
- [Part II — Maintenance API (developers)](#help_viewer_impl.part-ii-maintenance-api-developers)
  - [API for module help_core.py (EN)](#help_viewer_impl.api-for-module-help_core-py)
    - [Part II — Internal / maintenance API (related to this module)](#help_core.part-ii-internal-maintenance-api-related-to-this-module)
    - [4. Role of help_core.py in the architecture](#help_core.4-role-of-help_core-py-in-the-architecture)
    - [5. Dependencies and imported symbols](#help_core.5-dependencies-and-imported-symbols)
    - [6. Relevant implementation details](#help_core.6-relevant-implementation-details)
      - [6.1 Modal overlay and frozen frame](#help_core.6-1-modal-overlay-and-frozen-frame)
      - [6.2 Autorepeat handling](#help_core.6-2-autorepeat-handling)
      - [6.3 Legacy variant of ShowHelpOverlay (commented)](#help_core.ShowHelpOverlay-2)
    - [7. Manual testing (related demos)](#help_core.7-manual-testing-related-demos)
    - [8. Known issues / operational notes](#help_core.8-known-issues-operational-notes)
    - [9. History and compatibility](#help_core.9-history-and-compatibility)
    - [10. Document changelog](#help_core.10-document-changelog)
  - [API for module help_viewer_impl.py (EN)](#help_core.api-for-module-help_viewer_impl-py-2)
    - [Part II — Internal / maintenance API](#help_viewer_impl.part-ii-internal-maintenance-api)
    - [6. Style (DEFAULT_STYLE and _load_style)](#help_viewer_impl.DEFAULT_STYLE)
    - [7. Composition and structure of _lines](#help_viewer_impl._lines)
      - [7.1 self._blocks (input)](#help_viewer_impl.7-1-self-blocks-input)
      - [7.2 self._lines (composition output)](#help_viewer_impl.7-2-self-lines-composition-output)
    - [8. Render (draw) and scroll](#help_viewer_impl.draw)
    - [9. Events (handle_event) and “scroll limit”](#help_viewer_impl.handle_event)
    - [10. Main internal helpers (inventory)](#help_viewer_impl.10-main-internal-helpers-inventory)
    - [11. Operational notes and technical debt](#help_viewer_impl.11-operational-notes-and-technical-debt)
  - [API for module help_mini_markdown.py (EN)](#help_viewer_impl.api-for-module-help_mini_markdown-py)
    - [Part II — Internal / maintenance API](#help_mini_markdown.part-ii-internal-maintenance-api)
    - [1. Class _MiniMarkdown](#help_mini_markdown._MiniMarkdown)
      - [1.1 Constructor](#help_mini_markdown.1-1-constructor)
    - [2. normalize(text)](#help_mini_markdown.2-normalize-text)
      - [Signature](#help_mini_markdown.signature)
      - [Description](#help_mini_markdown.description)
      - [Returns](#help_mini_markdown.returns)
    - [3. parse(text)](#help_mini_markdown.3-parse-text)
      - [Signature](#help_mini_markdown.signature-2)
      - [Description](#help_mini_markdown.description-2)
      - [Emitted block types (dict)](#help_mini_markdown.emitted-block-types-dict)
    - [4. tokenize_inline(text)](#help_mini_markdown.4-tokenize-inline-text)
      - [Signature](#help_mini_markdown.signature-3)
      - [Description](#help_mini_markdown.description-3)
      - [Output format (“run”)](#help_mini_markdown.output-format-run)
      - [Important rules](#help_mini_markdown.important-rules)
    - [5. Maintenance details and decisions](#help_mini_markdown.5-maintenance-details-and-decisions)
      - [5.1 Emphasis regex and word boundaries](#help_mini_markdown.5-1-emphasis-regex-and-word-boundaries)
      - [5.2 Fenced code without language](#help_mini_markdown.5-2-fenced-code-without-language)
      - [5.3 Double fence-closing block at EOF (note)](#help_mini_markdown.5-3-double-fence-closing-block-at-eof-note)
    - [6. Interaction with tables (md_tables)](#help_mini_markdown.md_tables)
  - [API for module md_tables.py (EN)](#help_mini_markdown.api-for-module-md_tables-py)
    - [Part II — Internal / maintenance API](#md_tables.part-ii-internal-maintenance-api)
    - [5. Internal constants](#md_tables.5-internal-constants)
    - [6. TableParseResult (dataclass)](#md_tables.TableParseResult)
      - [Usage](#md_tables.usage)
    - [7. is_table_start(lines, index)](#md_tables.7-is-table-start-lines-index)
      - [Signature](#md_tables.signature)
      - [Exact rules (as implemented)](#md_tables.exact-rules-as-implemented)
    - [8. parse_table(lines, index)](#md_tables.8-parse-table-lines-index)
      - [Signature](#md_tables.signature-2)
      - [Contract of the returned block](#md_tables.returned-block-contract)
      - [Relevant parsing rules](#md_tables.relevant-parsing-rules)
    - [9. Internal helpers](#md_tables.9-internal-helpers)
      - [9.1 _parse_table_row(line)](#md_tables.9-1-parse-table-row-line)
      - [9.2 _parse_separator_row(line, expected_cols)](#md_tables.9-2-parse-separator-row-line-expected-cols)
      - [9.3 _normalize_row(row_cells, ncols)](#md_tables.9-3-normalize-row-row-cells-ncols)
    - [10. Maintenance notes / decisions](#md_tables.10-maintenance-notes-decisions)
    - [11. Relationship with other modules / docs](#md_tables.11-relationship-with-other-modules)
  - [API for module table_renderer.py (EN)](#md_tables.api-for-module-table_renderer-py)
    - [Part II — Internal / maintenance API](#table_renderer.part-ii-internal-maintenance-api)
    - [5. Internal constants](#table_renderer.5-internal-constants)
    - [6. TableRenderResult (dataclass)](#table_renderer.TableRenderResult)
    - [7. render_table(table_block, body_font, header_font)](#table_renderer.7-render-table-table-block-body-font-header-font)
      - [Signature](#table_renderer.signature)
      - [Input block contract (table_block)](#table_renderer.table_block)
      - [Behavior](#table_renderer.behavior)
      - [Returns](#table_renderer.returns)
    - [8. Private helpers](#table_renderer.8-private-helpers)
      - [8.1 _validate_table_block(table_block)](#table_renderer.8-1-validate-table-block-table-block)
      - [8.2 _blit_text_centered(...)](#table_renderer.8-2-blit-text-centered)
      - [8.3 _blit_text_aligned(...)](#table_renderer.8-3-blit-text-aligned)
      - [8.4 _draw_grid(...)](#table_renderer.8-4-draw-grid)
    - [9. Maintenance notes](#table_renderer.9-maintenance-notes)
  - [API for module image_cache.py (EN)](#table_renderer.api-for-module-image_cache-py)
    - [Part II — Internal / maintenance API](#image_cache.part-ii-internal-maintenance-api)
    - [4. Internal types](#image_cache.4-internal-types)
      - [4.1 SurfaceInfo](#image_cache.SurfaceInfo)
      - [4.2 _ImageKey (dataclass)](#image_cache._ImageKey)
    - [5. Class ImageCache](#image_cache.ImageCache)
      - [5.1 Constructor](#image_cache.5-1-constructor)
      - [5.2 set_base_dir(base_dir)](#image_cache.5-2-set-base-dir-base-dir)
      - [5.3 resolve_src_to_abs_path(src)](#image_cache.5-3-resolve-src-to-abs-path-src)
      - [5.4 get_scaled(src, target_width)](#image_cache.5-4-get-scaled-src-target-width)
    - [6. Private methods](#image_cache.6-private-methods)
      - [6.1 _load_image(abs_path)](#image_cache.6-1-load-image-abs-path)
      - [6.2 _scale_to_width(surface, target_width)](#image_cache.6-2-scale-to-width-surface-target-width)
    - [7. Maintenance considerations](#image_cache.7-maintenance-considerations)
      - [7.1 Cache policy](#image_cache.7-1-cache-policy)
      - [7.2 Recommended minimal changes](#image_cache.7-2-recommended-minimal-changes)

---

<a id="part-i-public-api-end-user"></a>

## Part I — Public API (end user)

Entry points and types needed to integrate and use the help system (*standalone* or *overlay*) without depending on internal renderer details.

---

<a id="api-for-module-help_core-py"></a>

### API for module help_core.py (EN)

---

<a id="help_core.part-i-public-api-integration-and-usage"></a>

#### Part I — Public API (integration and usage)

> **Goal of the public API:** allow using the help system without knowing the parser or internal renderer details.
> For more implementation details, see **Part II** and the source code.

<a id="help_core.ShowHelpOverlay"></a>

#### 1. ShowHelpOverlay

<a id="help_core.signature"></a>

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

<a id="help_core.description"></a>

##### Description

Shows help in reduced Markdown format as a **modal overlay** over the provided display.

- It is **modal/blocking**: it stops the caller’s loop while the help is open.
- Uses HelpViewer internally and delegates event handling and rendering to it.
- Freezes the incoming frame (copies the display) and restores it on each iteration before drawing the viewer,
  so the overlay appears “on top” of the frozen state.

<a id="help_core.parameters"></a>

##### Parameters

- display (pygame.Surface): main surface where the overlay will be drawn.
- md_text (str): reduced Markdown content.
- title (str): title for the help panel.
- exit_keys (Tuple[int, ...]): keys that close the help. Default: ESC.
- fps (int): FPS cap for the modal loop.
- kernel_bg (Tuple[int,int,int]): background color for the help area.
- wheel_step (int): scroll step per wheel tick.
- scroll_limit_cooldown_ms (int): cooldown for the “scroll limit” event (if the viewer uses it).
- base_dir (Optional[str]): base directory to resolve relative paths (e.g., images).

<a id="help_core.behavior-and-relevant-details"></a>

##### Behavior and relevant details

- If display is None, it raises ValueError.
- Temporarily adjusts keyboard **autorepeat** with pygame.key.set_repeat(250, 40) to improve navigation
  during the modal, and restores it on exit.
- The modal loop:
  - Processes events (pygame.event.get()).
  - Exits on QUIT or if a key in exit_keys is pressed.
  - Passes the rest of the events to viewer.handle_event(event).
  - Restores the frozen frame and draws viewer.draw(display, rect).

<a id="help_core.minimal-example"></a>

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

<a id="help_core.limitations"></a>

##### Limitations

- The “time jump” when returning to the main loop (if your game uses accumulated dt) **is not corrected here**.
  If you need it, your loop must discard or adjust the first dt after closing help.

---

<a id="help_core.open_help_standalone"></a>

#### 2. open_help_standalone

<a id="help_core.signature-2"></a>

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

<a id="help_core.description-2"></a>

##### Description

Opens its own window with the help viewer.

Internally:
1. Builds HelpConfig(...)
2. Runs HelpViewer(cfg).open_window()

<a id="help_core.parameters-integrator-level"></a>

##### Parameters (integrator level)

- md_text (str): reduced Markdown content.
- title (str): window/help title.
- size ((w,h)): window size.

**Style/font options (optional):**
- style_json_path, style_variant, style_overrides: optional style support.
- fonts_dir: base directory for fonts.
- help_font_file, help_code_font_file: font files for normal text and code.

**Indentation and scroll options:**
- indent_spaces_per_level: “logical” indentation per level (spaces) for lists.
- visual_indent_px: visual indentation per level in pixels.
- wheel_step: scroll step per wheel tick.
- kernel_bg: background color for the help panel (if specified).
- on_scroll_limit: callback when a limit is reached (“top”/“bottom” or other convention).
- scroll_limit_cooldown_ms: cooldown to avoid firing the callback continuously.

**Paths:**
- base_dir: base to resolve relative paths (e.g., images).

<a id="help_core.minimal-example-2"></a>

##### Minimal example

```python
from help_core_pygame.help_core import open_help_standalone

md = "# Help\n\nThis is a standalone window.\n"
open_help_standalone(md, title="Help", size=(900, 600))
```

---

<a id="help_core.3-minimal-integration-contract-standalone-vs-overlay"></a>

#### 3. Minimal integration contract (standalone vs overlay)

- **Standalone:** you call open_help_standalone(...) and the viewer manages its own window.
- **Modal overlay:** you call ShowHelpOverlay(...) from your loop whenever you want to show help.
- **Embedded/widget overlay:** it is recommended to use HelpConfig + HelpViewer directly (see the viewer module).

---

<a id="help_core.api-for-module-help_viewer_impl-py"></a>

### API for module help_viewer_impl.py (EN)

---

<a id="help_viewer_impl.part-i-public-api-integration-and-usage"></a>

#### Part I — Public API (integration and usage)

> **Goal of the public API:** allow an integrator to mount the viewer into a rectangle,
> feed it events, draw it, and optionally open it in standalone mode.

<a id="help_viewer_impl.HelpConfig"></a>

#### 1. HelpConfig (dataclass)

<a id="help_viewer_impl.description"></a>

##### Description

Configuration container for the viewer.

- Recommended place to define:
  - Markdown text
  - Size/title (standalone)
  - Parsing parameters (tab_size, nesting, indentation)
  - Interaction parameters (wheel_step, limit callback)
  - Style parameters (optional JSON, overrides, fonts)

<a id="help_viewer_impl.fields"></a>

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

    # Parser / composition
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

<a id="help_viewer_impl.usage-notes"></a>

##### Usage notes

- base_dir is important to resolve relative images in Markdown.
- on_scroll_limit(where) receives "top" or "bottom" (current convention).
- style_json_path is optional: if it does not exist, DEFAULT_STYLE is used.
- style_overrides allows adjusting specific keys without a JSON file.

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
- Loads style (DEFAULT_STYLE + optional JSON + overrides).
- Initializes parser _MiniMarkdown(...) with cfg parameters.
- Initializes image cache ImageCache(cfg.base_dir).
- Normalizes and parses the document:
  - normalized = parser.normalize(cfg.md_text)
  - self._blocks = parser.parse(normalized)

> **Important:** after construction, the viewer has no layout until on_mount(rect) is called.

---

<a id="help_viewer_impl.2-2-embedded-usage-widget-mode"></a>

##### 2.2 Embedded usage (“widget” mode)

#### Minimal lifecycle

1) Mount with an absolute rectangle:
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

4) On unmount (scene change, closing, etc.):
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
- update(...) exists for compatibility; currently it does nothing (pass).
- wants_keyboard() and wants_wheel() return True (widget-like interface).

#### Supported events (practical contract)

- pygame.MOUSEWHEEL: vertical scroll.
- pygame.MOUSEBUTTONDOWN:
  - click on http(s):// link → opens browser.
  - click on #anchor link → internal jump to anchor.
  - click-and-drag on scrollbar thumb → drag scroll.
- pygame.MOUSEBUTTONUP: releases drag.
- pygame.MOUSEMOTION: updates drag if active.
- pygame.KEYDOWN:
  - F2: toggles debug mode (anchors and image “ALT”)
  - Navigation: UP, DOWN, PAGEUP, PAGEDOWN, HOME, END

---

<a id="help_viewer_impl.2-3-standalone-usage"></a>

##### 2.3 Standalone usage

```python
def open_window(self) -> None:
    ...
```

- Initializes pygame.
- Creates display.set_mode(cfg.size) and caption(cfg.title).
- Mounts on_mount(screen.get_rect()).
- Loop:
  - ESC or QUIT → exit
  - otherwise → handle_event(e)
  - draw(screen, rect) + display.flip()
- In finally:
  - on_unmount()
  - restores pygame.key.set_repeat(...)
  - restores mouse visibility
  - pygame.quit()

**When to use it:** if you want a self-contained viewer without integrating it into your game loop.

---

<a id="help_viewer_impl.2-4-optional-adapter-as_interactive"></a>

##### 2.4 Optional adapter as_interactive()

```python
def as_interactive(self):
    ...
```

Returns an adapter object with this interface:

- on_mount(rect)
- on_unmount()
- update(dt)
- draw(surface, rect)
- handle_event(event) -> bool
- wants_keyboard()
- wants_wheel()

Useful if your GUI/framework expects that contract and you want to plug in HelpViewer without coupling dependencies.

---

<a id="help_viewer_impl.3-anchors-and-links"></a>

#### 3. Anchors and links

<a id="help_viewer_impl.3-1-explicit-anchors-html"></a>

##### 3.1 Explicit anchors (HTML)
The parser can emit blocks {"type":"anchor","id":...} from `<a id="..."></a>`.
The viewer:
- registers them in self._anchors[id] = y
- allows jumping with #id links on click.

<a id="help_viewer_impl.3-2-automatic-anchors-from-headings"></a>

##### 3.2 Automatic anchors from headings
During composition (_compose_all), for each h1..h6:
- generates slug = _slugify(text)
- registers self._anchors[slug] = y
- registers a variant “without numeric prefix” (e.g. 2-3-...-title → title)

<a id="help_viewer_impl.3-3-http-s-links"></a>

##### 3.3 http(s) links
If you click on a marked link region and href starts with http:// or https://,
webbrowser.open(href) is called.

---

<a id="help_viewer_impl.4-images"></a>

#### 4. Images

- The parser emits {"type":"img","alt":..., "src":...}.
- During composition:
  - tries to load with ImageCache.get_scaled(src, width)
  - if it exists: creates a line type="image" with an already scaled surface
  - if missing: creates type="image_missing" with a placeholder

In debug mode (F2), the alt text is overlaid as a label on the image.

---

<a id="help_viewer_impl.5-tables"></a>

#### 5. Tables

- The parser emits blocks of type table (schema defined by md_tables).
- During composition:
  - calls render_table(blk, body_font, header_font)
  - stores a table surface for blitting
  - if it fails, draws a fallback [Table render error]

---

---

<a id="help_viewer_impl.part-ii-maintenance-api-developers"></a>

## Part II — Maintenance API (developers)

Parser, renderer, and auxiliary modules (tables, images, style, etc.) needed for maintaining and evolving the project.

---

### Module dependencies (import graph, factual)

This section describes **what imports what** (module level) according to the current code.

**Exported by the package (help_core_pygame/__init__.py)**

- HelpConfig, HelpViewer, open_help_standalone, ShowHelpOverlay, DEFAULT_STYLE, RGB
- Note: symbols with a leading _ (for example _MiniMarkdown) are **not** exported.

**Core**

- help_core.py
  - uses pygame
  - internally imports: _MiniMarkdown from help_mini_markdown.py
  - internally imports: HelpViewer, HelpConfig, DEFAULT_STYLE, RGB from help_viewer_impl.py

- help_viewer_impl.py
  - uses pygame
  - internally imports: _MiniMarkdown from help_mini_markdown.py
  - internally imports: render_table from table_renderer.py
  - internally imports: ImageCache from image_cache.py

- help_mini_markdown.py
  - internally imports: is_table_start, parse_table from md_tables.py
  - note: contains an absolute-import fallback (from md_tables import ...) aimed at direct execution/special environments.

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

<a id="help_viewer_impl.api-for-module-help_core-py"></a>

### API for module help_core.py (EN)

---

<a id="help_core.part-ii-internal-maintenance-api-related-to-this-module"></a>

#### Part II — Internal / maintenance API (related to this module)

> This part is for maintenance: understanding the module, decisions, and safe change points.
> It is not intended for integrators.

<a id="help_core.4-role-of-help_core-py-in-the-architecture"></a>

#### 4. Role of help_core.py in the architecture

This module is a **facade**: it glues the system’s pieces and offers quick paths:

- Builds HelpConfig with reasonable defaults.
- Creates and uses HelpViewer.
- Implements a modal loop (overlay) that restores the frozen frame.

It should not contain complex parsing/rendering logic: that belongs in specialized modules.

---

<a id="help_core.5-dependencies-and-imported-symbols"></a>

#### 5. Dependencies and imported symbols

This module depends on:

- Parser (reduced Markdown): _MiniMarkdown (imported from help_mini_markdown).
- Viewer: HelpViewer, HelpConfig (imported from help_viewer_impl).
- Pygame: pygame.Surface, events, clock, key repeat, etc.

**Maintenance note:** although _MiniMarkdown is imported here, this module should not expose it as part of the public integration API.
Its full documentation must live in the parser module.

---

<a id="help_core.6-relevant-implementation-details"></a>

#### 6. Relevant implementation details

<a id="help_core.6-1-modal-overlay-and-frozen-frame"></a>

##### 6.1 Modal overlay and frozen frame

ShowHelpOverlay does:

- canvas = display.copy() on entry.
- Each frame: display.blit(canvas, (0, 0)) before drawing the viewer.

This prevents artifacts and lets you “see” the frozen state under the help.

<a id="help_core.6-2-autorepeat-handling"></a>

##### 6.2 Autorepeat handling

It stores pygame.key.get_repeat() and sets pygame.key.set_repeat(250, 40) during the modal,
restoring it in finally.

**Reason:** to facilitate key navigation within the viewer without depending on the game loop.

<a id="help_core.ShowHelpOverlay-2"></a>

##### 6.3 Legacy variant of ShowHelpOverlay (commented)

The file keeps a commented “legacy/backup” variant.

- Kept as a temporary reference.
- Must not be considered API.
- If removed, do it in a separate commit so it remains traceable.

---

<a id="help_core.7-manual-testing-related-demos"></a>

#### 7. Manual testing (related demos)

This module is usually validated indirectly with demos:

- Standalone (opens a window).
- Modal overlay (F1/F2/ESC depending on the demo).
- Embedded overlay (if applicable).

---

<a id="help_core.8-known-issues-operational-notes"></a>

#### 8. Known issues / operational notes

- “Time jump” when returning from the modal (if the game uses dt).
- Relative paths for images: depend on base_dir and the images module.

---

<a id="help_core.9-history-and-compatibility"></a>

#### 9. History and compatibility

- License: MIT.
- Requirements: Python >= 3.9 and Pygame.

---

<a id="help_core.10-document-changelog"></a>

#### 10. Document changelog

---

<a id="help_core.api-for-module-help_viewer_impl-py-2"></a>

### API for module help_viewer_impl.py (EN)

---

<a id="help_viewer_impl.part-ii-internal-maintenance-api"></a>

#### Part II — Internal / maintenance API

> This part is for maintaining the project: internal structure, helpers and decisions.

<a id="help_viewer_impl.DEFAULT_STYLE"></a>

#### 6. Style (DEFAULT_STYLE and _load_style)

- DEFAULT_STYLE defines sizes, colors, and spacings (hlp_*).
- _load_style(cfg):
  1) starts from DEFAULT_STYLE
  2) if cfg.style_json_path exists: loads JSON and applies variant if needed
  3) applies cfg.style_overrides
  4) normalizes colors list→tuple
  5) applies guardrails and defaults (padding, wheel step, code pad, font scale, etc.)
  6) sets hlp_CodeBlockMode (code_line or code_block)

---

<a id="help_viewer_impl._lines"></a>

#### 7. Composition and structure of _lines

<a id="help_viewer_impl.7-1-self-blocks-input"></a>

##### 7.1 self._blocks (input)
Parser output (_MiniMarkdown.parse): list of dicts per block.

<a id="help_viewer_impl.7-2-self-lines-composition-output"></a>

##### 7.2 self._lines (composition output)
List of “renderable” dicts, with typical keys:

- y, h: vertical position in document coordinates and line/block height
- runs: list of tuples (font_key, color, text, rx) for text blitting
- clicks: list of clickable logical rectangles {x, w, href}
- additional flags: is_code, hr, type (image, table, anchor, comment, etc.)
- specific fields:
  - code: code_bg, code_bg_indent, code_bg_width, code_block_indent
  - image: surface, alt, src, w
  - table: surface, w

**Useful invariant:** draw() must be able to iterate self._lines without assuming that all entries have runs with content.

---

<a id="help_viewer_impl.draw"></a>

#### 8. Render (draw) and scroll

- draw(surface, rect):
  - surface.fill(kernel_bg, rect)
  - computes paddings (fixed vertical, lateral based on base font * scale)
  - clamps scroll according to visible_height
  - iterates _lines in the visible window and draws:
    - code backgrounds (depending on hlp_CodeBlockMode)
    - images / placeholders
    - tables
    - hr
    - text runs
    - link underline (using clicks)
  - draws scrollbar if content_height > rect.height

- Scroll:
  - _scroll is a document coordinate (px)
  - max_scroll = content_height - visible_height

---

<a id="help_viewer_impl.handle_event"></a>

#### 9. Events (handle_event) and “scroll limit”
- Wheel and keys apply clamp.
- If scroll does not change and you were already at the limit, it calls _notify_scroll_limit("top"/"bottom").
- _notify_scroll_limit applies cooldown with pygame.time.get_ticks() if configured.

---

<a id="help_viewer_impl.10-main-internal-helpers-inventory"></a>

#### 10. Main internal helpers (inventory)

> This inventory helps maintenance but is not a public contract.

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

<a id="help_viewer_impl.11-operational-notes-and-technical-debt"></a>

#### 11. Operational notes and technical debt

- There is duplicated code in the anchor marker_h case (two assignments in a row).
- There is an unused _ensure_fonts_OLD (candidate for removal in a separate cleanup).
- update(dt_ms) is empty but part of the interface.

---

<a id="help_viewer_impl.api-for-module-help_mini_markdown-py"></a>

### API for module help_mini_markdown.py (EN)

---

<a id="help_mini_markdown.part-ii-internal-maintenance-api"></a>

#### Part II — Internal / maintenance API

<a id="help_mini_markdown._MiniMarkdown"></a>

#### 1. Class _MiniMarkdown

<a id="help_mini_markdown.1-1-constructor"></a>

##### 1.1 Constructor

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

#### Parameters

- tab_size: number of spaces to expand \t during normalization.
- max_list_nesting: maximum logical nesting depth for lists.
- indent_per_level_spaces: how many spaces equal 1 list level **during parsing** (not rendering).

#### Relevant attributes (internal)

- self.tab_size
- self.max_list_nesting
- self.spaces_per_level

It also initializes regular expressions for:
- blocks: hr, headers h1..h6, ul/ol, fences ``` and detection of image/anchor/comment
- inline: ***bold+italic***, **bold**, *italic*, inline code, URLs, links `[txt](url)`

---

<a id="help_mini_markdown.2-normalize-text"></a>

#### 2. normalize(text)

<a id="help_mini_markdown.signature"></a>

##### Signature

```python
def normalize(self, text: str) -> str:
    ...
```

<a id="help_mini_markdown.description"></a>

##### Description

Normalizes newlines and tabs:
- \t → spaces according to tab_size
- \r\n and \r → \n

<a id="help_mini_markdown.returns"></a>

##### Returns

str: normalized text.

---

<a id="help_mini_markdown.3-parse-text"></a>

#### 3. parse(text)

<a id="help_mini_markdown.signature-2"></a>

##### Signature

```python
def parse(self, text: str) -> List[Dict[str, Any]]:
    ...
```

<a id="help_mini_markdown.description-2"></a>

##### Description

Converts reduced Markdown into a **list of typed blocks** (dicts).
The parser is line-based and recognizes blocks in this order (simplified):

1. Empty lines (skipped between blocks; preserved inside fences)
2. Fences ``` (open/close code block)
3. Image as a block: `![alt](src) (full line)`
4. HTML comments:
   - one line: <!-- ... -->
   - multiline: line with <!-- and closing in -->
5. HTML anchor: `<a id="label"></a>`
6. Horizontal rule: ---
7. Headings: #..######
8. Lists: ul (- or *) / ol (1.)
9. Tables: detected by md_tables.is_table_start and parsed by md_tables.parse_table
10. Paragraphs: accumulation of lines until a “break” (another block)

<a id="help_mini_markdown.emitted-block-types-dict"></a>

##### Emitted block types (dict)

> **Important:** this list describes the structure **as emitted today**; if keys change, the viewer and tests must be updated.

#### 3.1 Paragraph

```python
{"type": "p", "text": "<text>"}
```

- text: can contain internal newlines (join with \n).

#### 3.2 Headings

```python
{"type": "h1", "text": "..."}
{"type": "h2", "text": "..."}
...
{"type": "h6", "text": "..."}
```

#### 3.3 Horizontal rule

```python
{"type": "hr"}
```

#### 3.4 Code (fenced)

```python
{"type": "code", "text": "<content>"}
```

- Empty lines **inside the fence** are preserved.
- If the fence is not closed before EOF, a code block is emitted anyway.

> Note: the old rule “4 spaces → code block” was removed in this parser.

#### 3.5 Lists (ul / ol)

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

- level: computed as indent_spaces // spaces_per_level, capped at max_list_nesting - 1.
- In ol, additionally:
  - num: detected number (int)

**Comments inside lists:**
- Full-line HTML comments and multiline <!-- ... --> blocks are ignored inside lists without breaking the list.

#### 3.6 Table (table)

The exact block is built by parse_table(...) from module md_tables.

- Detected before paragraphs so it is not absorbed as text.

#### 3.7 Image (img)

```python
{"type": "img", "alt": "<alt>", "src": "<src>"}
```

- Only detected as a block if the full line matches `![...](...)`.
- Inline (inside paragraphs) is not supported.
- Inside lists is not supported (by design and by detection mechanics).

#### 3.8 Comment (comment)

```python
{"type": "comment", "text": "<text>"}
```

- One-line comment: inside of <!-- ... -->.
- Multiline comment: content stored between <!-- and -->.

> **Note:** the viewer may choose to ignore these nodes or use them as metadata.

#### 3.9 Anchor (anchor)

```python
{"type": "anchor", "id": "<label>"}
```

- Detects `<a id="label"></a>` (tolerates spaces around).

---

<a id="help_mini_markdown.4-tokenize-inline-text"></a>

#### 4. tokenize_inline(text)

<a id="help_mini_markdown.signature-3"></a>

##### Signature

```python
def tokenize_inline(self, text: str) -> List[Dict[str, Any]]:
    ...
```

<a id="help_mini_markdown.description-3"></a>

##### Description

Tokenizes text (typically the content of a p, h*, list item, etc.) into a list of “runs”
to render: each run is a dict with flags.

Tokenization follows these phases:

1. **Protect inline code** (split by backticks; code segments are kept out of emphasis/link processing)
2. Apply emphasis in normal text:
   - ***text*** → bold+italic (no strict word boundaries)
   - **text** → bold (with word boundaries to avoid false positives like price*2)
   - *text* → italic (also with boundaries)
3. Expand basic Markdown links `[text](target)` outside inline code
   - Images `![...](...)` are excluded via negative regex.
4. Auto-detect http:// / https:// URLs in normal text (not in runs already marked as link)
   - Trims typical trailing punctuation (.,;:!?)]}"')
   - Special case for ) to avoid trimming if parenthesis balance is not “extra”.

<a id="help_mini_markdown.output-format-run"></a>

##### Output format (“run”)

Each run has this form:

```python
{
  "text": "<text>",
  "bold": bool,
  "italic": bool,
  "code": bool,
  "link": bool,
  "href": "<url or ''>"
}
```

<a id="help_mini_markdown.important-rules"></a>

##### Important rules

- A run with code=True **is not** processed for emphasis or links/URLs.
- A run with link=True **is not** re-processed to detect URLs inside (avoids duplicate linking).
- Links [text](target) generate:
  - run with text=text, link=True, href=target, code=False
- Raw URLs generate:
  - run with text=url, link=True, href=url, code=False
  - trailing punctuation (if trimmed) becomes a normal run.

---

<a id="help_mini_markdown.5-maintenance-details-and-decisions"></a>

#### 5. Maintenance details and decisions

<a id="help_mini_markdown.5-1-emphasis-regex-and-word-boundaries"></a>

##### 5.1 Emphasis regex and word boundaries

- ***text*** is detected without word restrictions.
- **text** and *text* use lookbehind/lookahead to require not being adjacent to word characters.

Goal: avoid false positives like price*2.

<a id="help_mini_markdown.5-2-fenced-code-without-language"></a>

##### 5.2 Fenced code without language

- Any line starting with ``` is detected (regex: ^\s*```.*$).
- The “language” is not detected/stored.

<a id="help_mini_markdown.5-3-double-fence-closing-block-at-eof-note"></a>

##### 5.3 Double fence-closing block at EOF (note)

The code contains a duplication at the end:

```python
if in_fence and fence_buf:
    out.append({"type": "code", "text": "\n".join(fence_buf)})

if in_fence and fence_buf:
    out.append({"type": "code", "text": "\n".join(fence_buf)})
```

- This could emit **two** code blocks at EOF if a fence is left open.
- If the current behavior “does not bother” because in_fence was already cleared earlier, it still deserves review.

---

<a id="help_mini_markdown.md_tables"></a>

#### 6. Interaction with tables (md_tables)

- parse calls is_table_start(lines, i) and, if true, tries parse_table.
- If parse_table returns None, it continues normal parsing.

---

<a id="help_mini_markdown.api-for-module-md_tables-py"></a>

### API for module md_tables.py (EN)

---

<a id="md_tables.part-ii-internal-maintenance-api"></a>

#### Part II — Internal / maintenance API

<a id="md_tables.5-internal-constants"></a>

#### 5. Internal constants

```python
_ALIGN_LEFT = "left"
_ALIGN_CENTER = "center"
_ALIGN_RIGHT = "right"
```

Separator cell regex:

```python
_RE_SEPARATOR_CELL = re.compile(r"^\s*:?-{3,}:?\s*$")
```

---

<a id="md_tables.TableParseResult"></a>

#### 6. TableParseResult (dataclass)

```python
@dataclass(frozen=True)
class TableParseResult:
    # Result of parsing a table.
    #
    # Attributes:
    #   block: Dictionary with the agreed table structure.
    #   next_index: Line index from which to continue global parsing.
    block: Dict[str, Any]
    next_index: int
```

<a id="md_tables.usage"></a>

##### Usage

parse_table(...) returns an instance with:

- block: normalized table model
- next_index: index so the global parse continues from there

---

<a id="md_tables.7-is-table-start-lines-index"></a>

#### 7. is_table_start(lines, index)

<a id="md_tables.signature"></a>

##### Signature

```python
def is_table_start(lines: Sequence[str], index: int) -> bool:
    # Indicates whether a valid table block starts at lines[index].
    ...
```

<a id="md_tables.exact-rules-as-implemented"></a>

##### Exact rules (as implemented)

- Requires at least 3 lines available: index, index+1, index+2.
- header_cells = _parse_table_row(lines[index]):
  - must exist and have len >= 2.
- align = _parse_separator_row(lines[index + 1], expected_cols=len(header_cells)):
  - must exist and have exactly expected_cols.
- first_row_cells = _parse_table_row(lines[index + 2]):
  - must exist and have len >= 2.

If all are met: True; otherwise: False.

---

<a id="md_tables.8-parse-table-lines-index"></a>

#### 8. parse_table(lines, index)

<a id="md_tables.signature-2"></a>

##### Signature

```python
def parse_table(lines: Sequence[str], index: int) -> Optional[TableParseResult]:
    # Parses a table block starting at index.
    ...
```

<a id="md_tables.returned-block-contract"></a>

##### Contract of the returned block

The dict block has this **exact** schema:

```python
{
  "type": "table",
  "header": [...],           # len = ncols
  "align":  [...],           # len = ncols (body alignment)
  "rows":   [[...], ...],    # each row normalized to ncols
  "row_overflow": [bool, ...]
}
```

- header: list of strings (trimmed cells) with length ncols.
- align: list of strings ("left"|"center"|"right") with length ncols.
- rows: list of rows, each a list of strings of length ncols.
- row_overflow: list parallel to rows, True if that row had more cells than ncols.

<a id="md_tables.relevant-parsing-rules"></a>

##### Relevant parsing rules

- If is_table_start(...) fails, returns None.
- Iterates rows from i = index + 2 while:
  - line is not empty, and
  - _parse_table_row(line) returns at least 2 cells.
- Each row is normalized with _normalize_row(row_cells, ncols):
  - fills with "@" if cells are missing
  - truncates and marks overflow if there are too many
- Requires at least 1 data row (rows not empty); otherwise returns None.
- next_index is the index i where the loop stopped (first line not belonging to the table).

---

<a id="md_tables.9-internal-helpers"></a>

#### 9. Internal helpers

<a id="md_tables.9-1-parse-table-row-line"></a>

##### 9.1 _parse_table_row(line)

```python
def _parse_table_row(line: str) -> Optional[List[str]]:
    # Converts a pipe-separated line into a list of cells.
    ...
```

- Returns None if there is no | in the line.
- Does strip() and split("|").
- If there is a leading or trailing pipe, removes the associated empty element.
- Trims each cell with strip().
- If fewer than 2 cells remain, returns None.
- Does not support escaping | inside cells.

<a id="md_tables.9-2-parse-separator-row-line-expected-cols"></a>

##### 9.2 _parse_separator_row(line, expected_cols)

```python
def _parse_separator_row(line: str, expected_cols: int) -> Optional[List[str]]:
    # Parses the separator row and produces alignment per column.
    ...
```

- Uses _parse_table_row to extract cells.
- Requires len(cells) == expected_cols (strict).
- Each cell must match _RE_SEPARATOR_CELL.
- Determines alignment by colons:
  - :...: → center
  - :... → left
  - ...: → right
  - ... → left

<a id="md_tables.9-3-normalize-row-row-cells-ncols"></a>

##### 9.3 _normalize_row(row_cells, ncols)

```python
def _normalize_row(row_cells: List[str], ncols: int) -> Tuple[List[str], bool]:
    # Normalizes a row to the header column count.
    ...
```

Agreed rules (exact):

- If len(row_cells) < ncols:
  - appends "@" until complete, overflow=False
- If len(row_cells) > ncols:
  - truncates to ncols, overflow=True
- If len(row_cells) == ncols:
  - returns as-is, overflow=False

---

<a id="md_tables.10-maintenance-notes-decisions"></a>

#### 10. Maintenance notes / decisions

- **Strict detector**: requires minimum 2 columns, valid separator, and at least 1 data row.
  - Advantage: fewer false positives.
  - Drawback: some “flexible” Markdown tables will not be recognized.
- **No escaping of |**: if needed in the future, a more sophisticated row parser is required
  (and that affects compatibility).
- **"@" marker**: normalization convention; the renderer must document and respect how it represents it.

---

<a id="md_tables.11-relationship-with-other-modules"></a>

#### 11. Relationship with other modules

- help_mini_markdown.py: calls is_table_start and parse_table during block parsing.
- help_viewer_impl.py: receives type="table" blocks and passes them to the renderer.
- table_renderer.py: consumes block and row_overflow to render (including "@" marker).

---

<a id="md_tables.api-for-module-table_renderer-py"></a>

### API for module table_renderer.py (EN)

---

<a id="table_renderer.part-ii-internal-maintenance-api"></a>

#### Part II — Internal / maintenance API

<a id="table_renderer.5-internal-constants"></a>

#### 5. Internal constants

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

Allowed alignments:

```python
_ALIGN_LEFT = "left"
_ALIGN_CENTER = "center"
_ALIGN_RIGHT = "right"
```

---

<a id="table_renderer.TableRenderResult"></a>

#### 6. TableRenderResult (dataclass)

```python
@dataclass(frozen=True)
class TableRenderResult:
    """Result of rendering a table.

    Attributes:
        surface: Rendered surface with the complete table.
        width: Width in pixels.
        height: Height in pixels.
    """
    surface: pygame.Surface
    width: int
    height: int
```

---

<a id="table_renderer.7-render-table-table-block-body-font-header-font"></a>

#### 7. render_table(table_block, body_font, header_font)

<a id="table_renderer.signature"></a>

##### Signature

```python
def render_table(
    table_block: Dict[str, Any],
    body_font: pygame.font.Font,
    header_font: pygame.font.Font,
) -> TableRenderResult:
    ...
```

<a id="table_renderer.table_block"></a>

##### Input block contract (table_block)

Must comply exactly with:

```python
{
  "type": "table",
  "header": ["Col A", "Col B", ...],      # len = ncols >= 2
  "align":  ["left|center|right", ...],   # len = ncols (body only)
  "rows": [
    ["r1c1", "r1c2", ...],                # each row normalized to ncols
    ...
  ],
  "row_overflow": [False, True, ...]      # len = len(rows)
}
```

<a id="table_renderer.behavior"></a>

##### Behavior

1) Validates the block with _validate_table_block:
- If it fails, raises ValueError with a specific message.

2) Measures widths per column:
- uses header_font.size(text) for header
- uses body_font.size(text) for rows

3) Computes geometry:
- col_width = max_text_width + 2*CELL_PAD_X
- header height: header_font.get_linesize() + 2*CELL_PAD_Y
- row height: body_font.get_linesize() + 2*CELL_PAD_Y

4) Computes overflow gutter:
- If any True exists in row_overflow, creates a gutter with:
  - gutter_width = width("@") + 2*CELL_PAD_X

5) Creates the Surface:
- pygame.Surface((total_width, total_height), pygame.SRCALPHA)
- surface.fill(BODY_BG_COLOR)
- Draws header background with surface.fill(HEADER_BG_COLOR, header_rect)

6) Draws text:
- Header centered (_blit_text_centered)
- Rows according to align (_blit_text_aligned)
- If overflow in the row: draws @ centered in the gutter.

7) Draws grid and borders on top (_draw_grid):
- Outer border of table (does not include gutter)
- horizontal separator under header
- horizontal separators between rows
- vertical separators between columns
- if there is a gutter: separator line and border rectangle of the gutter

<a id="table_renderer.returns"></a>

##### Returns

TableRenderResult(surface=<Surface>, width=<int>, height=<int>)

---

<a id="table_renderer.8-private-helpers"></a>

#### 8. Private helpers

<a id="table_renderer.8-1-validate-table-block-table-block"></a>

##### 8.1 _validate_table_block(table_block)

Validates:

- type == "table"
- header is a list with len >= 2
- rows is a list with len >= 1
- align is a list with len == len(header)
- row_overflow is a list with len == len(rows)
- Each row in rows is a list with len == ncols

Normalizes:
- header_cells: str(x) per cell
- body_rows: str(x) per cell
- body_align: validates values, fallback to "left"
- overflow_flags: bool(x) per element

<a id="table_renderer.8-2-blit-text-centered"></a>

##### 8.2 _blit_text_centered(...)

- Renders text and centers it within the cell.

<a id="table_renderer.8-3-blit-text-aligned"></a>

##### 8.3 _blit_text_aligned(...)

- Simple vertical centering.
- Horizontal:
  - center: text_rect.centerx = cell_rect.centerx
  - right: text_rect.right = cell_rect.right - CELL_PAD_X
  - left: text_rect.left = cell_rect.left + CELL_PAD_X

<a id="table_renderer.8-4-draw-grid"></a>

##### 8.4 _draw_grid(...)

- Draws outer border and separators.
- If there is a gutter, draws the gutter border aligned with the table.

---

<a id="table_renderer.9-maintenance-notes"></a>

#### 9. Maintenance notes

- The fixed style is documented as an explicit decision (“NOT configurable by design”).
  If table styles are parameterized, the cleanest would be:
  - introduce a table style structure (dataclass/dict)
  - pass it from the viewer
  - keep current defaults for visual compatibility

- There is no maximum width control:
  - if needed, introduce wrapping/truncation or scaling (carefully for readability).

---

<a id="table_renderer.api-for-module-image_cache-py"></a>

### API for module image_cache.py (EN)

---

<a id="image_cache.part-ii-internal-maintenance-api"></a>

#### Part II — Internal / maintenance API

<a id="image_cache.4-internal-types"></a>

#### 4. Internal types

<a id="image_cache.SurfaceInfo"></a>

##### 4.1 SurfaceInfo

```python
SurfaceInfo = Tuple[pygame.Surface, int, int]
```

Represents:
- resulting surface (possibly scaled)
- w, h: final size

<a id="image_cache._ImageKey"></a>

##### 4.2 _ImageKey (dataclass)

```python
@dataclass(frozen=True)
class _ImageKey:
    abs_path: str
    target_width: int
```

Used as a dictionary key for the cache.

---

<a id="image_cache.ImageCache"></a>

#### 5. Class ImageCache

<a id="image_cache.5-1-constructor"></a>

##### 5.1 Constructor

```python
def __init__(self, base_dir: Optional[str] = None) -> None:
    ...
```

- base_dir is normalized with Path(base_dir).resolve().
- Cache initialized empty: Dict[_ImageKey, SurfaceInfo].

<a id="image_cache.5-2-set-base-dir-base-dir"></a>

##### 5.2 set_base_dir(base_dir)

```python
def set_base_dir(self, base_dir: Optional[str]) -> None:
    ...
```

Updates base_dir (e.g., if configuration changes).

> Design note: this method **does not** invalidate the cache.
> - If you change base_dir, some relative paths could resolve to a different file.
> - Since the cache key is abs_path (resolved) + target_width, in practice there is no collision,
>   but stale cache entries for old paths may remain.

<a id="image_cache.5-3-resolve-src-to-abs-path-src"></a>

##### 5.3 resolve_src_to_abs_path(src)

```python
def resolve_src_to_abs_path(self, src: str) -> Optional[Path]:
    ...
```

Resolves a src to an absolute Path:

- empty/whitespace src → None
- if Path(src).is_absolute() → returns that Path
- if base_dir is None and src is relative → None
- if base_dir exists → (base_dir / src).resolve()

<a id="image_cache.5-4-get-scaled-src-target-width"></a>

##### 5.4 get_scaled(src, target_width)

```python
def get_scaled(self, src: str, target_width: int) -> Optional[SurfaceInfo]:
    ...
```

Flow:

1. abs_path = resolve_src_to_abs_path(src)
   if None → returns None

2. Builds key = _ImageKey(str(abs_path), int(target_width))
   if exists in cache → returns cached

3. loaded = _load_image(abs_path)
   if fails → None

4. scaled = _scale_to_width(loaded, target_width)
   if fails → None

5. Stores in cache and returns.

---

<a id="image_cache.6-private-methods"></a>

#### 6. Private methods

<a id="image_cache.6-1-load-image-abs-path"></a>

##### 6.1 _load_image(abs_path)

```python
def _load_image(self, abs_path: Path) -> Optional[pygame.Surface]:
    ...
```

- If abs_path does not exist → None
- Loads with pygame.image.load(str(abs_path))
- Attempts convert() / convert_alpha() **only if a display is initialized**:
  - pygame.display.get_init() and pygame.display.get_surface() is not None
  - If there is alpha (surface.get_alpha() is not None or SRCALPHA flag) → convert_alpha()
  - Otherwise → convert()
  - Catches pygame.error and continues returning the surface unconverted.

Motivation: convert/convert_alpha speed up blits but require a display; without display,
the surface is still usable.

<a id="image_cache.6-2-scale-to-width-surface-target-width"></a>

##### 6.2 _scale_to_width(surface, target_width)

```python
def _scale_to_width(self, surface: pygame.Surface, target_width: int) -> Optional[SurfaceInfo]:
    ...
```

- Gets original size src_w, src_h
- If size invalid → None
- max_w = max(1, int(target_width))
- If src_w <= max_w:
  - returns (surface, src_w, src_h) without scaling
- If scaling needed:
  - scale = max_w / src_w
  - computes dst_w, dst_h (rounded)
  - tries pygame.transform.smoothscale(...)
  - if it fails, falls back to pygame.transform.scale(...)
  - returns (scaled, dst_w, dst_h)

Caught errors: ValueError, pygame.error.

---

<a id="image_cache.7-maintenance-considerations"></a>

#### 7. Maintenance considerations

<a id="image_cache.7-1-cache-policy"></a>

##### 7.1 Cache policy

- The cache stays in memory and grows with combinations (abs_path, target_width).
- If the application frequently changes the target width (resizes), it can grow quite a bit.

<a id="image_cache.7-2-recommended-minimal-changes"></a>

##### 7.2 Recommended minimal changes

- Avoid changing the contract of returning None on failure: it is key for the viewer to degrade safely.
- Keep path resolution simple (and documented).

---
> 🔙 Back to index: [INDEX_en.md](INDEX_en.md)
