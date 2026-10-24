from md2pdf.parser.ast import Emphasis, Strong, Text
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