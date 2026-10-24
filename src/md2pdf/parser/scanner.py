from md2pdf.parser.tokens import Token, TokenType, Tokens


class Scanner:
    def __init__(self, source: str) -> None:
        self.source = source
        self.position = 0
        self.tokens: list[Token] = []



    def scan_tokens(self) -> list[Token]:
        while self.position < len(self.source):
            if self.scan_link_or_image():
                continue

            if self.scan_autolink():
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

    def scan_link_or_image(self) -> bool:
        """Scan a complete inline link or image."""
        start = self.position
        is_image = self.source.startswith("![", start)

        if is_image:
            bracket_start = start + 1
        elif self.source[start] == "[":
            bracket_start = start
        else:
            return False

        label_end = self._find_matching(bracket_start, "[", "]")
        if label_end is None:
            return False

        # An inline link/image must have '(' immediately after ']'.
        destination_start = label_end + 1
        if (
            destination_start >= len(self.source)
            or self.source[destination_start] != "("
        ):
            return False

        destination_end = self._find_matching(
            destination_start, "(", ")"
        )
        if destination_end is None:
            return False

        token_type = TokenType.IMAGE if is_image else TokenType.INLINE_LINK
        value = self.source[start:destination_end + 1]

        self.add_token(token_type, value, start)
        self.position = destination_end + 1
        return True

    def scan_autolink(self) -> bool:
        """Scan an angle-bracket URL or email autolink."""
        start = self.position

        if self.source[start] != "<":
            return False

        end = self.source.find(">", start + 1)
        if end == -1:
            return False

        value = self.source[start + 1:end]

        if not value or any(
            char.isspace() or char in "<>" for char in value
        ):
            return False

        is_url = value.startswith(
            ("http://", "https://", "mailto:")
        )
        is_email = (
            "@" in value
            and not value.startswith("@")
            and not value.endswith("@")
        )

        if not (is_url or is_email):
            return False

        self.add_token(TokenType.AUTOLINK, value, start)
        self.position = end + 1
        return True

    def _find_matching(
        self,
        start: int,
        opening: str,
        closing: str,
    ) -> int | None:
        """Find a matching delimiter, accounting for nesting and escapes."""
        depth = 0
        escaped = False
        in_quote: str | None = None

        for index in range(start, len(self.source)):
            char = self.source[index]

            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
                continue

            if in_quote is not None:
                if char == in_quote:
                    in_quote = None
                continue

            # Quoted titles only need special treatment inside destinations.
            if opening == "(" and char in {"'", '"'}:
                in_quote = char
                continue

            if char == opening:
                depth += 1
            elif char == closing:
                depth -= 1
                if depth == 0:
                    return index

        return None


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
            if self.source.startswith("![", self.position):
                if self._has_link_or_image_at(self.position):
                    break
            elif self.source[self.position] == "[":
                if self._has_link_or_image_at(self.position):
                    break
            elif self.source[self.position] == "<":
                if self._has_autolink_at(self.position):
                    break

            if any(
                self.source.startswith(delimiter, self.position)
                for delimiter, _, _ in Tokens
            ):
                break

            self.position += 1

        if self.position == start:
            self.position += 1

        self.add_token(
            TokenType.TEXT,
            self.source[start:self.position],
            start,
        )


    def _has_link_or_image_at(self, position: int) -> bool:
        start = position

        is_image = self.source.startswith("![", start)
        if is_image:
            bracket_start = start + 1
        elif self.source[start] == "[":
            bracket_start = start
        else:
            return False

        label_end = self._find_matching(bracket_start, "[", "]")
        if label_end is None:
            return False

        destination_start = label_end + 1
        if (
            destination_start >= len(self.source)
            or self.source[destination_start] != "("
        ):
            return False

        return (
            self._find_matching(destination_start, "(", ")")
            is not None
        )


    def _has_autolink_at(self, position: int) -> bool:
        end = self.source.find(">", position + 1)
        if end == -1:
            return False

        value = self.source[position + 1:end]

        if not value or any(
            char.isspace() or char in "<>" for char in value
        ):
            return False

        return (
            value.startswith(("http://", "https://", "mailto:"))
            or (
                "@" in value
                and not value.startswith("@")
                and not value.endswith("@")
            )
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