from md2pdf.ast import Document, Heading, Paragraph, RawText
from md2pdf.block_parser import BlockParser


def test_heading():
    result = BlockParser().parse("# Hello")

    assert isinstance(result, Document)
    assert len(result.children) == 1

    heading = result.children[0]
    assert isinstance(heading, Heading)
    assert heading.level == 1
    assert heading.children == [RawText("Hello")]


def test_paragraph():
    result = BlockParser().parse("Hello world")

    paragraph = result.children[0]
    assert isinstance(paragraph, Paragraph)
    assert paragraph.children == [RawText("Hello world")]


def test_multiple_blocks():
    result = BlockParser().parse("# Title\n\nSome text.")

    assert len(result.children) == 2
    assert isinstance(result.children[0], Heading)
    assert isinstance(result.children[1], Paragraph)