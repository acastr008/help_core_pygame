# 💡 help_core_pygame: Visor de Ayuda Markdown Independiente (Pygame)

> Versión en inglés: **[README.md](README.md)**

![Licencia MIT](https://img.shields.io/badge/License-MIT-green.svg)

## 🚀 Visión General

`help_core_pygame` es una librería de Python diseñada para ofrecer una **solución de visualización de ayuda altamente portátil e independiente**, basada únicamente en **Pygame**.

Permite renderizar texto con formato **Markdown reducido** directamente en una ventana *standalone* o en cualquier superficie de Pygame, sin depender de librerías de interfaz gráfica complejas.

### Uso Principal

Es la solución ideal para proyectos de Pygame que necesitan una pantalla de ayuda profesionalmente formateada, que incluya listas, código y estilos (negrita, itálica), con funcionalidad de **scroll** completa y manejo de eventos.  
El contenido de la ayuda deberá ser proporcionado en formato texto Markdown. El soporte Markdown no es completo pero es suficiente para proporcionar ayudas vistosas y bien estructuradas.

---

## 📚 Documentación

**Índice de toda la documentación del proyecto en español.**: [docs/INDEX_es.md](docs/INDEX_es.md)

---

## 🧭 Lanzador de ejemplos (main.py)

En la raíz del proyecto hay un lanzador para ejecutar las demos de `examples/`.

### Ejecutar

```bash
python3 main.py
```

### Qué scripts aparecen en el menú

El lanzador **solo** lista scripts que cumplan:

1) **Extensión**: debe terminar en `.py`  
2) **Ruta**: el path relativo debe empezar por algún prefijo de `PATH_INCLUDE` (lista en `main.py`)  
3) **Cabecera**: debe existir una línea `Descripción breve:` en la cabecera del script

Esto permite mantener en `examples/` scripts auxiliares que no se quieren listar como demos.

---

## ✨ Características Destacadas

* **Sin Dependencias Externas Complejas:** Basado únicamente en Pygame, lo que garantiza una máxima portabilidad.
* **Soporte Markdown Reducido:** Maneja los elementos más esenciales para la documentación: encabezados (`#`), párrafos, listas (`-`, `1.`), código inline (`` `código` ``) y bloques de código *fenced* (```).
* **Modo Standalone (Ventana Propia):** Incluye la función `open_help_standalone` para abrir una ventana dedicada con un bucle de eventos propio (cierre con `ESC` o `QUIT`).
* **Modo Embebido:** Permite integrar el `HelpViewer` en un `pygame.Surface` y gestionar sus eventos (`handle_event`) en tu propio bucle.
* **Scroll Avanzado:** Soporte completo para scroll con rueda del ratón, arrastre de la barra de scroll (`thumb`) y teclas (`PgUp/PgDn`, `Home/End`).
* **Notificación de Límites:** Permite definir un *callback* (`on_scroll_limit`) para notificar cuando el scroll llega al tope superior o inferior, con un *cooldown* configurable para evitar rebotes (ideal para reproducir sonidos de límite, como el `beep_scroll.mp3`).

---

## 📦 Instalación

### Opción A) Instalar desde PyPI (pendiente)

> **Nota:** La subida a PyPI de esta versión está **pendiente**.  
> Cuando esté publicada, aquí se documentará el comando `pip install ...`.

### Opción B) Instalar desde el repositorio (recomendado mientras tanto)

Clona el repositorio y usa instalación editable:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -e .
```

Requisito: necesitas `pygame` (se instalará vía dependencias si está declarado, o instálalo manualmente si tu entorno lo requiere).

---

# 1) Ejemplo de uso para el modo Standalone

El siguiente ejemplo muestra cómo iniciar el visor de ayuda **en su propia ventana** y cómo configurar el callback de límite de scroll con un sonido, asumiendo que el archivo de ayuda se llama `mi_ayuda.md` y que el archivo de sonido (`beep_scroll.mp3`) está disponible en tu sistema.

En `examples/demo_help_standalone.py` tienes una demo completa. Lo que sigue es la explicación del uso del módulo `help_core_pygame` en la modalidad Standalone.

```python
import pygame
from help_core_pygame import open_help_standalone

# Inicializa Pygame (esencial para usar el visor)
pygame.init()

# 1. Lee el contenido Markdown
try:
    MD_TEXT = open("mi_ayuda.md", encoding="utf-8").read()
except FileNotFoundError:
    MD_TEXT = "# Error\nArchivo de ayuda no encontrado."

# 2. Prepara el sonido para el límite de scroll
try:
    # Ajusta esta ruta a donde tengas el asset en tu proyecto.
    beep_sound = pygame.mixer.Sound("beep_scroll.mp3")
except pygame.error:
    print("Advertencia: No se pudo cargar el archivo de sonido 'beep_scroll.mp3'.")
    beep_sound = None

# 3. Define el callback de límite
def beep_on_limit(where: str) -> None:
    """Se llama al llegar al límite de scroll (top/bottom)."""
    print(f"Límite de scroll alcanzado: {where}")
    if beep_sound is not None:
        beep_sound.play()

# 4. Llama a la función standalone
open_help_standalone(
    md_text=MD_TEXT,
    title="Ayuda de mi Aplicación",
    size=(1200, 900),
    wheel_step=48,
    kernel_bg=(222, 222, 222),
    on_scroll_limit=beep_on_limit,
    scroll_limit_cooldown_ms=300,
)

pygame.quit()
```

# 2) Ejemplo de uso en ventana principal (Modo overlay)

Se proporciona una demo en `examples/demo_help_overlay_beep.py`.

Se usará sobre un programita de ejemplo que consiste en dibujar **en la ventana principal**. La ayuda en este ejemplo se activará pulsando `F1` y se mostrará en la propia ventana principal del programa.

Usa el modo embebido de `HelpViewer` (no `open_help_standalone`). Al salir de la ayuda se recupera el contenido de la pantalla y se puede continuar dibujando.

> Para un mapa completo de ejemplos y qué valida cada uno, ver: [docs/OVERVIEW_es.md](docs/OVERVIEW_es.md)
