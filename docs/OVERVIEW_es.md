# OVERVIEW (help_core_pygame)

> 🔙 Volver al índice: [INDEX_es.md](INDEX_es.md)

Este documento es la **visión general** del proyecto y está pensado para lectura rápida.

---

![Sistema de ayuda en proyectos Pygame](Pulsando_F1.png)

## 1. Qué es help_core_pygame

`help_core_pygame` es una librería para mostrar pantallas de ayuda en proyectos Pygame mediante:

- un **parser** de Markdown reducido (MiniMarkdown),
- un **viewer** (visualizador) que renderiza a superficie Pygame y gestiona scroll/eventos,
- utilidades auxiliares (tablas, imágenes, caché).

### Qué resuelve

- Mostrar ayuda “bonita” (títulos, listas, código, tablas, imágenes) sin depender de GUI frameworks.
- Integración en juegos: ayuda como overlay o como ventana standalone.

### Qué NO pretende ser

- No es un motor de Markdown completo (CommonMark/GFM completo).
- No es un sistema de UI general: se centra en el caso “pantalla de ayuda”.

---

## 2. Arquitectura en una página

Pipeline simplificado:

1) **Texto MiniMarkdown** (string o fichero)
2) **Normalización** (CRLF/tabs → formato estable)
3) **Parser MiniMarkdown** → lista de **bloques** (`h1…h6`, `p`, `ul/ol`, `code`, `table`, `img`, etc.)
4) **Composición (layout)** → líneas internas renderizables (medidas, cortes, posiciones)
5) **Render (draw)** → dibuja en Pygame
6) **Interacción (handle_event)** → scroll, clicks en links, saltos a ancla, salida, modo debug

---

## 3. Modos de uso

- **Standalone**: abre una ventana propia para la ayuda.
- **Overlay / modal**: dibuja sobre tu pantalla del juego y consume eventos mientras está activo.
- **Embebido**: puedes dibujar en una superficie si tu arquitectura de juego lo requiere.

> La API exacta está en [API_REFERENCE_es.md](API_REFERENCE_es.md).  
> Aquí solo se describe el “qué” y el “cuándo”.

---

## 4. Ejemplos incluidos

La carpeta `examples/` contiene scripts de demostración y utilidades. Resumen:

| Archivo | Propósito | Qué valida / qué demuestra |
|---|---|---|
| `demo_help_overlay_beep.py` | (sin 'Descripción breve:' en cabecera) | Overlay de ayuda + feedback sonoro al llegar a límites de scroll. |
| `demo_help_show_overlay_circles.py` | (sin 'Descripción breve:' en cabecera) | Ejemplo de overlay contextual integrable en un juego (uso típico en runtime). |
| `demo_help_standalone.py` | (sin 'Descripción breve:' en cabecera) | Apertura de ayuda en ventana standalone. |
| `demo_mini_MarkDown_TEST.py` | (sin 'Descripción breve:' en cabecera) | Cobertura visual del MiniMarkdown (casos de formato y render). |
| `view_markdown_help_core.py` | (sin 'Descripción breve:' en cabecera) | Visor CLI para abrir un fichero Markdown en el viewer (utilidad de desarrollo). |

---

## 5. Estilos y personalización (visión general)

- El viewer usa un diccionario de estilo (valores `hlp_*`) con colores, fuentes, tamaños y paddings.
- Para uso normal, la ruta más segura es:
  - partir de `DEFAULT_STYLE`,
  - sobrescribir **solo** lo que necesites.

> Nota: el esquema exacto del estilo puede evolucionar. En caso de duda, usa `DEFAULT_STYLE` como base.

---

## 6. Recursos: rutas, imágenes y empaquetado

- Las imágenes en MiniMarkdown se tratan como **bloques** (`![alt](src)`).
- El viewer intenta cargar la imagen desde:
  - rutas relativas (dependiendo de `base_dir` o del directorio de trabajo),
  - rutas absolutas,
  - o assets si tu integración lo empaqueta así.
- Si una imagen no se puede cargar, el viewer muestra un **placeholder** (no rompe el render).

---

## 7. Modo depuración (debug)

El viewer incluye un modo de depuración para visualizar elementos internos útiles en mantenimiento, como:

- anclas (`<a id="..."></a>`)
- comentarios (`<!-- ... -->`)
- etiquetas auxiliares (p.ej. sobre imágenes)

Este modo es útil cuando:

- un link `#anchor` no salta donde esperas,
- quieres confirmar que el parser está emitiendo bloques correctos.

---

## 8. Resolución de problemas

### 8.1 El script no aparece en el lanzador

Según la política actual del lanzador:

- Debe ser un `*.py`
- Debe estar bajo uno de los `PATH_INCLUDE`
- Debe contener una línea `Descripción breve:` en la cabecera

### 8.2 La ayuda no se abre o se cierra “sin motivo”

- Confirma que tu loop principal sigue bombeando eventos de Pygame.
- Revisa que no estás consumiendo eventos antes de pasarlos al viewer/overlay.

### 8.3 No se ven imágenes

- Verifica la ruta `src` en `![alt](src)` y si es relativa, el `base_dir` efectivo.
- Si ves el placeholder “Image missing”, el render está funcionando: el fallo es de ruta/carga.

### 8.4 Los links externos no abren navegador

- En entornos restringidos (sandbox/kiosco) `webbrowser.open()` puede fallar.
- El viewer no debe romper por ello: se comporta como “best-effort”.

### 8.5 Tablas se ven “raras”

- Asegúrate de que la cabecera y la línea separadora existen y tienen `|`.
- Revisa alineaciones (`:---`, `---:`, `:---:`).

---

## 9. Dónde está cada cosa (mapa rápido)

- **Qué soporta MiniMarkdown**: [MINIMARKDOWN_GUIDE_es.md](MINIMARKDOWN_GUIDE_es.md)
- **Cómo usar la API** (pública y mantenimiento): [API_REFERENCE_es.md](API_REFERENCE_es.md)
- **Cómo probar visualmente**:
  - usa `examples/demo_mini_MarkDown_TEST.py` para validar el render de Markdown,
  - usa las demos de overlay/standalone para validar integración.

> 🔙 Volver al índice: [INDEX_es.md](INDEX_es.md)

