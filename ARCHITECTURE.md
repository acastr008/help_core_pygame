# 🏛️ Arquitectura del Proyecto `help-core-pygame` (v0.1.0)

Este documento describe la estructura modular, los componentes clave y el flujo de datos dentro de la librería `help_core_pygame`, un visor de ayuda Markdown independiente basado en Pygame.

---

## 1. 🏗️ Estructura del Directorio Principal

El proyecto sigue el **Layout de Estructura de Origen (`src/`)**, una práctica moderna para el empaquetado de Python.

| Directorio/Archivo | Propósito |
| :--- | :--- |
| `src/` | **Contenedor del Código Fuente:** Contiene el código fuente importable y los *assets* necesarios para el paquete PyPI. |
| `src/help_core_pygame/` | **Paquete Python Importable:** Este es el paquete que se importa (`import help_core_pygame`). |
| `examples/` | Scripts de demostración para el usuario y el desarrollo (`demo_help_standalone.py`, `demo_help_overlay_beep.py`). |
| `docs/` | Documentación técnica y guía de API para el desarrollador. |
| `pyproject.toml` | **Configuración del Proyecto:** Define los metadatos, dependencias (`pygame>=2.0`) y la configuración de *build* (`setuptools`) para el *layout* `src/`. |
| `README_ES.md / README_EN.md` | Documentación de alto nivel para el usuario final. |
| `TASKS.md` | Lista de tareas pendientes y *roadmap* del proyecto. |
| `AI_GUIDE.md` / `AI_EXCLUDE.txt` | Contexto de uso para herramientas de IA (ej. Gemini CLI). |

---

## 2. 🧩 Componentes Modulares del Paquete

El corazón funcional de la librería reside en `src/help_core_pygame/`.

### A. Módulos Clave

| Módulo | Componentes Principales | Responsabilidad |
| :--- | :--- | :--- |
| `help_core.py` | `HelpConfig`, `HelpViewer`, `_MiniMarkdown` (internal) | **Lógica Central:** Contiene la implementación del *parser* Markdown, el compositor de la vista de líneas (`_compose_all`), el manejo del *scroll* y la lógica de dibujo. **Es el módulo más complejo.** |
| `__init__.py` | Re-exportaciones (`from .help_core import ...`) | **API Pública:** Define qué funciones (`open_help_standalone`) y clases (`HelpConfig`, `HelpViewer`) son directamente accesibles desde el nivel superior del paquete (`help_core_pygame`). |

### B. Assets

* `assets/mp3/beep_scroll.mp3`: Archivo de sonido utilizado en las demos como *feedback* para el *callback* de límite de *scroll* (`on_scroll_limit`).
    * **Nota:** Los *assets* están incluidos en el paquete PyPI a través de la configuración `[tool.setuptools.package-data]` en `pyproject.toml`.

---

## 3. 🔄 Flujo de Datos y Abstracciones

La arquitectura se centra en un flujo de procesamiento de tres etapas dentro del componente `HelpViewer`, que encapsula la lógica de la Interfaz de Usuario (IU).

### A. Clases de Configuración y Abstracción

* **`HelpConfig` (Clase de Datos):** Contiene todos los parámetros estáticos necesarios para renderizar la ayuda (el texto Markdown, el tamaño de la ventana, el *kernel_bg*, los parámetros del *parser*, y los *callbacks*). Es la interfaz de configuración del usuario.
* **`HelpViewer` (Clase de Lógica):** La clase principal que gestiona el estado del visor (scroll actual, posición del *thumb*), procesa el texto, maneja los eventos de Pygame y realiza el dibujo.

### B. Flujo del Pipeline de Renderizado

1.  **Entrada:** Texto Markdown (`md_text` pasado a `HelpConfig`).
2.  **Parser (`_MiniMarkdown`):** Recorre el `md_text` línea por línea, lo convierte en una lista de **Bloques Lógicos** (párrafos, encabezados, listas, código). Estos son las unidades de contenido.
3.  **Composición (`_compose_all`):** Toma los Bloques Lógicos y genera una lista de **Líneas Físicas** (renderizables). Esta etapa:
    * Calcula la altura y posición `y` de cada línea.
    * Determina los *runs* de texto (qué fuente, color, y posición `x` relativa debe tener cada fragmento dentro de la línea).
    * Define la **Altura Total del Contenido** (`_content_height`).
4.  **Dibujo (`draw()`):** Dibuja la parte visible del documento (`_lines`) en la superficie de Pygame, aplicando el desplazamiento vertical definido por la variable de estado `self._scroll`.
5.  **Interacción (`handle_event()`):** Procesa eventos del ratón (rueda para *scroll*, arrastre del *thumb*), teclado y ejecuta el *callback* `on_scroll_limit` si se alcanzan los límites del contenido. 

### C. Modos de Uso

| Modo | Función de Entrada | Bucle de Eventos |
| :--- | :--- | :--- |
| **Standalone** | `open_help_standalone()` | **Interno:** La función toma el control del bucle de Pygame y gestiona la ventana hasta que el usuario pulsa `ESC` o cierra la ventana. |
| **Embebido** | `HelpViewer` (instancia) | **Externo:** El usuario debe llamar a `viewer.handle_event(event)` y `viewer.draw(surface)` dentro de su propio bucle principal. |

