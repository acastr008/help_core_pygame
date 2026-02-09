# OVERVIEW (help_core_pygame)

> 🔙 Back to index: [INDEX_en.md](INDEX_en.md)

This document is a **high-level overview** of the project and is meant for quick reading.

---

![Help system in Pygame projects](Pulsando_F1.png)

## 1. What is help_core_pygame

`help_core_pygame` is a library to display help screens in Pygame projects using:

- a **reduced Markdown parser** (MiniMarkdown),
- a **viewer** that renders to a Pygame surface and handles scroll/events,
- auxiliary modules (tables, images, cache).

### What it solves

- Display “nice-looking” help (headings, lists, code, tables, images) without depending on GUI frameworks.
- Game integration: help as an overlay or as a standalone window.

### What it is NOT trying to be

- It is not a complete Markdown engine (full CommonMark/GFM).
- It is not a general UI system: it focuses on the “help screen” use case.

---

## 2. One-page architecture

Simplified pipeline:

1) **MiniMarkdown text** (string or file)
2) **Normalization** (CRLF/tabs → stable format)
3) **MiniMarkdown parser** → list of **blocks** (`h1…h6`, `p`, `ul/ol`, `code`, `table`, `img`, etc.)
4) **Composition (layout)** → internal renderable lines (measurements, wrapping, positions)
5) **Render (draw)** → draws in Pygame
6) **Interaction (handle_event)** → scroll, link clicks, anchor jumps, exit, debug mode

---

## 3. Usage modes

- **Standalone**: opens a dedicated window for help.
- **Overlay / modal**: draws on top of your game screen and consumes events while active.
- **Embedded**: draws onto a surface if your game architecture requires it.

> The exact API is documented in [API_REFERENCE_en.md](API_REFERENCE_en.md).  
> This document only describes the “what” and the “when”.

---

## 4. Included examples

The `examples/` folder contains demo scripts and utilities. Summary:

| File | Purpose | What it validates / demonstrates |
|---|---|---|
| `demo_help_overlay_beep.py` | (no 'Descripción breve:' in header) | Help overlay + audible feedback when reaching scroll limits. |
| `demo_help_show_overlay_circles.py` | (no 'Descripción breve:' in header) | Contextual overlay example for in-game integration (typical runtime usage). |
| `demo_help_standalone.py` | (no 'Descripción breve:' in header) | Opening help in a standalone window. |
| `demo_mini_MarkDown_TEST.py` | (no 'Descripción breve:' in header) | Visual coverage of MiniMarkdown (format/render cases). |
| `view_markdown_help_core.py` | (no 'Descripción breve:' in header) | CLI utility to open a Markdown file in the viewer (developer utility). |

---

## 5. Styles and customization (high-level)

- The viewer uses a style dictionary (`hlp_*` keys) with colors, fonts, sizes and paddings.
- For typical usage, the safest approach is:
  - start from `DEFAULT_STYLE`,
  - override **only** what you need.

> Note: the exact style schema may evolve. When in doubt, use `DEFAULT_STYLE` as the base.

---

## 6. Assets: paths, images, packaging

- Images in MiniMarkdown are treated as **blocks** (`![alt](src)`).
- The viewer tries to load an image from:
  - relative paths (depending on `base_dir` or the working directory),
  - absolute paths,
  - or packaged assets if your integration provides them.
- If an image cannot be loaded, the viewer shows a **placeholder** (render does not break).

---

## 7. Debug mode

The viewer includes a debug mode to visualize internal elements useful for maintenance, such as:

- anchors (`<a id="..."></a>`)
- comments (`<!-- ... -->`)
- auxiliary labels (e.g., over images)

This mode is useful when:

- an internal link `#anchor` does not jump where you expect,
- you want to confirm the parser is emitting the expected blocks.

---

## 8. Problem solving

### 8.1 A script does not appear in the launcher

According to the current launcher policy:

- It must be a `*.py`
- It must be under one of the `PATH_INCLUDE` prefixes
- It must contain a `Descripción breve:` line in the header

### 8.2 Help does not open or closes “for no reason”

- Confirm your main loop is still pumping Pygame events.
- Check you are not consuming events before passing them to the viewer/overlay.

### 8.3 Images are not visible

- Check the `src` path in `![alt](src)` and, if it is relative, the effective `base_dir`.
- If you see the “Image missing” placeholder, the render is working: the issue is the load path.

### 8.4 External links do not open a browser

- In restricted environments (sandbox/kiosk), `webbrowser.open()` may fail.
- The viewer should not crash because of this: it behaves as “best-effort”.

### 8.5 Tables look “weird”

- Ensure the header row and separator line exist and contain `|`.
- Check alignments (`:---`, `---:`, `:---:`).

---

## 9. Where is everything (quick map)

- **MiniMarkdown support**: [MINIMARKDOWN_GUIDE_en.md](MINIMARKDOWN_GUIDE_en.md)
- **How to use the API** (public and maintenance): [API_REFERENCE_en.md](API_REFERENCE_en.md)
- **How to test visually**:
  - use `examples/demo_mini_MarkDown_TEST.py` to validate Markdown rendering,
  - use the overlay/standalone demos to validate integration.

> 🔙 Back to index: [INDEX_en.md](INDEX_en.md)
