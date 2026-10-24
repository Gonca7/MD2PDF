import pytest

from md2pdf.parser.scanner import Scanner
from md2pdf.parser.inline_parser import InlineParser
from md2pdf.parser.ast import (
    Text,
    Emphasis,
    Strong,
    Strikethrough,
    InlineCode,
)


def parse_inline(source: str):
    return InlineParser(Scanner(source).scan_tokens()).parse()


@pytest.mark.parametrize(
    ("source", "expected_type", "expected_content"),
    [
        ("*italic*", Emphasis, "italic"),
        ("_italic_", Emphasis, "italic"),
        ("**bold**", Strong, "bold"),
        ("__bold__", Strong, "bold"),
        ("~~removed~~", Strikethrough, "removed"),
        ("`code`", InlineCode, "code"),
    ],
)
def test_inline_formatting(source, expected_type, expected_content):
    nodes = parse_inline(source)

    assert len(nodes) == 1
    assert isinstance(nodes[0], expected_type)

    if isinstance(nodes[0], InlineCode):
        assert nodes[0].content == expected_content
    else:
        assert nodes[0].children[0].content == expected_content


def test_bold_and_italic():
    nodes = parse_inline("***bold italic***")

    assert len(nodes) == 1
    assert isinstance(nodes[0], Strong)
    assert isinstance(nodes[0].children[0], Emphasis)
    assert nodes[0].children[0].children[0].content == "bold italic"


def test_mismatched_delimiters_remain_literal():
    nodes = parse_inline("*italic_")

    print(nodes)
    print([type(node).__name__ for node in nodes])


    assert all(isinstance(node, Text) for node in nodes)
    assert "".join(node.content for node in nodes) == "*italic_"


def test_markdown_inside_inline_code_is_literal():
    nodes = parse_inline("`**not bold**`")

    assert len(nodes) == 1
    assert isinstance(nodes[0], InlineCode)
    assert nodes[0].content == "**not bold**"