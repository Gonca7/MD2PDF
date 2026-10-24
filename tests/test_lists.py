from md2pdf.parser.ast import ListBlock, Paragraph, RawText
from md2pdf.parser.block_parser import BlockParser


def test_unordered_list():
    document = BlockParser().parse("- One\n- Two\n- Three")

    assert len(document.children) == 1
    result = document.children[0]

    assert isinstance(result, ListBlock)
    assert result.ordered is False
    assert len(result.items) == 3
    assert result.items[0].children == [
        Paragraph(children=[RawText("One")])
    ]


def test_ordered_list():
    document = BlockParser().parse("3. Three\n4. Four")

    result = document.children[0]

    assert isinstance(result, ListBlock)
    assert result.ordered is True
    assert result.start == 3
    assert len(result.items) == 2


def test_list_after_paragraph():
    document = BlockParser().parse(
        "Introductory paragraph.\n\n- One\n- Two"
    )

    assert isinstance(document.children[0], Paragraph)
    assert isinstance(document.children[1], ListBlock)


def test_different_list_types_are_separate():
    document = BlockParser().parse("- One\n1. Two")

    assert len(document.children) == 2
    assert isinstance(document.children[0], ListBlock)
    assert document.children[0].ordered is False
    assert isinstance(document.children[1], ListBlock)
    assert document.children[1].ordered is True