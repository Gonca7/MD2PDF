import re

from md2pdf.parser.ast import *


HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
RULE_RE = re.compile(r"^ {0,3}(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})$")
BLOCKQUOTE_RE = re.compile(r"^ {0,3}> ?")
LIST_ITEM_RE = re.compile(r"^( {0,3})([-+*]|\d{1,9}[.)])[ \t]+(.*)$")
CHECKBOX_RE = re.compile(r"^\[([ xX])\][ \t]+(.*)$")
TABLE_SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")


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

                quote_document = self.parse("\n".join(quote_lines))
                document.children.append(
                    BlockQuote(children=quote_document.children)
                )
                continue


            # Thematic break
            if RULE_RE.match(line):
                flush_paragraph()
                document.children.append(ThematicBreak())

                i += 1
                continue


            # Table
            if (
                i + 1 < len(lines)
                and "|" in line
                and self._is_table_separator(lines[i + 1])
            ):
                flush_paragraph()

                header_cells = self._split_table_row(line)
                separator_cells = self._split_table_row(lines[i + 1])

                if len(header_cells) == len(separator_cells):
                    alignments = [
                        "center" if cell.startswith(":") and cell.endswith(":")
                        else "left" if cell.startswith(":")
                        else "right" if cell.endswith(":")
                        else None
                        for cell in separator_cells
                    ]

                    header = TableRow(
                        cells=[
                            TableCell(children=[RawText(cell)])
                            for cell in header_cells
                        ]
                    )

                    rows: list[TableRow] = []
                    i += 2

                    while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                        cells = self._split_table_row(lines[i])

                        # Normalize row width to match the header.
                        cells = (cells + [""] * len(header_cells))[:len(header_cells)]

                        rows.append(
                            TableRow(
                                cells=[
                                    TableCell(children=[RawText(cell)])
                                    for cell in cells
                                ]
                            )
                        )
                        i += 1

                    document.children.append(
                        TableBlock(
                            header=header,
                            rows=rows,
                            alignments=alignments,
                        )
                    )
                    continue



            # List
            list_match = LIST_ITEM_RE.match(line)

            if list_match:
                flush_paragraph()

                list_block, i = self._parse_list(lines, i)
                document.children.append(list_block)
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


            # Paragraph line
            paragraph_lines.append(line)
            i += 1

        flush_paragraph()

        return document

    def _parse_list(
        self,
        lines: list[str],
        start_index: int,
    ) -> tuple[ListBlock, int]:
        """Parse a list, including nested block content."""
        first_match = LIST_ITEM_RE.match(lines[start_index])
        if first_match is None:
            raise ValueError("Expected a list item")

        indentation = len(first_match.group(1))
        first_marker = first_match.group(2)
        ordered = first_marker[0].isdigit()
        list_marker = first_marker[-1] if ordered else first_marker
        start = int(first_marker[:-1]) if ordered else 1

        # The column at which the item's content begins.
        content_indent = indentation + len(first_marker) + 1

        items: list[ListItem] = []
        index = start_index

        while index < len(lines):
            match = LIST_ITEM_RE.match(lines[index])

            if match is None:
                break

            current_indent = len(match.group(1))
            marker = match.group(2)
            current_ordered = marker[0].isdigit()
            current_list_marker = marker[-1] if current_ordered else marker

            if (
                current_indent != indentation
                or current_ordered != ordered
                or current_list_marker != list_marker
            ):
                break

            item_content = match.group(3)
            checked: bool | None = None

            checkbox_match = CHECKBOX_RE.match(item_content)

            if checkbox_match:
                checked = checkbox_match.group(1).lower() == "x"
                item_content = checkbox_match.group(2)

            item_lines = [item_content]
            index += 1

            # Collect paragraphs, nested lists and quotes belonging to this item.
            while index < len(lines):
                line = lines[index]

                if not line.strip():
                    # Preserve blank lines only when followed by indented content.
                    next_index = index + 1
                    while (
                        next_index < len(lines)
                        and not lines[next_index].strip()
                    ):
                        next_index += 1

                    if next_index < len(lines):
                        next_line = lines[next_index]
                        next_match = LIST_ITEM_RE.match(next_line)

                        if next_match and len(next_match.group(1)) == indentation:
                            break

                        leading_spaces = len(next_line) - len(next_line.lstrip(" "))

                        if leading_spaces >= content_indent:
                            item_lines.append("")
                            index += 1
                            continue

                    break

                nested_match = LIST_ITEM_RE.match(line)

                # A same-level list item starts the next item.
                if nested_match and len(nested_match.group(1)) == indentation:
                    break

                leading_spaces = len(line) - len(line.lstrip(" "))

                if leading_spaces < content_indent:
                    break

                # Remove the indentation belonging to this item's content.
                item_lines.append(line[content_indent:])
                index += 1

            item_document = self.parse("\n".join(item_lines))
            items.append(
                ListItem(
                    children=item_document.children,
                    checked=checked,
                )
            )

        return ListBlock(
            ordered=ordered,
            items=items,
            start=start,
        ), index

    @staticmethod
    def _split_table_row(line: str) -> list[str]:
        """Split a Markdown table row on unescaped pipe characters."""
        line = line.strip()

        if line.startswith("|"):
            line = line[1:]

        if line.endswith("|") and not line.endswith(r"\|"):
            line = line[:-1]

        cells: list[str] = []
        current: list[str] = []
        escaped = False

        for char in line:
            if char == "|" and not escaped:
                cells.append("".join(current).strip())
                current = []
            else:
                current.append(char)

            if char == "\\" and not escaped:
                escaped = True
            else:
                escaped = False

        cells.append("".join(current).strip())
        return cells


    @classmethod
    def _is_table_separator(cls, line: str) -> bool:
        """Return whether a line is a valid table separator row."""
        cells = cls._split_table_row(line)
        return bool(cells) and all(
            TABLE_SEPARATOR_RE.fullmatch(cell) for cell in cells
        )