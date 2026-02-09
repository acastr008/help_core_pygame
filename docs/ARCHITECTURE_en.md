# ARCHITECTURE (help_core_pygame)

> 🔙 Back to index: [INDEX_en.md](INDEX_en.md)

Minimalist architecture document for maintainers.

---

## 1. Repository map

- `src/help_core_pygame/`  
  Library code (parser, viewer, and auxiliary modules).
- `examples/`  
  Demos and visual validation utilities.
- `docs/`  
  Project documentation.
- `tools/`  
  Auxiliary scripts (diagnostics and utilities).

---

## 2. Main modules (conceptual view)

- `help_core.py`  
  **Public facade**: entry point to open standalone help, overlay helpers, and re-exported classes.
  It can orchestrate text loading and delegate to the viewer.

- `help_viewer_impl.py`  
  **Viewer**: layout + render + interaction.  
  Converts parser blocks into internal lines, draws on Pygame, and processes events (scroll, link clicks, anchor jumps, debug).

- `help_mini_markdown.py`  
  **MiniMarkdown parser**: normalizes and parses text into blocks (h/p/list/code/table/img/anchor/comment) and tokenizes inline
  (emphasis, inline code, links).

---

## 3. Auxiliary modules (maintenance)

- `md_tables.py`  
  Table detection and parsing (reduced GFM subset).

- `table_renderer.py`  
  Table rendering (cells, header, alignment) on Pygame surfaces.

- `image_cache.py`  
  Image cache to avoid reloads and improve performance.

- `__init__.py`  
  Re-export of the public API (what is considered stable for “normal” usage).

---

## 4. Internal pipeline (from text to screen)

1) **Input**: MiniMarkdown text (string or file).
2) **Normalization**: CRLF/tabs → stable format.
3) **Parsing (blocks)**: the parser produces a list of dicts (`type=...`).
4) **Composition (layout)**: the viewer transforms blocks into an internal list of “renderable lines”
   (with measurements, splits, rects, etc.).
5) **Render (draw)**: the viewer draws text, tables, and images onto a Pygame surface.
6) **Interaction (handle_event)**:
   - scroll (wheel/keys/drag if applicable),
   - link clicks (http(s) with `webbrowser.open`, `#anchor` for internal jumps),
   - exit/close (depending on mode),
   - debug mode (anchor/comment visualization, etc.).

---

## 5. Extension points (where to change what)

- **MiniMarkdown syntax/parsing**: `help_mini_markdown.py` (+ `md_tables.py` if tables are involved).
- **General render / layout / scroll / events**: `help_viewer_impl.py`.
- **Tables (how they look)**: `table_renderer.py` (and associated style).
- **Images / performance**: `image_cache.py` and `img` handling in `help_viewer_impl.py`.
- **Public API surface** (what is exported): `__init__.py` and the facade in `help_core.py`.

---

## 6. Maintenance principles (practical rules)

- **Minimal changes**: modify only what is needed; prefer small commits.
- **Safe degradation**: on errors (missing image, link cannot open), the viewer should not crash.
- **Visual validation**: use `examples/` to verify render and interaction changes.
  - Parser: `demo_mini_MarkDown_TEST.py`
  - Integration: standalone/overlay demos

> 🔙 Back to index: [INDEX_en.md](INDEX_en.md)
