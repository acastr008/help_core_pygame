
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
# Manual de Usuario de *Cardumen*

(Pulse la tecla **F1** para salir)

### 1 · Introducción

*Cardumen* es un juego inspirado en el fascinante movimiento de los
peces cuando forman cardúmenes. Para convertir una mera simulación en un
juego usamos como escenario dos tipos de peces de distinto tamaño y
color conviviendo en un mismo acuario, añadiendo un reto: Separar ambos
tipos de peces a derecha e izquierda del centro del acuario usando una
mano virtual movida con el cursor del ratón. Los peces reaccionan con
vida propia, esquivan, se agrupan y huyen. Los bordes de la pantalla
hacen de paredes del acuario. Es un juego de observación, coordinación y
ritmo. Superar cada nivel requiere reflejos, precisión, estrategia y
paciencia.

### 2 · Parámetros de Ejecución

*Cardumen* puede iniciarse desde una terminal con distintos argumentos
que modifican su comportamiento.

#### 2.1 Uso general

*cardumen.py [-level=N] [-counters] [-cpu] [-help]*

#### 2.2 Opciones disponibles

-   *-level=N* → Ejecuta solo el nivel *N*.
    Si no se indica, se jugarán todos los niveles en orden.
-   *-counters* → Activa los contadores visuales laterales de peces.
-   *-cpu* → Activa el monitor de rendimiento que muestra el uso de CPU
    por frame.
-   *-help* → Muestra la ayuda básica por terminal con la lista de
    parámetros.

#### 7.3 Ejemplos

-   *cardumen.py -counters*
-   *cardumen.py -level=3 -cpu*

### 3 · Inicio y Portada

Al ejecutar el juego, aparece una **pantalla de portada** con el
logotipo y una melodía de fondo.
Es el punto de partida antes de entrar al mundo del acuario.

**Controles disponibles en la portada:**

-   **Intro / Enter** → Comienza el juego.
-   **F1** → Muestra la ayuda general del juego (Es decir, este
    documento).
-   **ESC** → Cierra el juego antes de empezar.

***Nota técnica***: *Durante esta fase el juego no utiliza aún el
sistema de niveles ni el control de estados. Es simplemente un bucle de
espera elegante y musical hasta que el jugador decida comenzar.*

*Cuando se pulsa Intro, el juego inicializa la simulación, crea los
peces y pasa al ******primer nivel******, o al nivel indicado en la
línea de comandos si se usó la opción *-level=n*.*

### 4 · Modo de Juego

Una vez dentro del acuario, el jugador controla la **mano** que se
desplaza sobre la pantalla. La posición de la mano dentro del acuario
genera comportamientos de huida en los peces. Los peces del mismo tipo
tienden a agruparse. Los peces pequeños azules huyen de los peces
grandes rojos. Estós últimos no tienen un comportamiento agresivo. No
persiguen a los peces pequeños. (Son peces vegetarianos)
El objetivo es conseguir que cada tipo de pez quede confinado en un lado
del acuario, **sin mezclas**.

Cada partida está dividida en **niveles** que van aumentando
gradualmente la dificultad:
más peces, reacciones más rápidas o cambios en la distribución inicial.

El primer nivel es un mero entrenamiento ya que su distribución inicial
facilita con un poco de suerte poder separar ambos tipos de peces en
pocos segundos.

#### 4.1 Condición de victoria

Cuando la separación es completa a ambos lados, se inicia una **cuenta
atrás** de confirmación.
Si los peces permanecen separados durante toda la cuenta atrás, el nivel
se da por **superado**.

Si alguno cruza de nuevo al lado contrario antes de terminar el tiempo,
la cuenta atrás se reinicia y hay que recomenzar la separación. Da
bastante rabia que un pececillo cruce a lado contrario y la labor del
rabillo del ojo en todo momento es imprescindible para evitar estos
contratiempos.

#### 4.2 Progresión

-   En modo normal (sin argumentos) el juego recorre **todos los
    niveles** uno tras otro.
-   En modo *-level=n*, se ejecuta sólo ese nivel y, al completarlo,
    suena la música de banda de circo para celebrarlo.

Cada nivel incluye su propia configuración de peces, velocidad, límites
y tiempo de espera entre fases, para ofrecer una **progresión fluida**
de reto y descanso.

### 5 · Controles del Juego

El manejo en *Cardumen* es tan sencillo como intuitivo. Todo el control
se basa en el movimiento del ratón y unas pocas teclas especiales.

#### 5.1 Movimiento principal

-   **Ratón** → Controla la posición de la mano virtual.
    La mano se mueve con suavidad y responde incluso cuando el cursor
    real del sistema sale de la ventana, evitando que se "enganche" en
    los bordes.

#### 5.2 Teclas de control

-   **ESC** → Interrumpe el juego en cualquier momento.
    Si se pulsa durante un nivel, se produce una salida ordenada: se
    detiene la música, suena el efecto de despedida y el programa
    termina.
-   **F1** → Muestra la ayuda del juego (este manual).
-   **Intro / Enter** → Usado tanto en la portada como en algunos
    diálogos de confirmación para continuar.
-   **F2** (si está habilitado) → Puede activar o desactivar la
    visualización de contadores laterales o el monitor de CPU, según la
    configuración.

### 6 · Requisitos Técnicos

#### 6.1 Entorno recomendado

-   **Sistema operativo:** Linux o Windows con Python 3.10+.
-   **Bibliotecas:** requiere *pygame* y módulos estándar de Python.
-   **Resolución mínima:** 1024×768 píxeles.
-   **Dispositivo de entrada:** ratón.
-   **Audio:** salida estéreo o auriculares.

#### 6.2 Instalación

*pip install pygame*

#### 6.3 Estructura típica del proyecto

*cardumen/*

*├── cardumen.py # Programa principal*
*├── game_state.py # Máquina de estados*
*├── Pzes.py # Clases de peces*
*├── Pzes_IzqDecha.py # Contadores laterales*
*├── sonidos.py # Sonido y música*
*├── varglob.py # Configuración global*
*├── levels.py # Generador de niveles*
*└── recursos/ # Imágenes y efectos*

### 7 · Créditos y Licencia

**Autor:** Antonio Castro Snurmacher

Agradecimientos:

Python --- lenguaje principal.

Pygame --- motor de gráficos y sonido.

**Licencia:** uso educativo y no comercial, manteniendo la autoría
visible.

(Pulse la tecla **F1** para salir)

### 





# Test de Markdown reducido — PygamePopupForm help()

Este documento prueba **todas** las marcas soportadas: encabezados (H1/H2/H3), **negrita**, *itálica*, mezcla ***negrita+itálica***, `código inline`, listas (• y 1.), reglas horizontales, URLs como https://www.pygame.org/docs/, y bloques de código (``` y 4 espacios).

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

Nada más.




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


