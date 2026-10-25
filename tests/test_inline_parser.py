from md2pdf.parser.ast import Emphasis, Strong, Text, Link, InlineHTML
from md2pdf.parser.inline_parser import InlineParser
from md2pdf.parser.scanner import Scanner


def parse_inline(source: str):
    tokens = Scanner(source).scan_tokens()
    return InlineParser(tokens).parse()


def test_parses_plain_text():
    assert parse_inline("hello") == [
        Text("hello"),
    ]


def test_parses_bold_text():
    assert parse_inline("**hello**") == [
        Strong([Text("hello")]),
    ]


def test_parses_bold_after_plain_text():
    assert parse_inline("hello **world**") == [
        Text("hello "),
        Strong([Text("world")]),
    ]


def test_parses_italic_text():
    assert parse_inline("*hello*") == [
        Emphasis([Text("hello")]),
    ]


def test_parses_bold_and_italic():
    assert parse_inline("**bold** and *italic*") == [
        Strong([Text("bold")]),
        Text(" and "),
        Emphasis([Text("italic")]),
    ]


def test_parses_empty_input():
    assert parse_inline("") == []


def test_parses_link():
    assert parse_inline("[OpenAI](https://openai.com)") == [
        Link(
            children=[Text("OpenAI")],
            url="https://openai.com",
            title=None,
        ),
    ]


def test_parses_link_with_double_quoted_title():
    assert parse_inline(
        '[Docs](https://example.com "Example title")'
    ) == [
        Link(
            children=[Text("Docs")],
            url="https://example.com",
            title="Example title",
        ),
    ]


def test_parses_link_with_single_quoted_title():
    assert parse_inline(
        "[Docs](https://example.com 'Example title')"
    ) == [
        Link(
            children=[Text("Docs")],
            url="https://example.com",
            title="Example title",
        ),
    ]


def test_parses_link_with_nested_strong_text():
    assert parse_inline(
        "[**Bold link**](https://example.com)"
    ) == [
        Link(
            children=[Strong([Text("Bold link")])],
            url="https://example.com",
            title=None,
        ),
    ]


def test_parses_link_between_plain_text():
    assert parse_inline(
        "Visit [OpenAI](https://openai.com) today"
    ) == [
        Text("Visit "),
        Link(
            children=[Text("OpenAI")],
            url="https://openai.com",
            title=None,
        ),
        Text(" today"),
    ]

def test_malformed_link_remains_text():
    assert parse_inline("[OpenAI](https://openai.com") == [
        Text("[OpenAI](https://openai.com"),
    ]

def test_inline_html_is_parsed():
    source = "This is <strong>bold HTML</strong>."

    tokens = Scanner(source).scan_tokens()
    nodes = InlineParser(tokens).parse()

    assert isinstance(nodes[0], Text)
    assert isinstance(nodes[1], InlineHTML)
    assert nodes[1].content == "<strong>"
    assert isinstance(nodes[2], Text)
    assert isinstance(nodes[3], InlineHTML)
    assert nodes[3].content == "</strong>"