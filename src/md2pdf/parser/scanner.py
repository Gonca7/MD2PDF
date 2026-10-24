from md2pdf.parser.tokens import Token, TokenType, Tokens


class Scanner:
    def __init__(self, source: str) -> None:
        self.source = source
        self.position = 0
        self.tokens: list[Token] = []



    def scan_tokens(self) -> list[Token]:
        while self.position < len(self.source):
            self.scan_token()

        self.tokens.append(
            Token(
                type=TokenType.EOF,
                value="",
                position=self.position,
            )
        )

        return self.tokens

    def scan_token(self) -> None:

        for delimiter, token_type, _ in Tokens:
            if self.source.startswith(delimiter, self.position):
                self.add_token(token_type, delimiter)
                self.position += len(delimiter)
                return

        self.scan_text()

    def scan_text(self) -> None:
        start = self.position

        while self.position < len(self.source):
            found_token = False
            for delimiter, _, _ in Tokens:
                if self.source.startswith(delimiter, self.position):
                    found_token = True
                    break

            if found_token: break

            self.position += 1

        self.add_token(
            TokenType.TEXT,
            self.source[start:self.position],
            start,
        )

    def add_token(
        self,
        token_type: TokenType,
        value: str,
        position: int | None = None,
    ) -> None:
        if position is None:
            position = self.position

        self.tokens.append(
            Token(
                type=token_type,
                value=value,
                position=position,
            )
        )