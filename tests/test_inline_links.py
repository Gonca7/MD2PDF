from md2pdf.parser.ast import Image, Link, Strong, Text
from md2pdf.parser.inline_parser import InlineParser
from md2pdf.parser.scanner import Scanner
from md2pdf.parser.tokens import TokenType


def parse_inline(source: str):
    return InlineParser(Scanner(source).scan_tokens()).parse()


def test_scanner_recognizes_inline_link():
    tokens = Scanner(
        '[Example](https://example.com "Example title")'
    ).scan_tokens()

    assert tokens[0].type == TokenType.INLINE_LINK
    assert tokens[0].value == (
        '[Example](https://example.com "Example title")'
    )
    assert tokens[0].position == 0


def test_inline_link_with_title():
    nodes = parse_inline(
        '[Example](https://example.com "Example title")'
    )

    assert len(nodes) == 1
    assert isinstance(nodes[0], Link)
    assert nodes[0].url == "https://example.com"
    assert nodes[0].title == "Example title"
    assert nodes[0].children == [Text("Example")]


def test_image_with_alt_text_and_title():
    nodes = parse_inline(
        '![A cat](https://example.com/cat.png "Cat image")'
    )

    assert len(nodes) == 1
    assert isinstance(nodes[0], Image)
    assert nodes[0].alt == "A cat"
    assert nodes[0].src == "https://example.com/cat.png"
    assert nodes[0].title == "Cat image"


def test_url_autolink():
    nodes = parse_inline("<https://example.com>")

    assert len(nodes) == 1
    assert isinstance(nodes[0], Link)
    assert nodes[0].url == "https://example.com"


def test_email_autolink():
    nodes = parse_inline("<hello@example.com>")

    assert len(nodes) == 1
    assert isinstance(nodes[0], Link)
    assert nodes[0].url == "mailto:hello@example.com"
    assert nodes[0].children == [Text("hello@example.com")]


def test_link_label_can_contain_strong_text():
    nodes = parse_inline("[**Bold link**](https://example.com)")

    assert len(nodes) == 1
    assert isinstance(nodes[0], Link)
    assert len(nodes[0].children) == 1
    assert isinstance(nodes[0].children[0], Strong)


def test_unrecognized_angle_brackets_remain_text():
    nodes = parse_inline("x < y")

    assert nodes == [Text("x < y")]