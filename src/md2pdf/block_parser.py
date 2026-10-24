import re

from md2pdf.ast import (
    BlockQuote,
    CodeBlock,
    Document,
    Heading,
    Paragraph,
    RawBlock,
    RawText,
    ThematicBreak,
)


HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
RULE_RE = re.compile(r"^ {0,3}(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})$")
BLOCKQUOTE_RE = re.compile(r"^ {0,3}> ?")


class BlockParser:
    """
    Parses Markdown block elements into an AST.
    """

    def parse(self, source: str) -> Document:
        """
        Parse Markdown source into a Document AST.
        """
        lines = source.splitlines()
        document = Document()
        paragraph_lines: list[str] = []

        def flush_paragraph() -> None:
            """Append the accumulated paragraph to the document."""
            if paragraph_lines:
                content = " ".join(
                    line.strip() for line in paragraph_lines
                )

                document.children.append(
                    Paragraph(children=[RawText(content)])
                )

                paragraph_lines.clear()

        i = 0

        while i < len(lines):
            line = lines[i]

            # Empty line
            if not line.strip():
                flush_paragraph()
                i += 1
                continue

            # Fenced code block
            fence_match = FENCE_RE.match(line)
            if fence_match:
                flush_paragraph()

                fence = fence_match.group(1)
                info = fence_match.group(2).strip()
                language = info.split(maxsplit=1)[0] if info else None

                code_lines: list[str] = []
                i += 1

                while i < len(lines):
                    candidate = lines[i]

                    closing_fence = re.match(
                        rf"^ {{0,3}}{re.escape(fence[0])}"
                        rf"{{{len(fence)},}}[ \t]*$",
                        candidate,
                    )

                    if closing_fence:
                        break

                    code_lines.append(candidate)
                    i += 1

                document.children.append(
                    CodeBlock(
                        content="\n".join(code_lines),
                        language=language,
                    )
                )

                if i < len(lines):
                    i += 1

                continue


            # Collect a blockquote, leaving its inner blocks unparsed.
            if BLOCKQUOTE_RE.match(line):
                flush_paragraph()
                quote_lines: list[str] = []

                while i < len(lines):
                    match = BLOCKQUOTE_RE.match(lines[i])
                    if not match:
                        break

                    quote_lines.append(lines[i][match.end():])
                    i += 1

                document.children.append(
                    BlockQuote(
                        children=[
                            RawBlock(content="\n".join(quote_lines))
                        ]
                    )
                )
                continue



            # Heading
            heading_match = HEADING_RE.match(line)

            if heading_match:
                flush_paragraph()

                document.children.append(
                    Heading(
                        level=len(heading_match.group(1)),
                        children=[RawText(heading_match.group(2))],
                    )
                )

                i += 1
                continue

            # Thematic break
            if RULE_RE.match(line):
                flush_paragraph()
                document.children.append(ThematicBreak())

                i += 1
                continue

            # Paragraph line
            paragraph_lines.append(line)
            i += 1

        flush_paragraph()

        return document