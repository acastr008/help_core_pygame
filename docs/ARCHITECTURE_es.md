# ARCHITECTURE (help_core_pygame)

> 🔙 Volver al índice: [INDEX_es.md](INDEX_es.md)

Documento **minimalista** de arquitectura para mantenimiento.  

---

## 1. Mapa del repositorio

- `src/help_core_pygame/`  
  Código de librería (parser, viewer y módulos auxiliares).
- `examples/`  
  Demos y utilidades de validación visual.
- `docs/`  
  Documentación del proyecto.
- `tools/`  
  Scripts auxiliares (diagnóstico y utilidades).

---

## 2. Módulos principales (visión conceptual)

- `help_core.py`  
  **Fachada pública**: punto de entrada para abrir ayuda standalone, helpers de overlay y re-export de clases.
  Puede orquestar carga de texto y delegar en el viewer.

- `help_viewer_impl.py`  
  **Viewer**: layout + render + interacción.  
  Convierte bloques del parser en líneas internas, dibuja sobre Pygame y procesa eventos (scroll, click en links, saltos a anclas, debug).

- `help_mini_markdown.py`  
  **Parser MiniMarkdown**: normaliza y parsea el texto a bloques (h/p/list/code/table/img/anchor/comment) y tokeniza inline
  (énfasis, código inline, links).

---

## 3. Módulos auxiliares (mantenimiento)

- `md_tables.py`  
  Detección y parseo de tablas (subconjunto estilo GFM).

- `table_renderer.py`  
  Render de tablas (celdas, cabeceras, alineación) sobre superficies Pygame.

- `image_cache.py`  
  Caché de imágenes cargadas para evitar recargas y mejorar rendimiento.

- `__init__.py`  
  Re-export de la API pública (lo que se considera estable para uso “normal”).

---

## 4. Pipeline interno (de texto a pantalla)

1) **Entrada**: texto MiniMarkdown (string o fichero).
2) **Normalización**: CRLF/tabs → formato estable.
3) **Parseo (bloques)**: el parser produce una lista de dicts (`type=...`).
4) **Composición (layout)**: el viewer transforma bloques en una lista interna de “líneas renderizables”
   (con medidas, cortes, rects, etc.).
5) **Render (draw)**: el viewer dibuja las líneas, tablas e imágenes sobre una superficie Pygame.
6) **Interacción (handle_event)**:
   - scroll (rueda/teclas/drag si aplica),
   - click en links (http(s) con `webbrowser.open`, `#anchor` para salto interno),
   - salida/cierre (según modo),
   - modo debug (visualización de anclas/comentarios, etc.).

---

## 5. Puntos de extensión (dónde tocar según el cambio)

- **Sintaxis/parseo MiniMarkdown**: `help_mini_markdown.py` (+ `md_tables.py` si afecta a tablas).
- **Render general / layout / scroll / eventos**: `help_viewer_impl.py`.
- **Tablas (cómo se ven)**: `table_renderer.py` (y estilo asociado).
- **Imágenes / rendimiento**: `image_cache.py` y el manejo de `img` en `help_viewer_impl.py`.
- **API pública** (qué se exporta): `__init__.py` y fachada en `help_core.py`.

---

## 6. Principios de mantenimiento (reglas prácticas)

- **Cambios mínimos**: modificar solo lo necesario y preferir commits pequeños.
- **Degradación segura**: ante errores (imagen no encontrada, link no abrible), el viewer no debe romper.
- **Validación visual**: usar `examples/` para comprobar cambios de render e interacción.
  - Parser: `demo_mini_MarkDown_TEST.py`
  - Integración: demos standalone/overlay

> 🔙 Volver al índice: [INDEX_es.md](INDEX_es.md)
