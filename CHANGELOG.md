# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

---

## [0.1.2] - 2026-02-10 (Unreleased)

### Added

- **Soporte ampliado de MiniMarkdown:** tablas e imágenes (con mejoras de robustez en el parseo/render).
- **Enlaces enriquecidos:** links a web, a cabeceras internas y soporte de anclas HTML (`<a id="..."></a>`).
- **API de conveniencia:** nueva función `ShowHelpOverlay()` y demo asociada.
- **Visualizador de Markdown para examples:** herramienta `examples/view_markdown_help_core.py`..

### Changed

- **Refactor interno:** reorganización/limpieza de módulos principales (`help_core.py`, `help_mini_markdown.py`, `help_viewer_impl.py`, `__init__.py`).
- **Mejoras de render:** corrección y ajuste visual de la barra `hr` (longitud y grosor).
- **Lanzador:** añadido `main.py` y actualización de cabeceras en demos.
- **Documentación:** ampliación general, creación de índice `INDEX_es.md`, navegación en docs y versión completa en inglés (`*_en.md`), además de API Reference y nuevos documentos de overview/guía.

---

## [0.1.1] - 2025-12-19 (Publicado en PyPI)

### Fixed

- **Localización de Assets:** Corregido el acceso a recursos internos en el paquete PyPI. El archivo `beep_scroll.mp3` ahora se incluye correctamente en el *wheel*, permitiendo que las demos lo localicen en `help_core_pygame/assets/mp3/`.

### Added

- **Herramienta de diagnóstico:** Nuevo script `diagnose_help_core_pygame_assets_v2.py` para verificar la existencia de assets en instalaciones de usuario final.
- **Directorio de herramientas:** Creación de carpeta `tools/` para scripts de soporte.

### Changed

- **Metadatos:** Actualizado `pyproject.toml` y README para la nueva publicación.

---

## [0.1.0] - 2025-12-01 (Publicado en PyPI)

### Added

- Primera versión pública del paquete.
- Núcleo principal (`help_core.py`) y API pública (`open_help_standalone`, etc.).
