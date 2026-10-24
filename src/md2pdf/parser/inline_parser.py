from md2pdf.parser.ast import Inline, Emphasis, Strong, Text
from md2pdf.parser.tokens import Token, TokenType, Tokens
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