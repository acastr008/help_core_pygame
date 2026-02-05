# examples — demos y utilidades

Este directorio contiene **demos ejecutables** y una **herramienta de visualización** para probar y mostrar el uso de `help_core_pygame` en aplicaciones Pygame.

> README generado automáticamente: 2026-02-05 07:46 CET

---

## Requisitos

- Python 3.11+ (en el proyecto se menciona 3.11; si usas 3.12 también debería funcionar)
- `pygame`
- `help_core_pygame` disponible en el `PYTHONPATH` (instalado o en modo editable)

> Nota: al ejecutar, es normal ver mensajes de Pygame del estilo “Hello from the pygame community”.

---

## Contenido del directorio

### 1) `demo_help_overlay_beep.py`

Demo **embebida** (overlay) usando `HelpViewer` directamente:

- Aplicación de dibujo con ratón.
- `F1` abre/cierra la ayuda como overlay **sin salir** del programa.
- Reproduce un *beep* cuando se alcanza el límite de scroll (arriba/abajo).
- Carga el sonido desde assets empaquetados usando `importlib.resources.as_file()`.

Ejecutar:

```bash
python3 examples/demo_help_overlay_beep.py
```

Controles:

- Ratón izquierdo: dibujar
- Ratón derecho: borrar lienzo
- `F1`: abrir/cerrar ayuda
- `ESC`: salir

---

### 2) `demo_help_show_overlay_circles.py`

Demo de `ShowHelpOverlay()` invocable desde una aplicación ya en ejecución:

- Animación con círculos rebotando (la simulación **continúa** tras cerrar la ayuda).
- `F1` abre/cierra el overlay modal de ayuda.
- `SPACE` alterna el tamaño de los círculos.
- `ESC` sale de la demo.

Ejecutar:

```bash
python3 examples/demo_help_show_overlay_circles.py
```

---

### 3) `demo_help_standalone.py`

Demo **standalone** usando `open_help_standalone()`:

- Abre una ventana de ayuda con un texto Markdown de prueba.
- Reproduce un *beep* al llegar a los límites del scroll.
- Carga el sonido desde el paquete (`assets/mp3/beep_scroll.mp3`) con `importlib.resources.as_file()`.

Ejecutar:

```bash
python3 examples/demo_help_standalone.py
```

---

### 4) `demo_mini_MarkDown_TEST.py`

Batería de pruebas “en vivo” del subconjunto de Markdown implementado (parser + viewer):

Incluye pruebas de:

- Encabezados, párrafos, énfasis e inline code
- Links (Markdown y autolink por URL)
- Listas (UL/OL con anidamiento)
- Bloques de código con fences
- Línea horizontal
- Comentarios HTML (una línea / multilínea) y modo debug con `F2`
- Anclas HTML en línea completa
- Imágenes como bloques (rutas relativas/absolutas, fichero inexistente)
- Tablas (incluyendo casos negativos y filas con celdas de más/menos)

Ejecutar:

```bash
python3 examples/demo_mini_MarkDown_TEST.py
```

Notas sobre imágenes:

- El `TEST_MD` referencia imágenes bajo `examples/images/...`.
- Se pasa `base_dir=os.path.dirname(__file__)` a `open_help_standalone()` para que las rutas relativas se resuelvan desde el directorio `examples/`.
- También copia `images/batman_mini.png` a `/tmp/` para probar un caso de ruta absoluta.

---

### 5) `view_markdown_help_core.py`

Utilidad para abrir **cualquier** fichero `.md` con `open_help_standalone()` resolviendo rutas relativas desde el directorio del propio `.md`.

Uso:

```bash
python3 examples/view_markdown_help_core.py RUTA/AL/FICHERO.md
```

Opciones:

- `--size ANCHOxALTO` (por defecto `1200x900`)
- `--title "Título"` (por defecto: nombre del fichero)
- `--cooldown-ms N` (por defecto `300`)

Ejemplos:

```bash
python3 examples/view_markdown_help_core.py docs/TUTORIAL.md
python3 examples/view_markdown_help_core.py docs/TUTORIAL.md --size 1400x900
python3 examples/view_markdown_help_core.py docs/TUTORIAL.md --title "Mi ayuda" --cooldown-ms 250
```

---

## Consejos rápidos

- Si algo falla al importar `help_core_pygame`, revisa que:
  - estés en el entorno virtual correcto,
  - el paquete esté instalado (o editable) y disponible en `PYTHONPATH`.
- Si el audio no está disponible (SDL/mixer), las demos deberían seguir funcionando sin beep; se mostrará una advertencia.
- Si quieres probar **solo** el renderizado de un `.md` del proyecto, usa `view_markdown_help_core.py` (es la forma más directa).

---

## Licencia

Estos ejemplos están bajo licencia **MIT** (ver cabeceras de los ficheros fuente).
