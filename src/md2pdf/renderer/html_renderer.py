from html import escape
from urllib.parse import urlsplit

from md2pdf.parser.ast import *

class HTMLRenderer:
    """Convert a resolved Markdown AST into an HTML document."""

    def render(self, document: Document) -> str:
        body = "\n".join(
            self._render_block(block) for block in document.children
        )

        return (
            "<!doctype html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '  <meta charset="utf-8">\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "  <title>Markdown document</title>\n"
            "</head>\n"
            f"<body>\n{body}\n</body>\n"
            "</html>"
        )

    def _render_block(self, node: Block) -> str:
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
            content = escape(node.content)

            if node.language:
                language = escape(node.language, quote=True)
                content = (
                    f'<code class="language-{language}">'
                    f"{content}</code>"
                )
            else:
                content = f"<code>{content}</code>"

            return f"<pre>{content}</pre>"

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
        
        if isinstance(node, ThematicBreak):
            return "<hr>"

        raise TypeError(
            f"Unsupported block node: {type(node).__name__}"
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
        if isinstance(node, RawText):
            raise ValueError(
                f"Unresolved RawText: {node.content!r}"
            )

        if isinstance(node, Text):
            return escape(node.content)

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
