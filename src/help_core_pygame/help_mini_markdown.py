from __future__ import annotations

# ====================================================================================================
# Proyecto : help_core_pygame
# Archivo  : help_mini_markdown.py
# Autor    : Antonio Castro Snurmacher 
# Licencia : MIT 
#
# Fecha última modificación: (4-feb-2026) 
#
# Descripción:
# ------------
#   El módulo help_mini_markdown.py implementa el parser MiniMarkdown de help_core_pygame.
#   A partir de un texto, lo normaliza y lo convierte en una lista de bloques (títulos, párrafos, listas, código,
#   tablas, imágenes, anclas y comentarios), y tokeniza el formato inline (negrita, itálica, código y enlaces).
#   Tras esta tarea, todo queda listo para entregar al visualizador (help_viewer_impl.py) toda la información
#   necesaria para poder visualizar el texto con el formato adecuado.
#
# Requisitos:
# -----------
#   - Versión Python     : >_3.9 
#   - Pygame
#
# Documentación en español: https://github.com/acastr008/help_core_pygame/blob/main/docs/INDEX_es.md 
# Documentation in English: https://github.com/acastr008/help_core_pygame/blob/main/docs/INDEX_en.md 
# ====================================================================================================



import re
from typing import Any, Dict, List

try:
    # Uso normal dentro del paquete
    from .md_tables import is_table_start, parse_table
except Exception:
    # Fallback si se ejecuta en contexto sin paquete
    from md_tables import is_table_start, parse_table


# ---------------------------------------------------------------------------
# Parser de Markdown reducido con límites de palabra
# ---------------------------------------------------------------------------
class _MiniMarkdown:
    """
    #, ##, ###, ####, #####, ###### → títulos
    --- → línea horizontal
    - / * → lista viñetas, 1. → lista numerada
    Bloques de código: … o 4 espacios
    Énfasis: *itálica*, **negrita**, ***ambas***
    `inline code`
    URLs http://...
    Bloques de código "fence"  con ``` para abrir/cerrar. No se detecta lenguaje
    (No hay imágenes, tablas ni enlaces con [texto](url))
    """
    def __init__(self, tab_size: int = 4, max_list_nesting: int = 4, indent_per_level_spaces: int = 2):
        self.tab_size = max(1, int(tab_size))
        self.max_list_nesting = max(1, int(max_list_nesting))
        # nº de espacios que equivalen a 1 nivel en PARSEO (no px en render)
        self.spaces_per_level = max(1, int(indent_per_level_spaces))

        # Bloques
        self._re_hr     = re.compile(r"^\s*---\s*$")
        # Ampliamos encabezados a 1..6 almohadillas (petición)
        self._re_h      = re.compile(r"^(#{1,6})\s+(.*)$")
        self._re_ul     = re.compile(r"^(\s*)([-*])\s+(.*)$")
        self._re_ol     = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")
        self._re_fence  = re.compile(r"^\s*```.*$")

        # Inline:
        # Para ***texto*** relajamos los límites de palabra para evitar que se
        # rompa en casos donde va pegado a otras palabras; ** y * mantienen
        # los límites para evitar falsos positivos tipo "precio*2".
        self._re_bold_italic = re.compile(r"\*\*\*(.+?)\*\*\*")
        self._re_bold        = re.compile(r"(?<!\w)\*\*(.+?)\*\*(?!\w)")
        self._re_italic      = re.compile(r"(?<!\w)\*(.+?)\*(?!\w)")

        self._re_inline_code = re.compile(r"`([^`]+)`")
        self._re_url         = re.compile(r"(https?://\S+)")
        # Enlaces Markdown básicos: [texto](destino). Se excluyen imágenes ![...](...)
        self._re_md_link     = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
        # Anclas HTML: <a id="etiqueta"></a> (se ignoran espacios alrededor)
        self._re_html_anchor = re.compile(r"^\s*<a\s+id=\"([^\"]+)\"\s*>\s*</a>\s*$")
        # Comentarios HTML: <!-- ... --> (una sola línea)
        self._re_html_comment = re.compile(r"^\s*<!--(.*?)-->\s*$")
        # Imagen Markdown como bloque (línea completa): ![alt](src)
        # Caso simple: no soporta paréntesis anidados en src.
        self._re_image_line = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)\s*$")


    def normalize(self, text: str) -> str:
        return text.replace("\t", " " * self.tab_size).replace("\r\n", "\n").replace("\r", "\n")

    def parse(self, text: str) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        lines = text.split("\n")
        n = len(lines)
        i = 0
        in_fence = False
        fence_buf: List[str] = []

        while i < n:
            line = lines[i]

            # Saltar vacías entre bloques (pero no dentro de fence)
            if not in_fence and line.strip() == "":
                i += 1
                continue

            # Fence ```
            if self._re_fence.match(line):
                if not in_fence:
                    in_fence = True
                    fence_buf = []
                else:
                    out.append({"type": "code", "text": "\n".join(fence_buf)})
                    in_fence = False
                i += 1
                continue

            if in_fence:
                fence_buf.append(line)  # ← dentro del fence, preservamos TODO, incluidas líneas vacías
                i += 1
                continue

            # Imagen Markdown como bloque: línea completa ![alt](src)
            # - No se soporta inline (dentro de párrafos).
            # - No se soporta en listas (si fuese en lista, line.strip() no empezaría por '![').
            line_stripped = line.strip()
            m_img = self._re_image_line.match(line_stripped)
            # if m_img is not None and line_stripped.startswith("!["):
            if m_img is not None:
                out.append({"type": "img", "alt": m_img.group(1).strip(), "src": m_img.group(2).strip()})
                i += 1
                continue


            # Comentarios HTML (simples):
            #  - 1 línea completa: <!-- ... -->
            #  - bloque multilínea: línea '<!--' y cierre con línea '-->'
            m_one = self._re_html_comment.match(line)
            if m_one:
                out.append({"type": "comment", "text": m_one.group(1).strip()})
                i += 1
                continue

            if line.strip() == "<!--":
                buf: List[str] = []
                i += 1
                while i < n and lines[i].strip() != "-->":
                    buf.append(lines[i])
                    i += 1
                # Consumir línea de cierre '-->' si existe
                if i < n and lines[i].strip() == "-->":
                    i += 1
                comment_text = "\n".join(buf).strip()
                out.append({"type": "comment", "text": comment_text})
                continue


            # Ancla HTML: <a id="etiqueta"></a>
            m_anchor = self._re_html_anchor.match(line)
            if m_anchor:
                out.append({"type": "anchor", "id": m_anchor.group(1)})
                i += 1
                continue

            # Regla horizontal
            if self._re_hr.match(line):
                out.append({"type": "hr"})
                i += 1
                continue

            # Encabezados (ahora h1..h6)
            mh = self._re_h.match(line)
            if mh:
                level = len(mh.group(1))
                out.append({"type": f"h{level}", "text": mh.group(2).strip()})
                i += 1
                continue


            # ----------------------------------------------------------------------
            # >>> Eliminada la regla: "Si empieza con 4 espacios → bloque de código"
            # (Se conserva el comentario para documentación, pero no se aplica.)


            # Listas

            mul = self._re_ul.match(line)
            mol = self._re_ol.match(line)
            if mul or mol:
                kind = "ul" if mul else "ol"
                items: List[Dict[str, Any]] = []
                while i < n:
                    cur = lines[i]
                    # Ignorar comentarios HTML de línea completa dentro de listas (no rompen la lista)
                    if self._re_html_comment.match(cur):
                        i += 1
                        continue
                    # Ignorar bloque de comentario multilínea dentro de listas
                    if cur.strip() == "<!--":
                        i += 1
                        while i < n and lines[i].strip() != "-->":
                            i += 1
                        if i < n and lines[i].strip() == "-->":
                            i += 1
                        continue
                    m = (self._re_ul.match(cur) if kind == "ul" else self._re_ol.match(cur))
                    if not m:
                        break
                    indent_spaces = len(m.group(1))
                    level = min(indent_spaces // self.spaces_per_level, self.max_list_nesting - 1)
                    if kind == "ul":
                        text_item = m.group(3).strip()
                        items.append({"level": level, "text": text_item})
                    else:
                        num = int(m.group(2))
                        text_item = m.group(3).strip()
                        items.append({"level": level, "num": num, "text": text_item})
                    i += 1
                out.append({"type": kind, "items": items})
                continue

            # Tabla Markdown como bloque (GFM reducido)
            # - Se detecta antes del párrafo para evitar que se absorba dentro de texto.
            if is_table_start(lines, i):
                res = parse_table(lines, i)
                if res is not None:
                    out.append(res.block)
                    i = res.next_index
                    continue

            # Párrafo
            para = [line]
            i += 1
            while i < n and lines[i].strip() != "" and not self._re_h.match(lines[i]) \
                  and not self._re_hr.match(lines[i]) and not lines[i].startswith("    ") \
                  and not self._re_ul.match(lines[i]) and not self._re_ol.match(lines[i]) \
                  and not self._re_html_anchor.match(lines[i]) and not self._re_html_comment.match(lines[i]) \
                  and lines[i].strip() != "<!--" \
                  and not self._re_fence.match(lines[i]) \
                  and not self._re_image_line.match(lines[i].strip()) \
                  and not is_table_start(lines, i):
                para.append(lines[i])
                i += 1
            # Saltar separadores vacíos entre párrafos
            while i < n and lines[i].strip() == "":
                i += 1
            text_p = "\n".join(para).strip()
            if text_p:
                out.append({"type": "p", "text": text_p})


        # Fence sin cierre al EOF → se considera bloque de código
        if in_fence and fence_buf:
            out.append({"type": "code", "text": "\n".join(fence_buf)})

        # Fence sin cierre al EOF → se considera bloque de código
        if in_fence and fence_buf:
            out.append({"type": "code", "text": "\n".join(fence_buf)})

        return out

    def tokenize_inline(self, text: str) -> List[Dict[str, Any]]:
        runs: List[Dict[str, Any]] = []

        # proteger inline code
        parts: List[Tuple[str, bool]] = []
        last = 0
        for m in self._re_inline_code.finditer(text):
            if m.start() > last:
                parts.append((text[last:m.start()], False))
            parts.append((m.group(1), True))
            last = m.end()
        if last < len(text):
            parts.append((text[last:], False))

        def emit_plain(seg: str) -> None:
            # *** → ** → *
            base: List[Tuple[str, Dict[str, bool]]] = [(seg, {})]

            def apply(regex, flag, incoming):
                out = []
                for chunk, attrs in incoming:
                    if attrs:
                        out.append((chunk, attrs))
                        continue
                    pos = 0
                    for m in regex.finditer(chunk):
                        if m.start() > pos:
                            out.append((chunk[pos:m.start()], {}))
                        out.append((m.group(1), {flag: True}))
                        pos = m.end()
                    if pos < len(chunk):
                        out.append((chunk[pos:], {}))
                return out

            base = apply(self._re_bold_italic, "bi", base)
            base = apply(self._re_bold, "b", base)
            base = apply(self._re_italic, "i", base)

            for txt, flags in base:
                if not txt:
                    continue
                runs.append({
                    "text": txt,
                    "bold": bool(flags.get("b") or flags.get("bi")),
                    "italic": bool(flags.get("i") or flags.get("bi")),
                    "code": False,
                    "link": False,
                    "href": ""
                })

        for seg, is_code in parts:
            if is_code:
                runs.append({"text": seg, "bold": False, "italic": False, "code": True, "link": False, "href": ""})
            else:
                emit_plain(seg)


        # Links y URLs
        # 1) Expandir enlaces Markdown [texto](destino) fuera de inline code.
        expanded: List[Dict[str, Any]] = []
        for r in runs:
            if r.get("code") or not r.get("text"):
                expanded.append(r)
                continue

            seg = str(r["text"])
            pos = 0
            for m_link in self._re_md_link.finditer(seg):
                if m_link.start() > pos:
                    expanded.append({**r, "text": seg[pos:m_link.start()], "link": False, "href": ""})

                link_text = m_link.group(1)
                link_href = m_link.group(2).strip()
                expanded.append({**r, "text": link_text, "link": True, "href": link_href, "code": False})

                pos = m_link.end()

            if pos < len(seg):
                expanded.append({**r, "text": seg[pos:], "link": False, "href": ""})

        # 2) Autolinks por URL en crudo (http/https), recortando puntuación final.
        final: List[Dict[str, Any]] = []
        trailing_punct = ".,;:!?)]}\"'"

        for r in expanded:
            if r.get("code") or not r.get("text") or r.get("link"):
                # Si ya es link (p.ej. [texto](destino)), NO re-procesar URLs dentro.
                final.append(r)
                continue

            txt = str(r["text"])
            pos = 0
            for m_url in self._re_url.finditer(txt):
                if m_url.start() > pos:
                    final.append({**r, "text": txt[pos:m_url.start()], "link": False, "href": ""})

                raw_url = m_url.group(1)

                # Recortar puntuación final típica pegada a la URL.
                # Caso especial: ')': solo se recorta si sobran paréntesis de cierre.
                tail = ""
                url = raw_url
                while url and url[-1] in trailing_punct:
                    last = url[-1]
                    if last == ")" and url.count("(") >= url.count(")"):
                        break
                    tail = last + tail
                    url = url[:-1]

                if url:
                    final.append({**r, "text": url, "link": True, "href": url, "code": False})

                if tail:
                    final.append({**r, "text": tail, "link": False, "href": ""})

                pos = m_url.end()

            if pos < len(txt):
                final.append({**r, "text": txt[pos:], "link": False, "href": ""})

        return final


