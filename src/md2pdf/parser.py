import re
from md2pdf.ast import *


HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")     # ``` or ~~~ to identify codeblocks
RULE_RE = re.compile(r"^ {0,3}(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})$")   # finds line breaks


def parse_md(source: str) -> Document:

    '''
        Parses plain .md text onto an AST
        Args:
            - source [str] : plain markdown text
    '''

    lines = source.splitlines()
    document = Document()
    paragraph_lines : list[str] = []


    def flush_paragraph():

        '''
            Append paragraph onto document object
        '''
        if paragraph_lines:

            content = " ".join(line.strip() for line in paragraph_lines)
            document.children.append(
                Paragraph(children=[Text(content=content)])
            )

            paragraph_lines.clear()

    i=0
    while i < len(lines):

        line = line[i]

        # Empty line
        if not line.strip():
            flush_paragraph()
            i+=1
            continue


        # Fence
        fence_match = FENCE_RE.match(line)
        if fence_match:
            flush_paragraph()

            fence = fence_match.group(1)
            info = fence_match.group(2).strip()
            language = info.split(maxsplit=1, sep=" ")[0] if info else None

            code_lines : list[str] = []

            i+=1
            while i < len(lines):
                candidate = lines[i]

                if re.match(
                    rf"^ {{0,3}}{re.escape(fence[0])}"
                    rf"{{{len(fence)},}}[ \t]*$",
                    candidate,
                ):
                    break

                code_lines.append(candidate)
                i+=1

            document.children.append(
                CodeBlock(
                    content="\n".join(code_lines),
                    language=language
                )
            )

            if i < len(lines):
                i+=1
                continue


        # Heading
        heading_match = HEADING_RE.match(line)
        if heading_match:
            flush_paragraph()

            document.children.append(
                Heading(
                    level=len(heading_match.group(1)),
                    children=[Text(heading_match.group(2))]
                )
            )

            i+=1
            continue

        # Line Break
        rule_match = RULE_RE.match(line)
        if rule_match:
            flush_paragraph()

            document.children.append(
                ThematicBreak()
            )

            i+=1
            continue

        # If its nothin append as a paragraph line
        paragraph_lines.append(line)
        i+=1
        continue

    flush_paragraph()
    return document