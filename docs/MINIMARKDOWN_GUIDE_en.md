# MiniMarkdown Guide (help_core_pygame)

> 🔙 Back to index: [INDEX_en.md](INDEX_en.md)

> **Goal**  
> This document describes **only** the supported Markdown subset (“MiniMarkdown”) implemented by the internal
> parser `_MiniMarkdown` and used by the help system in `help_core_pygame`.

MiniMarkdown is designed to be:

- **Portable** (no external dependencies besides Pygame on the viewer side).
- **Predictable** (simple rules; few “magic” edge cases).
- **Sufficient** for good-looking help: headings, paragraphs, lists, code, links, anchors, block images and simple tables.

---

## Table of contents

- [1. Core concepts](#core-concepts)
- [2. Text normalization](#text-normalization)
- [3. Supported blocks](#supported-blocks)
  - [3.1 ATX headings](#atx-headings)
  - [3.2 Paragraphs](#paragraphs)
  - [3.3 Horizontal rule](#horizontal-rule)
  - [3.4 Lists (UL and OL)](#lists-ul-and-ol)
  - [3.5 Code blocks (fences)](#code-blocks-fences)
  - [3.6 HTML comments](#html-comments)
  - [3.7 HTML anchors](#html-anchors)
  - [3.8 Images as blocks](#images-as-blocks)
  - [3.9 Tables (reduced GFM)](#tables-reduced-gfm)
- [4. Inline: tokenization inside text](#inline-tokenization-inside-text)
  - [4.1 Emphasis](#emphasis)
  - [4.2 Inline code](#inline-code)
  - [4.3 Links: Markdown and raw URLs](#links-markdown-and-raw-urls)
- [5. What is NOT supported](#what-is-not-supported)
- [6. Parser output schema](#parser-output-schema)
  - [6.1 Blocks](#blocks)
  - [6.2 Inline runs](#inline-runs)
- [7. Practical tips](#practical-tips)
- [8. Compatibility checklist (for authors)](#compatibility-checklist-for-authors)

---

<a id="core-concepts"></a>
## 1. Core concepts

MiniMarkdown works in two phases:

1) **Block parsing** (`parse()`): recognizes “large” structures (headings, lists, code, tables, etc.)
and produces a list of **blocks** with `type`.

2) **Inline tokenization** (`tokenize_inline()`): inside a text (for example a paragraph or a list item),
it splits into fragments (“runs”) with attributes such as bold, italic, code and link.

In general:

- If something is a **block**, it is decided in `parse()`.
- If something is **inside text** (bold, italic, links, inline code), it is decided in `tokenize_inline()`.

---

<a id="text-normalization"></a>
## 2. Text normalization

Before parsing, it is recommended to normalize the text:

- `	` → converted to spaces according to `tab_size`.
- `
` and `` → converted to `
`.

This prevents platform differences and makes parsing more predictable.

> Practical note: in the typical viewer flow, the text is normalized before parsing, so end users
> do not have to do it manually.

---

<a id="supported-blocks"></a>
## 3. Supported blocks

<a id="atx-headings"></a>
### 3.1 ATX headings

ATX headings with `#` from 1 to 6 are supported:

```text
# H1
## H2
### H3
#### H4
##### H5
###### H6
```

The parser generates `h1`...`h6` blocks with a `text` field.

**Rule**: there must be at least one space after the hashes.

---

<a id="paragraphs"></a>
### 3.2 Paragraphs

A paragraph is “whatever remains” when one or more lines are **not** a recognized block.

Characteristics:

- A paragraph may span multiple lines.
- A paragraph ends when an empty line appears or when another block starts (heading, list, table, fence, etc.).

Example:

```text
This is a paragraph split into two lines.
It is still the same paragraph.

This is another paragraph.
```

---

<a id="horizontal-rule"></a>
### 3.3 Horizontal rule

The exact line `---` (with optional surrounding spaces) is interpreted as a horizontal rule:

```text
---
```

It generates an `hr` block.

---

<a id="lists-ul-and-ol"></a>
### 3.4 Lists (UL and OL)

Supported:

- **Bulleted lists (UL)** using `- ` or `* `.
- **Numbered lists (OL)** using `N. ` (e.g. `1. `, `2. `).

Nesting is computed from indentation (spaces):

- `indent_per_level_spaces`: how many spaces equal one nesting level.
- `max_list_nesting`: maximum depth (level saturates if exceeded).

UL example:

```text
- Level 0
  - Level 1 (2 spaces if indent_per_level_spaces=2)
    - Level 2
```

OL example:

```text
1. Item 1
2. Item 2
   1. Subitem
```

**Important**:

- Inside lists, full-line HTML comments and `<!-- ... -->` blocks are **ignored** (they do not break the list).
- MiniMarkdown does not implement full Markdown “continuations” (multi-line paragraphs inside a list item using
  indented lines). List items are single-line text items.

---

<a id="code-blocks-fences"></a>
### 3.5 Code blocks (fences)

Triple-backtick fences are supported:

```text
```python
print("hello")
```
```

Notes:

- A fence is detected by a line that starts with ``` (it may carry extra text like `python`), but:
  - The language is **not interpreted** (ignored; used only as open/close).
- Inside the fence, the content is preserved as-is, including empty lines.
- If a fence is not closed by end-of-file, a `code` block is still emitted with the accumulated content.

> Note: “4 spaces indented code” is **not supported** in the current state.

---

<a id="html-comments"></a>
### 3.6 HTML comments

HTML comments are supported as **blocks** in two forms:

1) **Single full line**:

```text
<!-- comment -->
```

2) **Multi-line block**:

```text
<!--
line 1
line 2
-->
```

The parser produces `comment` blocks with `text`.

Usage recommendation:

- For “reliable” comments, use **a full line**.
- Inline comments inside a text line are **not** treated as comments; they remain normal text.

---

<a id="html-anchors"></a>
### 3.7 HTML anchors

HTML anchors are supported when the anchor occupies a **full line**:

```text
<a id="my_anchor"></a>
```

It generates an `anchor` block with an `id` field.

Typical uses:

- Build a manual table of contents.
- Create internal links using `#my_anchor`.

---

<a id="images-as-blocks"></a>
### 3.8 Images as blocks

Markdown images are supported as **blocks** when they occupy a full line:

```text
![alt text](path/or/url)
```

The parser emits:

- `type: "img"`
- `alt`: alternative text
- `src`: path or URL

Limitations:

- No support for **inline** images inside paragraphs.
- No support for complex syntax with nested parentheses inside the path.
- Use inside lists is not covered: images are treated as independent blocks.

---

<a id="tables-reduced-gfm"></a>
### 3.9 Tables (reduced GFM)

MiniMarkdown includes support for reduced GFM-style tables as blocks.

Example:

```text
| Col A | Col B |
|------:|:-----:|
|  123  | hello |
```

Notes:

- The table is detected **before** forming a paragraph, so a table “stuck” to text is still treated as a table.
- Header separator alignments are supported:
  - `:---` left, `---:` right, `:---:` centered (as per internal implementation).
- “Irregular” cases (rows with fewer/more cells) are handled robustly to avoid breaking rendering.

---

<a id="inline-tokenization-inside-text"></a>
## 4. Inline: tokenization inside text

Inline tokenization applies to texts such as:

- `p.text` (paragraphs)
- `hN.text` (headings)
- `items[].text` in lists

Precedence rules:

1) **Inline code** (between backticks) is protected first so it is not processed as emphasis or links.
2) Emphasis is applied (***, **, *).
3) Markdown links `[text](target)` are expanded (outside code).
4) Raw URLs `http(s)://...` are detected (outside code and outside already-marked links).

---

<a id="emphasis"></a>
### 4.1 Emphasis

Supported:

- `***text***` → bold + italic
- `**text**` → bold
- `*text*` → italic

Important rule:

- To avoid false positives like `price*2`, `**` and `*` require word boundaries (not glued to letters/digits).
- `***` is more permissive to reduce cases where it is glued to other words.

---

<a id="inline-code"></a>
### 4.2 Inline code

Supported:

```text
Use `inline code` in a sentence.
```

Effects:

- Text between backticks is marked as a run with `code=true`.
- Inside that segment, no links or emphasis are detected.

Known limitation (usage):

- If you nest `inline code` inside bold/italic fragments, the final result depends on the renderer;
  the practical recommendation is **do not nest** inline code inside emphasis.

---

<a id="links-markdown-and-raw-urls"></a>
### 4.3 Links: Markdown and raw URLs

Two forms are supported:

#### A) Basic Markdown links

```text
[Visible text](target)
```

- Images `![...](...)` are excluded.
- Runs are emitted with `link=true`, `href=target`, and text = `Visible text`.

Targets may be:

- URL: `https://example.com/...`
- Internal anchor: `#my_anchor`

#### B) Raw URL autolink

Detects URLs inside text:

```text
Visit https://www.python.org and also http://example.com/test?x=1#y.
```

Rules:

- Detects `http://` and `https://` followed by non-space characters.
- Trims common trailing punctuation `.,;:!?)]}"'` so it does not become part of the URL.
  - Special case: `)` is trimmed only if there are extra closing parentheses.

**Negative cases** (must NOT be linked):

- URLs inside inline code: `` `https://www.python.org/` ``
- URLs inside fenced code blocks

---

<a id="what-is-not-supported"></a>
## 5. What is NOT supported

MiniMarkdown is intentionally limited. It does not support (non-exhaustive):

- Full Markdown (CommonMark / full GFM).
- Blockquotes `>`.
- Reference links `[a][b]`.
- Inline images (inside paragraphs).
- 4-space indented code blocks.
- Multi-line list items (complex continuations).
- Parsing fence language (```python) as structured metadata.
- Arbitrary HTML (only anchors and comments in specific formats are supported).

---

<a id="parser-output-schema"></a>
## 6. Parser output schema

<a id="blocks"></a>
### 6.1 Blocks

`parse(text)` returns a list of dictionaries. Main types:

- Headings:
  - `{"type": "h1"|"h2"|...|"h6", "text": str}`

- Paragraph:
  - `{"type": "p", "text": str}`

- Horizontal rule:
  - `{"type": "hr"}`

- Lists:
  - UL:
    - `{"type": "ul", "items": [{"level": int, "text": str}, ...]}`
  - OL:
    - `{"type": "ol", "items": [{"level": int, "num": int, "text": str}, ...]}`

- Code:
  - `{"type": "code", "text": str}`

- Comment:
  - `{"type": "comment", "text": str}`

- Anchor:
  - `{"type": "anchor", "id": str}`

- Image:
  - `{"type": "img", "alt": str, "src": str}`

- Table:
  - `{"type": "table", ...}` (structure handled by the tables module)

---

<a id="inline-runs"></a>
### 6.2 Inline runs

`tokenize_inline(text)` returns a list of runs with this schema:

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

Rules:

- If `code=true`, the fragment is not processed as emphasis or link.
- If `link=true`, `href` holds the destination (URL or `#anchor`).

---

<a id="practical-tips"></a>
## 7. Practical tips

- **Build a manual index** using HTML anchors:
  - `<a id="TOC_ID"></a>` and links `[Back](#TOC_ID)`.
- **Always use fences** for code: do not rely on “4 spaces”.
- **Keep tables and images as blocks**:
  - Although tables may be detected when “stuck” to text, it is clearer to keep an empty line before/after.
- **Comments**:
  - For author notes, use `<!-- ... -->` as a **full line**.
  - Avoid comments “in the middle” of a line: they will be rendered as text.
- **Links**:
  - If you place a URL followed by punctuation or parentheses, MiniMarkdown attempts to trim it; still, separating by space is safer.

---

<a id="compatibility-checklist-for-authors"></a>
## 8. Compatibility checklist (for authors)

Before considering a text “ready”:

- [ ] Headings use `#` + space (not `#Title`).
- [ ] Code is always fenced with ``` and does not rely on indentation.
- [ ] Images are on a full line `![alt](src)`.
- [ ] Anchors are on a full line `<a id="..."></a>`.
- [ ] Important comments are on a full line `<!-- ... -->`.
- [ ] Tables have proper header + separator line.
- [ ] Internal links point to existing IDs (`#...`).
- [ ] No critical URLs are inside `inline code` (they will not be linked).

> 🔙 Back to index: [INDEX_en.md](INDEX_en.md)
