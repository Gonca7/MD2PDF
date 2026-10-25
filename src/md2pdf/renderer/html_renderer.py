from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import base64
import html

from md2pdf.parser.ast import *
from md2pdf.renderer.mermaid_renderer import render_mermaid


class _HTMLSanitizer(HTMLParser):
    """Allow a limited set of safe HTML elements and attributes."""

    ALLOWED_TAGS = {
        "a", "abbr", "b", "blockquote", "br", "caption",
        "code", "dd", "del", "details", "div", "dl", "dt",
        "em", "figcaption", "figure", "h1", "h2", "h3",
        "h4", "h5", "h6", "hr", "i", "img", "li", "ol",
        "p", "pre", "s", "small", "span", "strong", "sub",
        "summary", "sup", "table", "tbody", "td", "th",
        "thead", "tr", "u", "ul",
    }

    VOID_TAGS = {"br", "hr", "img"}

    DROP_CONTENT_TAGS = {
        "script", "style", "iframe", "object", "embed",
        "form", "svg", "math",
    }

    ALLOWED_ATTRIBUTES = {
        "a": {"href", "title", "id"},
        "img": {"src", "alt", "title", "width", "height"},
        "td": {"colspan", "rowspan"},
        "th": {"colspan", "rowspan"},
        "ol": {"start"},
        "details": {"open"},
    }

    def __init__(self, safe_url):
        super().__init__(convert_charrefs=False)
        self.safe_url = safe_url
        self.output: list[str] = []
        self._suppressed: list[str] = []

    def handle_starttag(self, tag, attrs):
        if self._suppressed:
            if tag in self.DROP_CONTENT_TAGS:
                self._suppressed.append(tag)
            return

        if tag in self.DROP_CONTENT_TAGS:
            self._suppressed.append(tag)
            return

        if tag not in self.ALLOWED_TAGS:
            return

        safe_attrs = []

        for name, value in attrs:
            if value is None:
                continue

            if name.startswith("on") or name not in self.ALLOWED_ATTRIBUTES.get(tag, set()):
                continue

            if name in {"href", "src"}:
                value = self.safe_url(value)
                if value is None:
                    continue

            if name in {"width", "height", "colspan", "rowspan", "start"}:
                if not value.isdigit():
                    continue

            safe_attrs.append(
                f' {name}="{escape(value, quote=True)}"'
            )

        self.output.append(f"<{tag}{''.join(safe_attrs)}>")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID_TAGS and not self._suppressed:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        
        if tag.lower() == "br":
            self.output.append("</br>")
            return
        
        if self._suppressed:
            if tag == self._suppressed[-1]:
                self._suppressed.pop()
            return

        if tag in self.ALLOWED_TAGS and tag not in self.VOID_TAGS:
            self.output.append(f"</{tag}>")

    def handle_data(self, data):
        if not self._suppressed:
            self.output.append(escape(data))

    def handle_entityref(self, name):
        if not self._suppressed:
            self.output.append(f"&{name};")

    def handle_charref(self, name):
        if not self._suppressed:
            self.output.append(f"&#{name};")

    def sanitize(self, source: str) -> str:
        self.feed(source)
        self.close()
        return "".join(self.output)




class HTMLRenderer:
    """Convert a resolved Markdown AST into an HTML document."""


    def __init__(self, css_path: str | Path | None = None) -> None:
        self.css_path = Path(css_path) if css_path is not None else None

    def render(self, document: Document) -> str:
        body = "\n".join(
            self._render_block(block) for block in document.children
        )

        css = ""
        if self.css_path is not None:
            stylesheet = self.css_path.read_text(encoding="utf-8")
            css = f"<style>\n{stylesheet}\n</style>\n"

        return (
            "<!doctype html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '  <meta charset="utf-8">\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "  <title>Markdown document</title>\n"
            f"  {css}"
            "</head>\n"
            f"<body>\n{body}\n</body>\n"
            "</html>"
        )

    def _render_block(self, node: Block) -> str:

        if isinstance(node, HTMLBlock):
            return self._sanitize_html(node.content)

        if isinstance(node, RawBlock):
            raise ValueError(
                f"Unresolved RawBlock: {node.content!r}"
            )

        if isinstance(node, Paragraph):
            return f"<p>{self._render_inlines(node.children)}</p>"

        if isinstance(node, Heading):
            if not 1 <= node.level <= 6:
                raise ValueError(
                    f"Invalid heading level: {node.level}"
                )

            identifier = ""
            if node.id is not None:
                identifier = f' id="{escape(node.id, quote=True)}"'

            content = self._render_inlines(node.children)
            return f"<h{node.level}{identifier}>{content}</h{node.level}>"

        if isinstance(node, CodeBlock):
            if node.language and node.language.lower() == "mermaid":
                svg = render_mermaid(node.content)
                svg_data = base64.b64encode(svg.encode("utf-8")).decode("ascii")

                return (
                    '<div class="mermaid-diagram">'
                    f'<img src="data:image/svg+xml;base64,{svg_data}" '
                    'alt="Mermaid diagram">'
                    '</div>'
                )

            language_class = (
                f' class="language-{html.escape(node.language)}"'
                if node.language
                else ""
            )

            return (
                f"<pre><code{language_class}>"
                f"{html.escape(node.content)}"
                "</code></pre>"
            )

        if isinstance(node, BlockQuote):
            content = "\n".join(
                self._render_block(child) for child in node.children
            )
            return f"<blockquote>\n{content}\n</blockquote>"

        if isinstance(node, ListBlock):
            is_checklist = (
                not node.ordered
                and bool(node.items)
                and all(item.checked is not None for item in node.items)
            )

            tag = "ol" if node.ordered else "ul"
            start = ""

            if is_checklist:
                start = ' class="checklist"'

            if node.ordered and node.start != 1:
                start = f' start="{node.start}"'

            items = "\n".join(
                self._render_list_item(item) for item in node.items
            )
            return f"<{tag}{start}>\n{items}\n</{tag}>"

        if isinstance(node, TableBlock):
            return self._render_table(node)
        
        if isinstance(node, ThematicBreak):
            return "<hr>"

        raise TypeError(
            f"Unsupported block node: {type(node).__name__}"
        )

    def _render_table(self, table: TableBlock) -> str:
        def render_cell(cell: TableCell, index: int, tag: str) -> str:
            alignment = table.alignments[index]

            style = (
                f' style="text-align: {alignment}"'
                if alignment is not None
                else ""
            )

            content = self._render_inlines(cell.children)
            return f"<{tag}{style}>{content}</{tag}>"

        header = "".join(
            render_cell(cell, index, "th")
            for index, cell in enumerate(table.header.cells)
        )

        body_rows = []

        for row in table.rows:
            cells = "".join(
                render_cell(cell, index, "td")
                for index, cell in enumerate(row.cells)
            )
            body_rows.append(f"<tr>{cells}</tr>")

        body = "\n".join(body_rows)

        return (
            "<table>\n"
            f"<thead><tr>{header}</tr></thead>\n"
            f"<tbody>\n{body}\n</tbody>\n"
            "</table>"
        )

    def _render_list_item(self, item: ListItem) -> str:
        content = "\n".join(
            self._render_block(child) for child in item.children
        )

        if item.checked is not None and item.children:
            first_child = item.children[0]

            if isinstance(first_child, Paragraph):
                checkbox = (
                    '<input type="checkbox" disabled checked> '
                    if item.checked
                    else '<input type="checkbox" disabled> '
                )

                paragraph = self._render_block(first_child)
                paragraph = paragraph.replace(
                    "<p>",
                    f"<p>{checkbox}",
                    1,
                )

                remaining = "\n".join(
                    self._render_block(child)
                    for child in item.children[1:]
                )

                content = "\n".join(
                    part for part in (paragraph, remaining) if part
                )

        return f"<li>{content}</li>"

    def _render_inlines(self, nodes: list[Inline]) -> str:
        return "".join(self._render_inline(node) for node in nodes)

    def _render_inline(self, node: Inline) -> str:

        if isinstance(node, InlineHTML):
            return self._sanitize_html(node.content)

        if isinstance(node, RawText):
            raise ValueError(
                f"Unresolved RawText: {node.content!r}"
            )

        if isinstance(node, Text):
            return escape(node.content)

        if isinstance(node, Strikethrough):
            return f"<del>{self._render_inlines(node.children)}</del>"

        if isinstance(node, Emphasis):
            return f"<em>{self._render_inlines(node.children)}</em>"

        if isinstance(node, Strong):
            return f"<strong>{self._render_inlines(node.children)}</strong>"

        if isinstance(node, InlineCode):
            return f"<code>{escape(node.content)}</code>"

        if isinstance(node, Link):
            href = self._safe_url(node.url)

            if href is None:
                return self._render_inlines(node.children)

            title = ""
            if node.title is not None:
                title = f' title="{escape(node.title, quote=True)}"'

            label = self._render_inlines(node.children)
            return (
                f'<a href="{escape(href, quote=True)}"{title}>'
                f"{label}</a>"
            )

        if isinstance(node, Image):
            src = self._safe_url(node.src)

            if src is None:
                return escape(node.alt)

            title = ""
            if node.title is not None:
                title = f' title="{escape(node.title, quote=True)}"'

            return (
                f'<img src="{escape(src, quote=True)}" '
                f'alt="{escape(node.alt, quote=True)}"{title}>'
            )

        raise TypeError(
            f"Unsupported inline node: {type(node).__name__}"
        )

    @staticmethod
    def _safe_url(url: str) -> str | None:
        """Reject active-content URL schemes such as javascript:."""
        value = url.strip()

        if not value or any(ord(char) < 32 for char in value):
            return None

        parsed = urlsplit(value)

        if parsed.scheme and parsed.scheme.lower() not in {
            "http", "https", "mailto"
        } or parsed.scheme and parsed.scheme.lower() in {"script"}:
            return None

        if value.startswith("//"):
            return None

        return value

    def _sanitize_html(self, source: str) -> str:
        sanitizer = _HTMLSanitizer(self._safe_url)
        return sanitizer.sanitize(source)
