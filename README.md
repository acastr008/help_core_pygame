# 💡 help_core_pygame: Standalone Markdown Help Viewer (Pygame)

> Spanish version: **[README_es.md](README_es.md)**

![MIT License](https://img.shields.io/badge/License-MIT-green.svg)

## 🚀 Overview

`help_core_pygame` is a Python library designed to provide a **highly portable and self-contained help viewer** based only on **Pygame**.

It can render **reduced Markdown** text in a *standalone* window or directly onto any Pygame surface, without relying on heavyweight GUI frameworks.

### Primary Use Case

Ideal for Pygame projects that need a professionally formatted help screen (headings, lists, code, basic styling), with full **scroll** support and event handling.  
Help content is provided as Markdown text. Markdown support is intentionally limited but sufficient for structured, good-looking help screens.

---

## 📚 Documentation

**Index of the complete project documentation**: [docs/INDEX_en.md](docs/INDEX_en.md)

---

## 🧭 Examples launcher (main.py)

A launcher is provided in the project root to run the scripts under `examples/`.

### Run

```bash
python3 main.py
```

### Which scripts are listed

The launcher only lists scripts that match:

1) **Extension**: must end with `.py`  
2) **Path**: the relative path must start with one of the prefixes in `PATH_INCLUDE` (a list defined in `main.py`)  
3) **Header**: the script must contain a `Descripción breve:` line in its header

This makes it possible to keep helper scripts in `examples/` without listing them as demos.

---

## ✨ Highlights

- **No heavy dependencies**: only Pygame.
- **Reduced Markdown support**: headings (`#`), paragraphs, lists (`-`, `1.`), inline code (`` `code` ``) and fenced code blocks (```).
- **Standalone mode**: `open_help_standalone` opens a dedicated window with its own event loop.
- **Embedded mode**: integrate `HelpViewer` into your own screen/surface and handle events via `handle_event`.
- **Smooth scrolling**: mouse wheel and keyboard support (implementation details may vary by demo/style).
- **Scroll limit callback**: `on_scroll_limit` can be used to trigger feedback (e.g., a sound) when reaching top/bottom.

---

## 📦 Installation

### Option A) Install from PyPI (pending)

> **Note:** this version is not published on PyPI yet.  
> Once published, this section will include the final `pip install ...` command.

### Option B) Install from the repository (recommended for now)

Clone the repository and install in editable mode:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -e .
```

You need `pygame` (it will be installed via declared dependencies if available, or install it manually if your environment requires it).

---

# 1) Standalone usage example

A complete demo is available at `examples/demo_help_standalone.py`.  
Below is a minimal standalone usage example:

```python
import pygame
from help_core_pygame import open_help_standalone

pygame.init()

try:
    MD_TEXT = open("my_help.md", encoding="utf-8").read()
except FileNotFoundError:
    MD_TEXT = "# Error\nHelp file not found."

try:
    beep_sound = pygame.mixer.Sound("beep_scroll.mp3")
except pygame.error:
    print("Warning: could not load 'beep_scroll.mp3'.")
    beep_sound = None


def beep_on_limit(where: str) -> None:
    """Called when the scroll limit is reached (top/bottom)."""
    print(f"Scroll limit reached: {where}")
    if beep_sound is not None:
        beep_sound.play()


open_help_standalone(
    md_text=MD_TEXT,
    title="My App Help",
    size=(1200, 900),
    wheel_step=48,
    kernel_bg=(222, 222, 222),
    on_scroll_limit=beep_on_limit,
    scroll_limit_cooldown_ms=300,
)

pygame.quit()
```

# 2) Overlay example (in your main window)

A complete demo is provided at `examples/demo_help_overlay_beep.py`.

In this mode the help viewer is displayed on top of your main window (overlay/modal). When you exit the help screen, your game continues normally.

> For a map of examples and what each one validates, see: [docs/OVERVIEW_es.md](docs/OVERVIEW_es.md)
