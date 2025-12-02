# 💡 help_core_pygame: Visor de Ayuda Markdown Independiente (Pygame)

![Licencia MIT](https://img.shields.io/badge/License-MIT-green.svg)

## 🚀 Visión General

`help_core_pygame` es una librería de Python diseñada para ofrecer una **solución de visualización de ayuda altamente portátil e independiente**, basada únicamente en **Pygame**.

Permite renderizar texto con formato **Markdown reducido** directamente en una ventana *standalone* o en cualquier superficie de Pygame, sin depender de librerías de interfaz gráfica complejas.

### Uso Principal

Es la solución ideal para proyectos de Pygame que necesitan una pantalla de ayuda profesionalmente formateada, que incluya listas, código y estilos (negrita, itálica), con funcionalidad de **scroll** completa y manejo de eventos.
El contenido de la ayuda deberá ser proporcionado en formato texto markdown. El soporte markdown no es completo pero es  suficiente para proporcionar ayudas vistosas y bien estructuradas.

## ✨ Características Destacadas

* **Sin Dependencias Externas Complejas:** Basado únicamente en Pygame, lo que garantiza una máxima portabilidad.
* **Soporte Markdown Reducido:** Maneja los elementos más esenciales para la documentación: encabezados (`#`), párrafos, listas (`-`, `1.`), código inline (`` `código` ``) y bloques de código *fenced* (```).
* **Modo Standalone (Ventana Propia):** Incluye la función `open_help_standalone` para abrir una ventana dedicada con un bucle de eventos propio (cierre con `ESC` o `QUIT`).
* **Modo Embebido:** Permite integrar el `HelpViewer` en un `pygame.Surface` y gestionar sus eventos (`handle_event`) en tu propio bucle.
* **Scroll Avanzado:** Soporte completo para scroll con rueda del ratón, arrastre de la barra de scroll (`thumb`) y teclas (`PgUp/PgDn`, `Home/End`).
* **Notificación de Límites:** Permite definir un *callback* (`on_scroll_limit`) para notificar cuando el scroll llega al tope superior o inferior, con un *cooldown* configurable para evitar rebotes (ideal para reproducir sonidos de límite, como el `beep_scroll.mp3`).

## 📦 Instalación

El paquete está disponible en PyPI:

```bash
# Nota: El nombre del paquete es el del proyecto, help_core_pygame, en formato pip.
pip install help-core-pygame
Requisito: Necesitas tener pygame instalado en tu entorno.
```

# 1) Ejemplo de uso para el modo Standalone:

El siguiente ejemplo muestra cómo iniciar el visor de ayuda **en su propia ventana** y cómo configurar el callback de límite de scroll con un sonido, asumiendo que el archivo de ayuda se llama mi_ayuda.md y que el archivo de sonido (beep_scroll.mp3) está disponible en tu sistema.
En examples/demo_help_standalone.py tiene una demo completa. Lo que sigue es la explicación del uso del módulo help_core_pygame en la modalidad Standalone.

```Python
import pygame
# El nombre del módulo que hay que importar es help_core_pygame.
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
    # Por simplicidad, asumimos que está en la misma carpeta que el script de prueba.
    beep_sound = pygame.mixer.Sound("beep_scroll.mp3") 
except pygame.error:
    print("Advertencia: No se pudo cargar el archivo de sonido 'beep_scroll.mp3'.")
    beep_sound = None

# 3. Define el callback de límite
def beep_on_limit(where: str) -> None:
    """Función que se llama al llegar al límite de scroll (top/bottom)."""
    print(f"Límite de scroll alcanzado: {where}")
    if beep_sound is not None:
        beep_sound.play()

# 4. Llama a la función standalone
open_help_standalone(
    md_text=MD_TEXT,
    title="Ayuda de mi Aplicación",
    size=(1200, 900),
    wheel_step=48,
    kernel_bg=(222, 222, 222),  # Fondo gris claro
    on_scroll_limit=beep_on_limit,
    scroll_limit_cooldown_ms=300, # Antirrebote de 300 ms
)

# Cierre de Pygame al finalizar
pygame.quit()
```

# 2) Ejemplo de uso para el modo embebido en una ventana (Modo overlay):

Se proporciona una demo en examples/demo_help_overlay_beep.py.  Se usará sobre un programita de ejemplo que consiste en dibujar **en la ventana principal**. (Se ha elejido dibujar por su sencillez y por incluir cierta gestión de eventos).  La ayuda en este ejemplo se activará pulsando F1 y se mostrará en la propia ventana principal del programa.  Usa el modo embebido de `HelpViewer` (no `open_help_standalone`). Al salir de la ayuda se recupera el contenido de la pantalla y se puede continuar dibujando.
