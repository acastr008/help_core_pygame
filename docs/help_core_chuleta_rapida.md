# Chuleta rápida de `popup_gui.help_core`

Guía condensada para uso frecuente del módulo de ayuda basado en Pygame.

---

## 1. Import básico

```python
from popup_gui.help_core import HelpConfig, HelpViewer, open_help_standalone
```

---

## 2. `HelpConfig` (configuración del visor)

```python
HelpConfig(
    md_text: str,
    title: str = "Ayuda",
    size: tuple[int, int] = (800, 480),

    # Estilo / fuentes
    style_json_path: str | None = None,
    style_variant: str | None = None,
    style_overrides: dict[str, object] | None = None,
    fonts_dir: str | None = None,
    help_font_file: str | None = None,
    help_code_font_file: str | None = None,

    # Parser
    tab_size: int = 4,
    max_list_nesting: int = 6,
    indent_spaces_per_level: int = 2,
    visual_indent_px: int = 24,

    # Fondo
    kernel_bg: tuple[int, int, int] | None = None,

    # Interacción
    wheel_step: int = 48,
    on_scroll_limit: callable[[str], None] | None = None,
    scroll_limit_cooldown_ms: int = 0,
)
```

### Campos clave

| Campo                      | Tipo                    | Por defecto     | Comentario breve                                           |
|---------------------------|-------------------------|-----------------|------------------------------------------------------------|
| `md_text`                 | `str`                   | **obligatorio** | Texto de ayuda en Markdown reducido.                      |
| `title`                   | `str`                   | `"Ayuda"`       | Título de la ventana / visor.                             |
| `size`                    | `(int, int)`            | `(800, 480)`    | Tamaño de ventana (standalone) o tamaño lógico.           |
| `wheel_step`              | `int`                   | `48`            | Paso de scroll con rueda (px).                            |
| `kernel_bg`               | `RGB \| None`           | `None`          | Color de fondo del área de ayuda.                         |
| `on_scroll_limit`         | `Callable[[str], None]` | `None`          | Callback al llegar a top/bottom (`"top"` / `"bottom"`).   |
| `scroll_limit_cooldown_ms`| `int`                   | `0`             | Antirrebote de callback (ms). 0 = sin límite.             |
| `style_json_path`         | `str \| None`           | `None`          | Ruta a JSON de estilos opcional.                          |
| `style_variant`           | `str \| None`           | `None`          | Variante de estilo dentro del JSON.                       |
| `style_overrides`         | `dict \| None`          | `None`          | Overrides puntuales de claves de estilo.                  |
| `fonts_dir`               | `str \| None`           | `None`          | Directorio base para TTF.                                 |
| `help_font_file`          | `str \| None`           | `None`          | TTF para texto normal.                                    |
| `help_code_font_file`     | `str \| None`           | `None`          | TTF para código.                                          |
| `tab_size`                | `int`                   | `4`             | Espacios por tabulador.                                   |
| `max_list_nesting`        | `int`                   | `6`             | Profundidad máxima de listas.                             |
| `indent_spaces_per_level` | `int`                   | `2`             | Espacios que significan 1 nivel de lista.                 |
| `visual_indent_px`        | `int`                   | `24`            | Sangría visual por nivel de lista (px).                   |

Uso típico mínimo:

```python
cfg = HelpConfig(
    md_text=md_text,
    title="Ayuda",
    size=pantalla.get_size(),
    wheel_step=48,
    on_scroll_limit=beep_on_limit,
    scroll_limit_cooldown_ms=300,
)
```

---

## 3. `HelpViewer` (visor embebible)

### Creación

```python
viewer = HelpViewer(cfg)
```

### Métodos públicos (resumen)

```python
viewer.on_mount(rect)
# Inicializa el visor para un rectángulo concreto (prepara layout y scroll).

viewer.on_unmount()
# Limpieza opcional al cerrar la ayuda o cambiar de escena.

handled = viewer.handle_event(event)
# Procesa:
# - MOUSEWHEEL
# - MOUSEBUTTONDOWN / MOUSEBUTTONUP (barra de scroll)
# - MOUSEMOTION (drag del thumb)
# - KEYDOWN (flechas, PgUp, PgDn, Home, End)
# Devuelve True si el evento ha sido consumido.

viewer.draw(surface, rect)
# Dibuja el contenido de ayuda dentro de rect (fondo, texto, barra de scroll).

viewer.open_window()
# Modo ventana propia:
# - Crea ventana Pygame con cfg.size.
# - Bucle interno de eventos (ESC o QUIT cierran).
# - Maneja visibilidad de ratón y key.set_repeat.
```

### Flujo típico embebido (resumen)

```python
cfg = HelpConfig(md_text=md, size=pantalla.get_size(), ...)
viewer = HelpViewer(cfg)
rect = pantalla.get_rect()
viewer.on_mount(rect)

while mostrando_ayuda:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            mostrando_ayuda = False
        elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_F1):
            mostrando_ayuda = False
        else:
            viewer.handle_event(ev)

    pantalla.fill((0, 0, 0))
    viewer.draw(pantalla, rect)
    pygame.display.flip()

viewer.on_unmount()
```

---

## 4. `open_help_standalone` (modo ventana independiente)

### Firma

```python
open_help_standalone(
    md_text: str,
    title: str = "Ayuda",
    size: tuple[int, int] = (800, 480),
    *,
    style_json_path: str | None = None,
    style_variant: str | None = None,
    style_overrides: dict[str, object] | None = None,
    fonts_dir: str | None = None,
    help_font_file: str | None = None,
    help_code_font_file: str | None = None,
    indent_spaces_per_level: int = 2,
    visual_indent_px: int = 24,
    wheel_step: int = 48,
    kernel_bg: tuple[int, int, int] | None = None,
    on_scroll_limit: callable[[str], None] | None = None,
    scroll_limit_cooldown_ms: int = 0,
) -> None
```

### Comportamiento resumido

- Llama a `pygame.init()` si es necesario.
- Crea ventana con `size`.
- Configura:
  - `pygame.mouse.set_visible(True)`,
  - `pygame.key.set_repeat(250, 40)`.
- Monta internamente un `HelpViewer` con los parámetros dados.
- Bucle propio:
  - `ESC` o `QUIT` → salir.
- En el cierre:
  - `on_unmount()`,
  - restaura `key.set_repeat`,
  - restaura visibilidad de ratón,
  - `pygame.quit()`.

### Uso típico

```python
import pygame
from popup_gui.help_core import open_help_standalone

pygame.init()
md_text = open("help.md", encoding="utf-8").read()

try:
    beep_sound = pygame.mixer.Sound("mp3/beep_scroll.mp3")
except pygame.error:
    beep_sound = None

def beep_on_limit(where: str) -> None:
    if beep_sound is not None:
        beep_sound.play()

open_help_standalone(
    md_text,
    title="Ayuda standalone",
    size=(1200, 900),
    wheel_step=48,
    kernel_bg=(222, 222, 222),
    on_scroll_limit=beep_on_limit,
    scroll_limit_cooldown_ms=300,
)
```

---

## 5. Subconjunto de Markdown soportado (recordatorio rápido)

- Encabezados: `#`, `##`, ..., `######`
- Listas:
  - No ordenadas: `- item`, `* item`
  - Numeradas: `1. item`
- Regla horizontal: `---`
- Énfasis:
  - `*itálica*`
  - `**negrita**`
  - `***negrita e itálica***`
- Código inline: `` `codigo()` ``
- Bloques de código:

  ```markdown
  ```python
  def algo():
      print("Hola")
  ```
  ```

(El lenguaje después de ``` se ignora para coloreado, pero no produce error.)

---

## 6. Checklist de integración rápida

- [ ] Tengo un `help.md` con contenido en Markdown reducido.
- [ ] Puedo leerlo con `open("help.md", encoding="utf-8").read()`.
- [ ] Para modo standalone:
  - [ ] Llamo a `open_help_standalone(md_text, ...)`.
- [ ] Para modo embebido:
  - [ ] Creo `HelpConfig` y `HelpViewer`.
  - [ ] Llamo a `on_mount(rect)` al entrar en la ayuda.
  - [ ] Paso eventos a `viewer.handle_event(ev)` en mi bucle.
  - [ ] Llamo a `viewer.draw(pantalla, rect)` cada frame.
  - [ ] Llamo a `on_unmount()` al salir de la ayuda.
- [ ] Si quiero beep en bordes:
  - [ ] Defino `on_scroll_limit(where)` en mi código.
  - [ ] Paso el callback en `HelpConfig` o en `open_help_standalone`.
  - [ ] Ajusto `scroll_limit_cooldown_ms` (ej. `300` ms).