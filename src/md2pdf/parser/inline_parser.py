import re

from md2pdf.parser.ast import Inline, Emphasis, Strong, Text, Link
from md2pdf.parser.tokens import Token, TokenType, Tokens
from md2pdf.parser.scanner import Scanner
from md2pdf.utils import tt2node

class InlineParser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.position = 0

    def parse(self) -> list[Inline]:
        return self.parse_until()

    def parse_until(
        self,
        closing_type: TokenType | None = None,
    ) -> list[Inline]:
        nodes: list[Inline] = []

        while self.position < len(self.tokens):
            token = self.tokens[self.position]

            if token.type == TokenType.EOF:
                break

            if token.type == closing_type:
                self.position += 1
                return nodes

            if (
                token.type == TokenType.LINK_TEXT
                and self.position + 1 < len(self.tokens)
                and self.tokens[self.position + 1].type
                == TokenType.LINK_DESTINATION
            ):
                link = self.parse_link()

                if link is not None:
                    nodes.append(link)
                continue

            if token.type == TokenType.TEXT:
                nodes.append(Text(token.value))
                self.position += 1
                continue

            if any(token.type == ttype for _, ttype, _ in Tokens):
                node = self.parse_delimited(token.type)

                if node is not None:
                    nodes.append(node)
                continue

            # Preserve unrecognized tokens as literal text.
            nodes.append(Text(token.value))
            self.position += 1

        return nodes

    def parse_link(self) -> Link | Text | None:
        label_token = self.tokens[self.position]
        destination_token = self.tokens[self.position + 1]

        parsed_destination = self._parse_destination(
            destination_token.value
        )

        if parsed_destination is None:
            self.position += 2
            return Text(
                f"[{label_token.value}]"
                f"({destination_token.value})"
            )

        url, title = parsed_destination

        # Parse the label with the same inline grammar. This allows
        # links to contain strong text or emphasis.
        label_tokens = Scanner(label_token.value).scan_tokens()
        children = InlineParser(label_tokens).parse()

        self.position += 2

        return Link(
            children=children,
            url=url,
            title=title,
        )

    @staticmethod
    def _parse_destination(
        value: str,
    ) -> tuple[str, str | None] | None:
        """Parse a URL and an optional quoted or parenthesized title."""
        pattern = (
            r'\s*(?:<([^>]*)>|(\S+?))'
            r'(?:\s+(?:"([^"]*)"|\'([^\']*)\'|\(([^)]*)\)))?\s*'
        )

        match = re.fullmatch(pattern, value)

        if match is None:
            return None

        url = match.group(1) or match.group(2) or ""
        title = (
            match.group(3)
            if match.group(3) is not None
            else match.group(4)
            if match.group(4) is not None
            else match.group(5)
        )

        return url, title

    def parse_delimited(self, delimiter_type: TokenType) -> Inline | None:
        opening_position = self.position
        self.position += 1

        children = self.parse_until(delimiter_type)

        # No matching closing delimiter was found.
        if (
            self.position >= len(self.tokens)
            or self.tokens[self.position - 1].type != delimiter_type
        ):
            self.position = opening_position + 1
            return Text(self.tokens[opening_position].value)

        node_class = tt2node(delimiter_type)
        if node_class is None:
            return None

        return node_class(children)