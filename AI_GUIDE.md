# Guía de Colaboración con la IA (Proyecto:Peces)

> Objetivo: que la IA trabaje **de forma predecible, segura y útil**
> en este proyecto, priorizando la calidad del código y la mínima fricción.

## Protocolo de trabajo

- **Política de archivos:** para inventariar usa
  find . -maxdepth 2 -not -path './.git*' -not -path './OLD*' -type f -printf '%P\n'
  y no leas binarios ni assets.

- **Invariantes:** no tocar shebang.

## Alcance del trabajo de la IA

- **No tocar**: assets binarios  salvo petición explícita.
- **Entorno**: Python 3.12, `pygame>=2.5`. Evitar añadir dependencias.
- **Compatibilidad**: Linux.

## Estilo y estándares

- **PEP8** y formateo tipo **Black** (longitud de línea 120).
- Tipado gradual con hints cuando sea razonable (no obligatorio en todo).
- Nombres claros en inglés para clases/métodos públicos; comentarios/docstrings en español.
- Evitar funciones “Dios”. Preferir funciones pequeñas, puras cuando se pueda.

## Codificación de modificaciones

- Respetar el historial de comentarios previos asociados a la partes del código no modificadas.
- Respetar las cabeceras del archivo. Estas deben indicar el nombre del archivo.
- Indicar con la máxima claridad el archivo, y la ubicación del fragmento añadido, eliminado o modificado.

## Política de dependencias

- Evitar en la medida de lo posible generar dependencias nuevas, salvo necesidad real y beneficio claro, y falta de alternativas.
- Si propones una dependencia nueva, justificalo, y comenta las alternativas.

## Manejo de ambigüedad

- Si falta contexto, **no inventes nada**. Propón 2–3 opciones breves con pros/contras y pide decisión.
- Si hay varias interpretaciones de un requisito, indicar explícitamente los supuestos.

## Evitar mejoras no solicitadas

- Cualquier posible mejora no solicitada ha de ser previamente autorizada.
- Mejorar lo que ya funciona correctamente requiere una justificación con bastante peso.

## Estilo de interacción con la IA

- Responder siempre en **español**.
- En las explicaciones no abusar de los términos técnicos en ingles salvo que sean ampliamente utilizados en informática desde hace mucho tiempo.
- Por defecto, las respuestas deben ser **cortas, directas y concisas**, salvo que se indique lo contrario.  
- Por defecto, evitar texto adicional no solicitado, explicaciones largas o introducciones innecesarias, salvo que se indique lo contrario.  
- No incluir ejemplos de código ni fragmentos que no hayan sido explícitamente pedidos.  
- Cuando se solicite código, limitarse estrictamente a lo solicitado, sin extras.  
- Respetar la estructura de archivos y convenciones descritas en este proyecto.
- No preguntar obviedades o cosas que que tengan implícita su respuesta por lo tratado anteriormente.
- En caso de dudas preguntar ofreciendo para cada una de ellas la opción que se considerará por defecto para evitar tener que contestarla.
- No asumir que los errores en el código son errores del usuario, ya que la IA introduce muchos de ellos con frecuencia.

## Exclusiones

Ignorar por defecto:

- `__pycache__/`
- `*.pyc`
- Archivos binarios, tales como fichero de imagen, de sonido, comprimidos, etc.
