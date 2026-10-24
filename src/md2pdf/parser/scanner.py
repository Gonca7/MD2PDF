from md2pdf.parser.tokens import Token, TokenType, Tokens


class Scanner:
    def __init__(self, source: str) -> None:
        self.source = source
        self.position = 0
        self.tokens: list[Token] = []



    def scan_tokens(self) -> list[Token]:
        while self.position < len(self.source):
            if self.scan_link():
                continue            

            self.scan_token()

        self.tokens.append(
            Token(
                type=TokenType.EOF,
                value="",
                position=self.position,
            )
        )

        return self.tokens

    def scan_link(self) -> bool:
        """Scan a basic inline link: [label](destination)."""
        if self.source[self.position] != "[":
            return False

        label_end = self.source.find("](", self.position + 1)
        if label_end == -1:
            return False

        destination_start = label_end + 2
        destination_end = self.source.find(")", destination_start)

        if destination_end == -1:
            return False

        label = self.source[self.position + 1:label_end]
        destination = self.source[destination_start:destination_end]

        # Empty destinations are allowed by Markdown, but an empty label
        # is also left to the parser to handle.
        self.add_token(
            TokenType.LINK_TEXT,
            label,
            self.position,
        )
        self.add_token(
            TokenType.LINK_DESTINATION,
            destination,
            destination_start,
        )

        self.position = destination_end + 1
        return True

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
            
            # Leave links for scan_link().
            if self.source[self.position] == "[":
                if self._has_link_at(self.position):
                    break
            
            found_token = False
            for delimiter, _, _ in Tokens:
                if self.source.startswith(delimiter, self.position):
                    found_token = True
                    break

            if found_token: break

            self.position += 1


        # A delimiter or link may be at the current position.
        # Avoid emitting an empty TEXT token in that case.
        if self.position > start:
            self.add_token(
                TokenType.TEXT,
                self.source[start:self.position],
                start,
            )


    def _has_link_at(self, position: int) -> bool:
        label_end = self.source.find("](", position + 1)
        if label_end == -1:
            return False

        destination_start = label_end + 2
        return self.source.find(")", destination_start) != -1


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