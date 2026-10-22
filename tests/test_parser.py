from md2pdf.ast import Document, Heading, Paragraph, Text
from md2pdf.parser import parse_md


def test_heading():
    result = parse_md("# Hello")

    assert isinstance(result, Document)
    assert len(result.children) == 1

    heading = result.children[0]
    assert isinstance(heading, Heading)
    assert heading.level == 1
    assert heading.children == [Text("Hello")]


def test_paragraph():
    result = parse_md("Hello world")

    paragraph = result.children[0]
    assert isinstance(paragraph, Paragraph)
    assert paragraph.children == [Text("Hello world")]


def test_multiple_blocks():
    result = parse_md("# Title\n\nSome text.")

    assert len(result.children) == 2
    assert isinstance(result.children[0], Heading)
    assert isinstance(result.children[1], Paragraph)