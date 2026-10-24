from md2pdf.parser.scanner import Scanner
from md2pdf.parser.tokens import TokenType


def test_scans_plain_text():
    tokens = Scanner("Hello world").scan_tokens()

    assert [token.type for token in tokens] == [
        TokenType.TEXT,
        TokenType.EOF,
    ]
    assert tokens[0].value == "Hello world"
    assert tokens[0].position == 0


def test_scans_bold_delimiters():
    tokens = Scanner("**bold**").scan_tokens()

    print(tokens)

    assert [token.type for token in tokens] == [
        TokenType.STRONG_DELIMITER,
        TokenType.TEXT,
        TokenType.STRONG_DELIMITER,
        TokenType.EOF,
    ]
    assert tokens[1].value == "bold"
    assert tokens[2].position == 6


def test_scans_italic_delimiters():
    tokens = Scanner("*italic*").scan_tokens()

    print(tokens)

    assert [token.type for token in tokens] == [
        TokenType.EMPHASIS_DELIMITER,
        TokenType.TEXT,
        TokenType.EMPHASIS_DELIMITER,
        TokenType.EOF,
    ]


def test_scans_empty_input():
    tokens = Scanner("").scan_tokens()

    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    assert tokens[0].position == 0


def test_scans_link():
    tokens = Scanner("[OpenAI](https://openai.com)").scan_tokens()

    assert [token.type for token in tokens] == [
        TokenType.INLINE_LINK,
        TokenType.EOF,
    ]
    assert tokens[0].value == "[OpenAI](https://openai.com)"
    assert tokens[0].position == 0


def test_scans_link_with_title():
    tokens = Scanner(
        '[Docs](https://example.com "Example title")'
    ).scan_tokens()

    assert tokens[0].type == TokenType.INLINE_LINK
    assert tokens[0].value == (
        '[Docs](https://example.com "Example title")'
    )
    assert tokens[0].position == 0
    assert tokens[1].type == TokenType.EOF


def test_scans_link_after_plain_text():
    tokens = Scanner(
        "Visit [OpenAI](https://openai.com)"
    ).scan_tokens()

    assert tokens[0].type == TokenType.TEXT
    assert tokens[0].value == "Visit "
    assert tokens[0].position == 0

    assert tokens[1].type == TokenType.INLINE_LINK
    assert tokens[1].value == "[OpenAI](https://openai.com)"
    assert tokens[1].position == 6

    assert tokens[2].type == TokenType.EOF
