# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [0.1.1] - 2025-12-19 (Unreleased)

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
