# Especificación de soporte de tablas (mini_MarkDown)

Este documento define el **alcance**, **reglas de reconocimiento** y **renderizado** del soporte de tablas
en nuestro mini_MarkDown (parser + visualizador).

> Objetivo: un soporte **simple, robusto y mantenible**, sin “complicaciones raras”.
> Si una tabla no cabe, el usuario puede agrandar la ventana; el render debe **clipearse** sin romper la ejecución.

---

## 1) Alcance (Scope)

### 1.1. Formato soportado
Se soporta un subconjunto de **tablas tipo GitHub (GFM)** con esta estructura mínima:

1. **Cabecera** (fila con `|` y ≥ 2 columnas)
2. **Separador** (línea de guiones con opcionales `:` para alineación)
3. **Al menos 1 fila de datos** (fila con `|` y ≥ 2 columnas)

Ejemplo:

```
| Col A | Col B |
|------:|:-----:|
|  123  | hola  |
```

### 1.2. No objetivos (Non-goals)
En esta versión **no** se pretende soportar:
- Celdas multilínea.
- Escapado de `|` dentro de una celda (por ejemplo `\|`).
- Tablas anidadas dentro de listas, blockquotes u otros bloques complejos.
- Enlaces clicables y “runs” dentro de celdas (la tabla se renderiza como Surface).

---

## 2) Reconocimiento de bloque tabla (Parser)

### 2.1. Reglas mínimas para considerar “tabla”
Un bloque se reconoce como tabla si, y solo si, se cumple:

- Línea *i*: **fila de cabecera** con `|` y **al menos 2 celdas**.
- Línea *i+1*: **separador válido** con guiones `-` y opcionales `:` por columna.
- Línea *i+2*: **primera fila de datos** con `|` y **al menos 2 celdas**.

Si falta cualquiera de las condiciones anteriores, el texto se trata como **párrafo normal** (no tabla).

### 2.2. Número de columnas
El número de columnas de la tabla es **estrictamente** el número de celdas de la cabecera:

- `ncols = len(header_cells)`

Todas las filas de datos se normalizan contra `ncols`.

---

## 3) Normalización de filas (Datos inconsistentes)

### 3.1. Faltan celdas (row shorter than header)
Si una fila de datos tiene menos celdas que `ncols`:

- Se **rellena** cada celda faltante con el literal: **`@`**

Ejemplo con `ncols = 3`:

- Entrada: `["dato"]`
- Normalizado: `["dato", "@", "@"]`

### 3.2. Sobran celdas (row longer than header)
Si una fila de datos tiene más celdas que `ncols`:

- Se **trunca** a las primeras `ncols` celdas para renderizar en la tabla.
- Se marca la fila como `overflow = True` y el renderer dibuja un **`@` a la derecha de la tabla**
  (fuera de las celdas) alineado verticalmente con esa fila.

> La intención es que el resultado se vea “raro” y llame la atención, indicando que el MarkDown
> debe corregirse.

---

## 4) Alineación por columna

### 4.1. Alineación de cuerpo (según separador GFM)
La alineación se obtiene por columna en la fila separadora:

- `:---`  → izquierda
- `---:`  → derecha
- `:---:` → centrado
- `---`   → izquierda (por defecto)

Esta alineación aplica **solo a las filas de datos**.

### 4.2. Alineación de cabecera (fija)
La cabecera se renderiza **siempre centrada**, ignorando el separador.

---

## 5) Contrato del bloque `table` (salida del parser)

El parser emitirá un bloque con este esquema (diccionario):

```python
{
  "type": "table",
  "header": ["Col A", "Col B", ...],      # longitud = ncols
  "align":  ["left|center|right", ...],   # longitud = ncols (solo cuerpo)
  "rows": [
    ["r1c1", "r1c2", ...],                # cada fila normalizada a ncols
    ...
  ],
  "row_overflow": [False, True, ...]      # longitud = len(rows)
}
```

Notas:
- `rows` **siempre** contiene filas con longitud `ncols` debido a la normalización.
- `row_overflow[i]` es `True` si la fila original tenía más celdas que `ncols`.

---

## 6) Renderizado (Visualizador)

### 6.1. Estrategia general: pre-render a `Surface`
La tabla se renderiza como un **bloque único** pre-renderizado a un `pygame.Surface` (en composición/layout),
y luego se pinta con un `blit()` en `draw()`.

Esto simplifica el layout y evita integrar celdas en el motor de “runs” de texto.

### 6.2. Estilo fijo (no configurable)
Estilo de render **incondicional**:

- **Cabecera:** negrita, texto **blanco** sobre fondo **negro**, alineación centrada.
- **Cuerpo:** fuente normal, texto **negro** sobre fondo **blanco**, alineación por columna (separador).
- Separadores/bordes: líneas finas (p.ej. 1 px).

### 6.3. Cálculo de anchos y alto (pasada previa)
Se hace una pasada previa para calcular anchos de columna:

- Para cada columna `j`:
  - `max_text_width[j] = max(width(cell_text))` considerando **cabecera + filas**
- `col_width[j] = max_text_width[j] + 2 * pad_x`
- Altura de fila:
  - cabecera: `header_font.get_linesize() + 2 * pad_y`
  - datos: `body_font.get_linesize() + 2 * pad_y`

No se implementa wrapping; se asume que la tabla “debería caber”.

### 6.4. Caso “no cabe”
Si la tabla es más ancha (o alta) que el área visible:
- Se dibuja igual.
- Queda **clipeada** por el `clip` del visor (sin crash, sin excepciones, sin lógica adicional).

### 6.5. Indicador de overflow a la derecha
Si existe al menos una fila con `row_overflow=True`, el renderer reserva un “gutter” a la derecha
y dibuja un `@` fuera de la tabla (uno por fila afectada), alineado con la fila correspondiente.

---

## 7) Organización modular recomendada

Para mantener el parser y el visualizador “ligeros”:

- `md_tables.py`
  - `is_table_start(lines, i) -> bool`
  - `parse_table(lines, i) -> (table_block, new_index)`

- `table_renderer.py`
  - `render_table(block, body_font, header_font, ...) -> (surface, width, height)`

Cambios mínimos en el código principal:
- Hook en el parser: detectar tabla **antes** de consumir párrafos.
- Hook en el visualizador: en composición, renderizar tabla a `Surface`; en draw, hacer `blit()`.

---

## 8) Casos de prueba recomendados (mínimos)

1. Tabla válida mínima (2 cols, 1 fila).
2. Alineación: izquierda/derecha/centro en cuerpo; cabecera centrada.
3. Fila con menos celdas (relleno con `@` dentro de tabla).
4. Fila con más celdas (truncado + `@` a la derecha).
5. Tabla mal formada (sin separador o sin filas) → debe caer a párrafo.
6. Tabla seguida de párrafo (separación correcta de bloques).

