from md2pdf.parser.ast import (
    BlockQuote,
    Heading,
    Paragraph,
    RawBlock,
    RawText,
    Strong,
    Text,
)
from md2pdf.parser.block_parser import BlockParser
from md2pdf.orchestrator import Orchestrator


def test_block_parser_parses_blockquote_contents():
    document = BlockParser().parse("> Hello world")

    quote = document.children[0]

    assert isinstance(quote, BlockQuote)
    assert len(quote.children) == 1
    assert isinstance(quote.children[0], Paragraph)
    assert quote.children[0].children == [
        RawText("Hello world")
    ]

def test_orchestrator_replaces_raw_block():
    document = Orchestrator().parse("> Hello **world**")

    quote = document.children[0]
    assert isinstance(quote, BlockQuote)

    paragraph = quote.children[0]
    assert isinstance(paragraph, Paragraph)
    assert paragraph.children == [
    Text("Hello "),
    Strong(children=[Text("world")]),
    ]

def test_nested_blockquotes():
    source = "> Outer\n>\n> > Inner"
    document = Orchestrator().parse(source)

    outer_quote = document.children[0]
    assert isinstance(outer_quote, BlockQuote)

    outer_paragraph = outer_quote.children[0]
    assert isinstance(outer_paragraph, Paragraph)
    assert outer_paragraph.children == [Text("Outer")]

    inner_quote = outer_quote.children[1]
    assert isinstance(inner_quote, BlockQuote)

    inner_paragraph = inner_quote.children[0]
    assert isinstance(inner_paragraph, Paragraph)
    assert inner_paragraph.children == [Text("Inner")]

def test_blockquote_can_contain_heading():
    document = Orchestrator().parse("> # Quoted heading")

    quote = document.children[0]
    heading = quote.children[0]

    assert isinstance(heading, Heading)
    assert heading.level == 1
    assert heading.children == [Text("Quoted heading")]

def test_blockquote_with_multiple_paragraphs():
    source = "> First paragraph\n>\n> Second paragraph"
    document = Orchestrator().parse(source)

    quote = document.children[0]

    assert isinstance(quote, BlockQuote)
    assert len(quote.children) == 2
    assert quote.children[0] == Paragraph(
    children=[Text("First paragraph")]
    )
    assert quote.children[1] == Paragraph(
    children=[Text("Second paragraph")]
    )