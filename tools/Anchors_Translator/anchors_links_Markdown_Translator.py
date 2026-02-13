#!/usr/bin/python3
"""
Programa: anchors_links_Markdown_Translator.py
Fecha: 12/Feb/2026 y hora 00:00
Titulo: Traducción masiva de anclas/links Markdown entre idiomas
Descripción: Sustituye IDs de anclas (<a id="...">) y enlaces internos (#id) desde un idioma origen
             a un idioma destino, usando una tabla multi-idioma basada en tuplas.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Lista de idiomas en el mismo orden que las tuplas de anchor_id_pairs.
languages = ["es", "en"]

# IMPORTANTE: La lista de tuplas ( IDs_es, IDs_en ) Debe ser proporcionada.
anchor_id_pairs = [
    ("parte-i-api-p-blica-usuario-final", "part-i-public-api-end-user"),
    ("api-del-m-dulo-help-core-py-es", "api-for-module-help_core-py"),
    ("help_core.parte-i-api-p-blica-integraci-n-y-uso", "help_core.part-i-public-api-integration-and-usage"),
    ("help_core.ShowHelpOverlay", "help_core.ShowHelpOverlay"),
    ("help_core.firma", "help_core.signature"),
    ("help_core.descripci-n", "help_core.description"),
    ("help_core.par-metros", "help_core.parameters"),
    ("help_core.comportamiento-y-detalles-relevantes", "help_core.behavior-and-relevant-details"),
    ("help_core.ejemplo-m-nimo", "help_core.minimal-example"),
    ("help_core.limitaciones", "help_core.limitations"),
    ("help_core.open_help_standalone", "help_core.open_help_standalone"),
    ("help_core.firma-2", "help_core.signature-2"),
    ("help_core.descripci-n-2", "help_core.description-2"),
    ("help_core.par-metros-nivel-integrador", "help_core.parameters-integrator-level"),
    ("help_core.ejemplo-m-nimo-2", "help_core.minimal-example-2"),
    ("help_core.3-contrato-m-nimo-de-integraci-n-standalone-vs-overlay", "help_core.3-minimal-integration-contract-standalone-vs-overlay"),
    ("help_core.api-del-m-dulo-help-viewer-impl-py-es", "help_core.api-for-module-help_viewer_impl-py"),
    ("help_viewer_impl.parte-i-api-p-blica-integraci-n-y-uso", "help_viewer_impl.part-i-public-api-integration-and-usage"),
    ("help_viewer_impl.HelpConfig", "help_viewer_impl.HelpConfig"),
    ("help_viewer_impl.descripci-n", "help_viewer_impl.description"),
    ("help_viewer_impl.campos", "help_viewer_impl.fields"),
    ("help_viewer_impl.notas-de-uso", "help_viewer_impl.usage-notes"),
    ("help_viewer_impl.HelpViewer", "help_viewer_impl.HelpViewer"),
    ("help_viewer_impl.2-1-constructor", "help_viewer_impl.2-1-constructor"),
    ("help_viewer_impl.2-2-uso-embebido-modo-widget", "help_viewer_impl.2-2-embedded-usage-widget-mode"),
    ("help_viewer_impl.2-3-uso-standalone", "help_viewer_impl.2-3-standalone-usage"),
    ("help_viewer_impl.2-4-adaptador-opcional-as_interactive", "help_viewer_impl.2-4-optional-adapter-as_interactive"),
    ("help_viewer_impl.3-anclas-y-links", "help_viewer_impl.3-anchors-and-links"),
    ("help_viewer_impl.3-1-anclas-expl-citas-html", "help_viewer_impl.3-1-explicit-anchors-html"),
    ("help_viewer_impl.3-2-anclas-autom-ticas-por-encabezados", "help_viewer_impl.3-2-automatic-anchors-from-headings"),
    ("help_viewer_impl.3-3-links-http-s", "help_viewer_impl.3-3-http-s-links"),
    ("help_viewer_impl.4-im-genes", "help_viewer_impl.4-images"),
    ("help_viewer_impl.5-tablas", "help_viewer_impl.5-tables"),
    ("help_viewer_impl.parte-ii-api-de-mantenimiento-desarrolladores", "help_viewer_impl.part-ii-maintenance-api-developers"),
    ("help_viewer_impl.api-del-m-dulo-help-core-py-es", "help_viewer_impl.api-for-module-help_core-py"),
    ("help_core.parte-ii-api-interna-de-mantenimiento-relacionada-con-este-m-dulo", "help_core.part-ii-internal-maintenance-api-related-to-this-module"),
    ("help_core.4-papel-de-help-core-py-en-la-arquitectura", "help_core.4-role-of-help_core-py-in-the-architecture"),
    ("help_core.5-dependencias-y-s-mbolos-importados", "help_core.5-dependencies-and-imported-symbols"),
    ("help_core.6-detalles-de-implementaci-n-relevantes", "help_core.6-relevant-implementation-details"),
    ("help_core.6-1-overlay-modal-y-frame-congelado", "help_core.6-1-modal-overlay-and-frozen-frame"),
    ("help_core.6-2-gesti-n-de-autorepeat", "help_core.6-2-autorepeat-handling"),
    ("help_core.ShowHelpOverlay-2", "help_core.ShowHelpOverlay-2"),
    ("help_core.7-testing-manual-demos-relacionadas", "help_core.7-manual-testing-related-demos"),
    ("help_core.8-problemas-conocidos-notas-operativas", "help_core.8-known-issues-operational-notes"),
    ("help_core.9-historial-y-compatibilidad", "help_core.9-history-and-compatibility"),
    ("help_core.10-changelog-del-documento", "help_core.10-document-changelog"),
    ("help_core.api-del-m-dulo-help-viewer-impl-py-es-2", "help_core.api-for-module-help_viewer_impl-py-2"),
    ("help_viewer_impl.parte-ii-api-interna-de-mantenimiento", "help_viewer_impl.part-ii-internal-maintenance-api"),
    ("help_viewer_impl.DEFAULT_STYLE", "help_viewer_impl.DEFAULT_STYLE"),
    ("help_viewer_impl._lines", "help_viewer_impl._lines"),
    ("help_viewer_impl.7-1-self-blocks-entrada", "help_viewer_impl.7-1-self-blocks-input"),
    ("help_viewer_impl.7-2-self-lines-salida-de-composici-n", "help_viewer_impl.7-2-self-lines-composition-output"),
    ("help_viewer_impl.draw", "help_viewer_impl.draw"),
    ("help_viewer_impl.handle_event", "help_viewer_impl.handle_event"),
    ("help_viewer_impl.10-helpers-internos-principales-inventario", "help_viewer_impl.10-main-internal-helpers-inventory"),
    ("help_viewer_impl.11-notas-operativas-y-deuda-t-cnica", "help_viewer_impl.11-operational-notes-and-technical-debt"),
    ("help_viewer_impl.api-del-m-dulo-help-mini-markdown-py-es", "help_viewer_impl.api-for-module-help_mini_markdown-py"),
    ("help_mini_markdown.parte-ii-api-interna-de-mantenimiento", "help_mini_markdown.part-ii-internal-maintenance-api"),
    ("help_mini_markdown._MiniMarkdown", "help_mini_markdown._MiniMarkdown"),
    ("help_mini_markdown.1-1-constructor", "help_mini_markdown.1-1-constructor"),
    ("help_mini_markdown.2-normalize-text", "help_mini_markdown.2-normalize-text"),
    ("help_mini_markdown.firma", "help_mini_markdown.signature"),
    ("help_mini_markdown.descripci-n", "help_mini_markdown.description"),
    ("help_mini_markdown.devuelve", "help_mini_markdown.returns"),
    ("help_mini_markdown.3-parse-text", "help_mini_markdown.3-parse-text"),
    ("help_mini_markdown.firma-2", "help_mini_markdown.signature-2"),
    ("help_mini_markdown.descripci-n-2", "help_mini_markdown.description-2"),
    ("help_mini_markdown.tipos-de-bloque-emitidos-dict", "help_mini_markdown.emitted-block-types-dict"),
    ("help_mini_markdown.4-tokenize-inline-text", "help_mini_markdown.4-tokenize-inline-text"),
    ("help_mini_markdown.firma-3", "help_mini_markdown.signature-3"),
    ("help_mini_markdown.descripci-n-3", "help_mini_markdown.description-3"),
    ("help_mini_markdown.formato-de-salida-run", "help_mini_markdown.output-format-run"),
    ("help_mini_markdown.reglas-importantes", "help_mini_markdown.important-rules"),
    ("help_mini_markdown.5-detalles-y-decisiones-de-mantenimiento", "help_mini_markdown.5-maintenance-details-and-decisions"),
    ("help_mini_markdown.5-1-regex-de-nfasis-y-l-mites-de-palabra", "help_mini_markdown.5-1-emphasis-regex-and-word-boundaries"),
    ("help_mini_markdown.5-2-c-digo-fence-sin-lenguaje", "help_mini_markdown.5-2-fenced-code-without-language"),
    ("help_mini_markdown.5-3-doble-bloque-de-cierre-de-fence-al-eof-nota", "help_mini_markdown.5-3-double-fence-closing-block-at-eof-note"),
    ("help_mini_markdown.md_tables", "help_mini_markdown.md_tables"),
    ("help_mini_markdown.api-del-m-dulo-md-tables-py-es", "help_mini_markdown.api-for-module-md_tables-py"),
    ("md_tables.parte-ii-api-interna-de-mantenimiento", "md_tables.part-ii-internal-maintenance-api"),
    ("md_tables.5-constantes-internas", "md_tables.5-internal-constants"),
    ("md_tables.TableParseResult", "md_tables.TableParseResult"),
    ("md_tables.uso", "md_tables.usage"),
    ("md_tables.7-is-table-start-lines-index", "md_tables.7-is-table-start-lines-index"),
    ("md_tables.firma", "md_tables.signature"),
    ("md_tables.reglas-exactas-tal-y-como-est-n-implementadas", "md_tables.exact-rules-as-implemented"),
    ("md_tables.8-parse-table-lines-index", "md_tables.8-parse-table-lines-index"),
    ("md_tables.firma-2", "md_tables.signature-2"),
    ("md_tables.contrato-del-bloque-devuelto", "md_tables.returned-block-contract"),
    ("md_tables.reglas-de-parseo-relevantes", "md_tables.relevant-parsing-rules"),
    ("md_tables.9-helpers-internos", "md_tables.9-internal-helpers"),
    ("md_tables.9-1-parse-table-row-line", "md_tables.9-1-parse-table-row-line"),
    ("md_tables.9-2-parse-separator-row-line-expected-cols", "md_tables.9-2-parse-separator-row-line-expected-cols"),
    ("md_tables.9-3-normalize-row-row-cells-ncols", "md_tables.9-3-normalize-row-row-cells-ncols"),
    ("md_tables.10-notas-de-mantenimiento-decisiones", "md_tables.10-maintenance-notes-decisions"),
    ("md_tables.11-relaci-n-con-otros-m-dulos", "md_tables.11-relationship-with-other-modules"),
    ("md_tables.api-del-m-dulo-table-renderer-py-es", "md_tables.api-for-module-table_renderer-py"),
    ("table_renderer.parte-ii-api-interna-de-mantenimiento", "table_renderer.part-ii-internal-maintenance-api"),
    ("table_renderer.5-constantes-internas", "table_renderer.5-internal-constants"),
    ("table_renderer.TableRenderResult", "table_renderer.TableRenderResult"),
    ("table_renderer.7-render-table-table-block-body-font-header-font", "table_renderer.7-render-table-table-block-body-font-header-font"),
    ("table_renderer.firma", "table_renderer.signature"),
    ("table_renderer.table_block", "table_renderer.table_block"),
    ("table_renderer.comportamiento", "table_renderer.behavior"),
    ("table_renderer.devuelve", "table_renderer.returns"),
    ("table_renderer.8-helpers-privados", "table_renderer.8-private-helpers"),
    ("table_renderer.8-1-validate-table-block-table-block", "table_renderer.8-1-validate-table-block-table-block"),
    ("table_renderer.8-2-blit-text-centered", "table_renderer.8-2-blit-text-centered"),
    ("table_renderer.8-3-blit-text-aligned", "table_renderer.8-3-blit-text-aligned"),
    ("table_renderer.8-4-draw-grid", "table_renderer.8-4-draw-grid"),
    ("table_renderer.9-notas-de-mantenimiento", "table_renderer.9-maintenance-notes"),
    ("table_renderer.api-del-m-dulo-image-cache-py-es", "table_renderer.api-for-module-image_cache-py"),
    ("image_cache.parte-ii-api-interna-de-mantenimiento", "image_cache.part-ii-internal-maintenance-api"),
    ("image_cache.4-tipos-internos", "image_cache.4-internal-types"),
    ("image_cache.SurfaceInfo", "image_cache.SurfaceInfo"),
    ("image_cache._ImageKey", "image_cache._ImageKey"),
    ("image_cache.ImageCache", "image_cache.ImageCache"),
    ("image_cache.5-1-constructor", "image_cache.5-1-constructor"),
    ("image_cache.5-2-set-base-dir-base-dir", "image_cache.5-2-set-base-dir-base-dir"),
    ("image_cache.5-3-resolve-src-to-abs-path-src", "image_cache.5-3-resolve-src-to-abs-path-src"),
    ("image_cache.5-4-get-scaled-src-target-width", "image_cache.5-4-get-scaled-src-target-width"),
    ("image_cache.6-m-todos-privados", "image_cache.6-private-methods"),
    ("image_cache.6-1-load-image-abs-path", "image_cache.6-1-load-image-abs-path"),
    ("image_cache.6-2-scale-to-width-surface-target-width", "image_cache.6-2-scale-to-width-surface-target-width"),
    ("image_cache.7-consideraciones-de-mantenimiento", "image_cache.7-maintenance-considerations"),
    ("image_cache.7-1-pol-tica-de-cach", "image_cache.7-1-cache-policy"),
    ("image_cache.7-2-cambios-m-nimos-recomendados", "image_cache.7-2-recommended-minimal-changes"),
]



_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_ANCHOR_TAG_RE = re.compile(r"<a\b[^>]*>", re.IGNORECASE)
_ID_ATTR_RE = re.compile(r"""\bid\s*=\s*(?:"([^"]+)"|'([^']+)')""", re.IGNORECASE)

# Enlaces internos estilo Markdown: ](#id) o ](#id "title")
_MD_INTERNAL_LINK_RE = re.compile(r"\]\(\s*#([^)\"\s]+)(?:\s+\"[^\"]*\")?\s*\)")
# Enlaces HTML internos típicos: href="#id"
_HTML_HREF_INTERNAL_RE = re.compile(r"""href\s*=\s*(?:"\#([^"]+)"|'\#([^']+)')""", re.IGNORECASE)


def _strip_inline_code_spans(line: str) -> str:
    """Elimina segmentos de código inline delimitados por backticks (regla simple)."""
    parts = line.split("`")
    kept_parts: List[str] = []
    for index, part in enumerate(parts):
        if index % 2 == 0:
            kept_parts.append(part)
        else:
            kept_parts.append(" ")
    return "".join(kept_parts)


def _build_translation_map(from_lang: str, to_lang: str) -> Dict[str, str]:
    """Construye el diccionario from_id -> to_id, validando duplicados."""
    if from_lang not in languages:
        raise ValueError(f"Idioma origen no soportado: {from_lang}")
    if to_lang not in languages:
        raise ValueError(f"Idioma destino no soportado: {to_lang}")

    from_index = languages.index(from_lang)
    to_index = languages.index(to_lang)

    translation_map: Dict[str, str] = {}
    for pair in anchor_id_pairs:
        if from_index >= len(pair) or to_index >= len(pair):
            raise ValueError("Hay tuplas en anchor_id_pairs que no coinciden con la lista languages.")

        from_id = str(pair[from_index]).strip()
        to_id = str(pair[to_index]).strip()

        if not from_id or not to_id:
            continue

        if from_id in translation_map:
            raise ValueError(f"ID duplicado en tabla para idioma '{from_lang}': {from_id}")

        translation_map[from_id] = to_id

    return translation_map


def _replace_anchor_ids_in_line(line: str, translation_map: Dict[str, str]) -> str:
    """Sustituye id="..." en etiquetas <a ...> y enlaces internos #... en una línea."""
    def replace_anchor_tag(match: re.Match) -> str:
        tag = match.group(0)
        id_match = _ID_ATTR_RE.search(tag)
        if not id_match:
            return tag

        current_id = (id_match.group(1) or id_match.group(2) or "").strip()
        if not current_id:
            return tag

        new_id = translation_map.get(current_id)
        if not new_id:
            return tag

        # Sustitución mínima: solo el valor del atributo id detectado
        if id_match.group(1) is not None:
            return tag[:id_match.start(1)] + new_id + tag[id_match.end(1):]
        return tag[:id_match.start(2)] + new_id + tag[id_match.end(2):]

    def replace_md_internal_link(match: re.Match) -> str:
        old_id = match.group(1).strip()
        new_id = translation_map.get(old_id, old_id)
        whole = match.group(0)
        return whole.replace(f"(#{old_id}", f"(#{new_id}", 1)

    def replace_html_href_internal(match: re.Match) -> str:
        old_id = (match.group(1) or match.group(2) or "").strip()
        new_id = translation_map.get(old_id, old_id)
        if match.group(1) is not None:
            return f'href="#{new_id}"'
        return f"href='#{new_id}'"

    line = _ANCHOR_TAG_RE.sub(replace_anchor_tag, line)
    line = _MD_INTERNAL_LINK_RE.sub(replace_md_internal_link, line)
    line = _HTML_HREF_INTERNAL_RE.sub(replace_html_href_internal, line)
    return line


def Anchor_IDs_Translation(from_lang: str, to_lang: str, input_path: Path, output_path: Path) -> None:
    """Procesa un Markdown y sustituye anclas/enlaces internos del idioma from_lang al idioma to_lang."""
    translation_map = _build_translation_map(from_lang, to_lang)

    in_fence = False
    output_lines: List[str] = []

    with input_path.open("r", encoding="utf-8") as file_handle:
        for raw_line in file_handle:
            line = raw_line.rstrip("\n")

            if _FENCE_RE.match(line):
                in_fence = not in_fence
                output_lines.append(line)
                continue

            if in_fence:
                output_lines.append(line)
                continue

            # Evitar falsos positivos dentro de `inline code`
            filtered = _strip_inline_code_spans(line)
            if filtered == line:
                output_lines.append(_replace_anchor_ids_in_line(line, translation_map))
            else:
                # Si hay inline code, aplicamos reemplazo solo en el texto fuera de backticks (mínimo).
                parts = line.split("`")
                for index in range(0, len(parts), 2):
                    parts[index] = _replace_anchor_ids_in_line(parts[index], translation_map)
                output_lines.append("`".join(parts))

    with output_path.open("w", encoding="utf-8") as file_handle:
        for line in output_lines:
            file_handle.write(f"{line}\n")


def _build_arg_parser() -> argparse.ArgumentParser:
    """Parser de argumentos."""
    parser = argparse.ArgumentParser(
        description="Traduce IDs de anclas (<a id=\"...\">) y enlaces internos (#id) entre idiomas."
    )
    parser.add_argument("from_lang", help="Idioma origen (por ejemplo: es).")
    parser.add_argument("to_lang", help="Idioma destino (por ejemplo: en).")
    parser.add_argument("markdown_in", help="Fichero Markdown de entrada.")
    parser.add_argument("markdown_out", help="Fichero Markdown de salida.")
    return parser


def main() -> int:
    """Punto de entrada."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    input_path = Path(args.markdown_in).expanduser()
    output_path = Path(args.markdown_out).expanduser()

    if not input_path.exists():
        print(f"ERROR: No existe el fichero de entrada: {input_path}", file=sys.stderr)
        return 2

    if output_path.exists():
        print(f"ERROR: El fichero de salida ya existe: {output_path}", file=sys.stderr)
        return 4

    try:
        Anchor_IDs_Translation(args.from_lang, args.to_lang, input_path, output_path)

    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

