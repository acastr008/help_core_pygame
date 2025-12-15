
########## Copyright (c) ##########################################################
# SPDX-FileCopyrightText: 2025 Antonio Castro Snurmacher <acastro0841@gmail.com>
# SPDX-License-Identifier: MIT
###################################################################################


# demos/demo_help_standalone.py
# Descripción breve: Demo del módulo help_core.py Por sí solo al margen de PopupWindow.

import os
import pygame
from help_core_pygame import open_help_standalone


TEST_MD="""
# Ayuda para *demo_help_standalone* 

(Pulse la tecla **F1** para salir)

### 1 · Descripción del Programa: *demo_help_standalone.py*
Este programa es una demostración autónoma del módulo *help_core_pygame* (una librería de ayuda o documentación para aplicaciones Pygame). 
Su función principal es mostrar cómo se renderiza y se presenta un texto de ayuda formateado en Markdown reducido dentro de una ventana sin depender de otros componentes de interfaz de usuario.
Muestra la forma más sencilla de invocar la funcionalidad de ayuda (open_help_standalone) directamente desde una aplicación Pygame, sin necesidad de encapsularla en un widget o ventana emergente más complejo.

### 2 . Prueba de Configuración: 
Permite probar varias opciones de configuración del motor de renderizado, como el tamaño de la ventana (size), el fondo (kernel_bg), el manejo de la indentación (indent_spaces_per_level, visual_indent_px) y el comportamiento al límite del desplazamiento (on_scroll_limit, scroll_limit_cooldown_ms).


---

# Test de Markdown reducido — help_core_pygame

Este documento prueba las marcas soportadas en este subconjunto de markdown soportado por help_core_pygame: 
- Encabezados (H1/H2/H3) 
- **Megrita**
- *Itálica*
- Mezcla ***negrita+itálica***
- `Código inline`
- Listas (viñetas OL • y numeradas UL 1.)
- Líneas separadoras horizontale horizontales
- URLs como https://www.pygame.org/docs/ (solo cambia el color de negro a azul)
- Bloques de código (fenced) (``` y 4 espacios). Se muestra resaltado sobre un rectángulo más claro.

Sugerencia para la prueba: usar indent_per_level=2 y tab_size=4.

---

## 1. Encabezados (H2)

Texto normal bajo H2. Debe aplicar espaciados verticales superiores e inferiores.

### 1.1. Subtítulo (H3)

Línea tras H3. Comprobar interlineado (hlp_LineHeightPct) y que **negrita** / *itálica* funcionen aquí también.

Párrafo con énfasis mixto:
- Solo **negrita**.
- Solo *itálica*.
- Combinado ***negrita+itálica*** en una misma palabra.
- Asteriscos literales: este*texto no debería activar itálica dentro*de*palabras*.
- Inline code con asteriscos: `**esto no es negrita**` y con tildes: `áéíóú`.

Separador:

---

## 2. Listas

### 2.1. Viñetas (UL)

- Nivel 0, ítem A con una línea muy muy larga que debería envolver sin partir palabras, para comprobar el wrapping alrededor del ancho disponible en el rect del kernel. Repite varias palabras para forzar el salto y verificar que no se corta ninguna palabra en el proceso.
  - Nivel 1, ítem B (indentado con 2 espacios).
    - Nivel 2, ítem C. Contiene `inline code` y **negrita**.
      - Nivel 3, ítem D. Profundidad máxima recomendada.
        - Nivel 4, ítem E. Si max_list_nesting es 4, este debería "quedarse" al nivel permitido.

* Otra rama con asterisco como marcador.
  * Subnivel con asterisco.
    * Sub-subnivel.

### 2.2. Numeradas (OL)

1. Ítem 1
2. Ítem 2 con una oración larga que debe partir por espacios y no cortar palabras. También contiene un enlace: http://example.com/test?param=1#anchor
3. Ítem 3
   1. Subítem 3.1
   2. Subítem 3.2 con *itálica* y `inline code`.
      1. Subítem 3.2.1 profundo
4. Ítem 4 empezando en número mayor (solo ver que se renderiza el índice literal).

---

## 3. Código

### 3.1. Código en bloque (fenced)

```python
# Comentario: este bloque está dentro de triple backtick.
import pygame

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 30))  # azul muy oscuro
        pygame.display.flip()

```

Fin de la ayuda. (Pulse la tecla **F1** para salir)




"""

# ----------------------------------------------------------------------
# 1. Obtener la ruta del directorio del script actual (examples/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Definir la ruta base del proyecto subiendo un nivel
# Esto asume que el directorio 'examples' está en la raíz del proyecto
PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')
# ----------------------------------------------------------------------

def main() -> None:
    pygame.init()

    try:
        # Construir la ruta absoluta al asset, basándose en la nueva estructura
        asset_path = os.path.join(PROJECT_ROOT, "src", "help_core_pygame", "assets", "mp3", "beep_scroll.mp3")
        beep_sound = pygame.mixer.Sound(asset_path)
    except pygame.error as exc:
        print(f"Error cargando 'mp3/beep_scroll.mp3' en demo_help_standalone: {exc}")
        beep_sound = None

    def beep_on_limit(_where: str) -> None:
        if beep_sound is not None:
            beep_sound.play()

    # Si quieres usar tus TTF/JSON de estilos, pásalos aquí:
    open_help_standalone(
        TEST_MD,
        title="Demo Help Standalone",
        size=(1200, 900),
        # style_json_path="popup_gui/Style_Popup_Dialog_Py.json",
        # style_variant="formal",
        # fonts_dir="fonts",
        # help_font_file="DejaVuSans.ttf",
        # help_code_font_file="DejaVuSansMono.ttf",
        indent_spaces_per_level=2,
        visual_indent_px=24,
        wheel_step=48,
        kernel_bg=(222, 222, 222),
        on_scroll_limit=beep_on_limit,
        scroll_limit_cooldown_ms=300,
    )


if __name__ == "__main__":
    main()


