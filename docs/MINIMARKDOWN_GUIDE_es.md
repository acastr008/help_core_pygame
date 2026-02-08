# Guía de MiniMarkdown (help_core_pygame)

> **Objetivo**  
> Este documento describe **exclusivamente** el subconjunto de Markdown (“MiniMarkdown”) que implementa
> el parser interno `_MiniMarkdown` y que usa el sistema de ayuda de `help_core_pygame`.

MiniMarkdown está pensado para ser:

- **Portátil** (sin dependencias externas aparte de Pygame en el visor).
- **Predecible** (reglas simples; pocos casos “mágicos”).
- **Suficiente** para ayudas vistosas: encabezados, párrafos, listas, código, enlaces, anclas, imágenes como bloque y tablas simples.

---

## Índice

- [1. Conceptos básicos](#conceptos-basicos)
- [2. Normalización del texto](#normalizacion-del-texto)
- [3. Bloques soportados](#bloques-soportados)
  - [3.1 Encabezados ATX](#encabezados-atx)
  - [3.2 Párrafos](#parrafos)
  - [3.3 Línea horizontal](#linea-horizontal)
  - [3.4 Listas (UL y OL)](#listas-ul-y-ol)
  - [3.5 Bloques de código (fences)](#bloques-de-codigo-fences)
  - [3.6 Comentarios HTML](#comentarios-html)
  - [3.7 Anclas HTML](#anclas-html)
  - [3.8 Imágenes como bloque](#imagenes-como-bloque)
  - [3.9 Tablas (GFM reducido)](#tablas-gfm-reducido)
- [4. Inline: tokenización dentro de texto](#inline-tokenizacion-dentro-de-texto)
  - [4.1 Énfasis](#enfasis)
  - [4.2 Código inline](#codigo-inline)
  - [4.3 Enlaces: Markdown y URL cruda](#enlaces-markdown-y-url-cruda)
- [5. Qué NO está soportado](#que-no-esta-soportado)
- [6. Esquema de salida del parser](#esquema-de-salida-del-parser)
  - [6.1 Bloques](#bloques)
  - [6.2 Runs inline](#runs-inline)
- [7. Consejos prácticos](#consejos-practicos)
- [8. Checklist de compatibilidad (para autores)](#checklist-de-compatibilidad-para-autores)

---

<a id="conceptos-basicos"></a>
## 1. Conceptos básicos

MiniMarkdown trabaja en dos fases:

1) **Parseo por bloques** (`parse()`): reconoce estructuras “grandes” (encabezados, listas, código, tablas, etc.)
y produce una lista de **bloques** con `type`.

2) **Tokenización inline** (`tokenize_inline()`): dentro de un texto (por ejemplo un párrafo o el texto de un ítem),
se divide en fragmentos (“runs”) con atributos como negrita, itálica, código y link.

En general:

- Si algo es un **bloque**, se decide en `parse()`.
- Si algo está **dentro de texto** (negrita, itálica, links, código inline), se decide en `tokenize_inline()`.

---

<a id="normalizacion-del-texto"></a>
## 2. Normalización del texto

Antes de parsear, se recomienda normalizar el texto:

- `\t` → se convierte a espacios según `tab_size`.
- `\r\n` y `\r` → se convierten a `\n`.

Esto evita diferencias por plataforma y hace el parseo más predecible.

> Nota práctica: en el flujo típico del visor, el texto se normaliza antes de parsear, de forma que el usuario
> final no tiene que hacerlo manualmente.

---

<a id="bloques-soportados"></a>
## 3. Bloques soportados

<a id="encabezados-atx"></a>
### 3.1 Encabezados ATX

Se soportan encabezados ATX con `#` de 1 a 6:

```text
# H1
## H2
### H3
#### H4
##### H5
###### H6
```

El parser genera bloques con tipos `h1`...`h6` y campo `text`.

**Regla**: debe haber al menos un espacio tras las almohadillas.

---

<a id="parrafos"></a>
### 3.2 Párrafos

Un párrafo es “lo que queda” cuando una o más líneas **no son** un bloque reconocido.

Características:

- Un párrafo puede ocupar varias líneas.
- Se corta un párrafo cuando aparece una línea vacía o cuando empieza otro bloque (encabezado, lista, tabla, fence, etc.).

Ejemplo:

```text
Esto es un párrafo en dos líneas.
Sigue siendo el mismo párrafo.

Esto ya es otro párrafo.
```

---

<a id="linea-horizontal"></a>
### 3.3 Línea horizontal

La línea exacta `---` (con posibles espacios alrededor) se interpreta como regla horizontal:

```text
---
```

Genera un bloque de tipo `hr`.

---

<a id="listas-ul-y-ol"></a>
### 3.4 Listas (UL y OL)

Se soportan:

- **Listas con viñetas (UL)** usando `- ` o `* `.
- **Listas numeradas (OL)** usando `N. ` (por ejemplo `1. `, `2. `).

El anidamiento se calcula por indentación en espacios:

- `indent_per_level_spaces` = cuántos espacios equivalen a 1 nivel.
- `max_list_nesting` = profundidad máxima (el nivel se “satura” si se supera).

Ejemplo UL:

```text
- Nivel 0
  - Nivel 1 (2 espacios si indent_per_level_spaces=2)
    - Nivel 2
```

Ejemplo OL:

```text
1. Item 1
2. Item 2
   1. Subitem
```

**Importante**:

- Dentro de listas, los comentarios HTML de línea completa y los bloques `<!-- ... -->` se **ignoran** (no rompen la lista).
- MiniMarkdown no implementa “continuations” tipo Markdown completo (párrafos largos dentro de un ítem usando líneas
  indentadas). Los ítems son de una sola línea textual.

---

<a id="bloques-de-codigo-fences"></a>
### 3.5 Bloques de código (fences)

Se soportan fences con triple backtick:

```text
```python
print("hola")
```
```

Notas:

- El parser detecta fences por una línea que empieza con ``` (puede llevar texto, p.ej. `python`), pero:
  - **No interpreta** el lenguaje (se ignora, solo se usa para abrir/cerrar).
- Dentro del fence, se preserva el contenido tal cual, incluyendo líneas vacías.
- Si un fence queda sin cerrar al final del texto, se emite igualmente un bloque `code` con lo acumulado.

> Nota: el “código por indentación de 4 espacios” **no está soportado** en el estado actual.

---

<a id="comentarios-html"></a>
### 3.6 Comentarios HTML

Se soportan comentarios HTML como **bloques**, de dos formas:

1) **Una sola línea completa**:

```text
<!-- comentario -->
```

2) **Bloque multilínea**:

```text
<!--
línea 1
línea 2
-->
```

El parser produce bloques de tipo `comment` con `text`.

Recomendación de uso:

- Para comentarios “confiables”, usar **línea completa**.
- Los comentarios en mitad de una línea (inline) **no** se tratan como comentario; se quedan como texto normal.

---

<a id="anclas-html"></a>
### 3.7 Anclas HTML

Se soporta la ancla HTML en **línea completa**:

```text
<a id="mi_ancla"></a>
```

Genera un bloque `anchor` con el campo `id`.

Usos típicos:

- Crear índice manual.
- Crear links internos con `#mi_ancla`.

---

<a id="imagenes-como-bloque"></a>
### 3.8 Imágenes como bloque

Se soporta imagen Markdown como **bloque** cuando ocupa una línea completa:

```text
![texto alternativo](ruta/o/url)
```

El parser emite:

- `type: "img"`
- `alt`: texto alternativo
- `src`: ruta o URL

Limitaciones:

- No hay soporte de imágenes **inline** dentro de un párrafo.
- No se soporta sintaxis compleja con paréntesis anidados en la ruta.
- El uso dentro de listas no está contemplado: las imágenes se tratan como bloques independientes.

---

<a id="tablas-gfm-reducido"></a>
### 3.9 Tablas (GFM reducido)

MiniMarkdown incluye soporte de tablas estilo GFM reducido, como bloque.

Ejemplo:

```text
| Col A | Col B |
|------:|:-----:|
|  123  | hola  |
```

Notas:

- Se detecta la tabla **antes** de formar el párrafo, para que una tabla “pegada” al texto siga siendo tabla.
- Se soportan alineaciones en el separador de cabecera:
  - `:---` izquierda, `---:` derecha, `:---:` centrado (según implementación interna).
- Casos “irregulares” (filas con menos/más celdas) se gestionan de forma robusta para no romper el render.

---

<a id="inline-tokenizacion-dentro-de-texto"></a>
## 4. Inline: tokenización dentro de texto

La tokenización inline se aplica sobre textos como:

- `p.text` (párrafos)
- `hN.text` (encabezados)
- `items[].text` en listas

Regla de precedencia:

1) Se protege primero el **código inline** (entre backticks) para que no se procese como énfasis o link.
2) Se aplica énfasis (***, **, *).
3) Se expanden links `[texto](destino)` (fuera de código).
4) Se detectan URLs crudas `http(s)://...` (fuera de código y fuera de links ya marcados).

---

<a id="enfasis"></a>
### 4.1 Énfasis

Se soporta:

- `***texto***` → negrita + itálica
- `**texto**` → negrita
- `*texto*` → itálica

Regla importante:

- Para evitar falsos positivos tipo `precio*2`, `**` y `*` exigen límites de palabra (no pegado a letras/números).
- `***` es más permisivo para reducir casos donde va pegado a otras palabras.

---

<a id="codigo-inline"></a>
### 4.2 Código inline

Se soporta:

```text
Usa `inline code` en una frase.
```

Efectos:

- El texto entre backticks se marca como run `code=true`.
- Dentro de ese segmento NO se detectan links ni énfasis.

Limitación conocida (de uso):

- Si metes `inline code` dentro de un fragmento en negrita/itálica, el resultado final depende del renderizador;
  la recomendación práctica es **no anidar** inline code dentro de énfasis.

---

<a id="enlaces-markdown-y-url-cruda"></a>
### 4.3 Enlaces: Markdown y URL cruda

Se soportan dos formas:

#### A) Enlaces Markdown básicos

```text
[Texto visible](destino)
```

- Se excluyen imágenes `![...](...)`.
- Se emiten runs con `link=true`, `href=destino` y texto = `Texto visible`.

El destino puede ser:

- URL: `https://example.com/...`
- Ancla interna: `#mi_ancla`

#### B) Autolink por URL cruda

Detecta URLs en texto:

```text
Visita https://www.python.org y también http://example.com/test?x=1#y.
```

Reglas:

- Se detecta `http://` y `https://` seguido de caracteres no-espacio.
- Se recorta puntuación final típica `.,;:!?)]}"'` para que no forme parte de la URL.
  - Caso especial: `)` solo se recorta si sobran paréntesis de cierre.

**Casos negativos** (NO deben linkear):

- URLs dentro de código inline: `` `https://www.python.org/` ``
- URLs dentro de bloque code fence

---

<a id="que-no-esta-soportado"></a>
## 5. Qué NO está soportado

MiniMarkdown es intencionalmente limitado. No se soporta (lista no exhaustiva):

- Markdown completo (CommonMark/GFM total).
- Citas `>`.
- Enlaces de referencia `[a][b]`.
- Imágenes inline (dentro de párrafos).
- Bloques de código por indentación de 4 espacios.
- List items multilínea (continuations complejas).
- Parseo de lenguaje en fences (```python) como metadata estructurada.
- HTML arbitrario (solo se soportan anclas y comentarios en formatos concretos).

---

<a id="esquema-de-salida-del-parser"></a>
## 6. Esquema de salida del parser

<a id="bloques"></a>
### 6.1 Bloques

`parse(text)` devuelve una lista de diccionarios. Tipos principales:

- Encabezados:
  - `{"type": "h1"|"h2"|...|"h6", "text": str}`

- Párrafo:
  - `{"type": "p", "text": str}`

- Regla horizontal:
  - `{"type": "hr"}`

- Listas:
  - UL:
    - `{"type": "ul", "items": [{"level": int, "text": str}, ...]}`
  - OL:
    - `{"type": "ol", "items": [{"level": int, "num": int, "text": str}, ...]}`

- Código:
  - `{"type": "code", "text": str}`

- Comentario:
  - `{"type": "comment", "text": str}`

- Ancla:
  - `{"type": "anchor", "id": str}`

- Imagen:
  - `{"type": "img", "alt": str, "src": str}`

- Tabla:
  - `{"type": "table", ...}` (estructura interna gestionada por el módulo de tablas)

---

<a id="runs-inline"></a>
### 6.2 Runs inline

`tokenize_inline(text)` devuelve una lista de “runs” con este esquema:

```text
{
  "text": str,
  "bold": bool,
  "italic": bool,
  "code": bool,
  "link": bool,
  "href": str
}
```

Reglas:

- Si `code=true`, el fragmento no se procesa como énfasis ni link.
- Si `link=true`, `href` contiene el destino (URL o `#anchor`).

---

<a id="consejos-practicos"></a>
## 7. Consejos prácticos

- **Crea un índice manual** usando anclas HTML:
  - `<a id="ID_INDICE"></a>` y links `[Volver](#ID_INDICE)`.
- **Usa fences** para código siempre: evita depender de “4 espacios”.
- **Separa tablas e imágenes como bloques**:
  - Aunque una tabla puede ir “pegada” al texto, es más legible dejar una línea en blanco antes/después.
- **Comentarios**:
  - Para notas del autor, usa `<!-- ... -->` en **línea completa**.
  - Evita comentarios “en medio” de una línea: se verán como texto.
- **Links**:
  - Si pones una URL seguida de punto o paréntesis, MiniMarkdown intenta recortarlos; aun así, es mejor separar con espacio.

---

<a id="checklist-de-compatibilidad-para-autores"></a>
## 8. Checklist de compatibilidad (para autores)

Antes de dar por bueno un texto:

- [ ] Los títulos usan `#` + espacio (no `#Titulo`).
- [ ] El código está siempre entre fences ``` y no depende de indentación.
- [ ] Las imágenes están en una línea completa `![alt](src)`.
- [ ] Las anclas usan línea completa `<a id="..."></a>`.
- [ ] Los comentarios importantes están en línea completa `<!-- ... -->`.
- [ ] Las tablas tienen cabecera + separador correcto.
- [ ] Los links internos apuntan a IDs existentes (`#...`).
- [ ] No hay URLs críticas dentro de `inline code` (no linkearán).
