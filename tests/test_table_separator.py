from md2pdf.orchestrator import Orchestrator
from md2pdf.parser.ast import TableBlock
from md2pdf.parser.block_parser import BlockParser


def test_single_dash_separator_is_table():
    document = BlockParser().parse(
        "| Name | Age |\n"
        "| - | - |\n"
        "| Alice | 21 |"
    )

    assert len(document.children) == 1

    table = document.children[0]
    assert isinstance(table, TableBlock)
    assert len(table.header.cells) == 2
    assert len(table.rows) == 1
    assert table.header.cells[0].children[0].content == "Name"
    assert table.rows[0].cells[0].children[0].content == "Alice"


def test_short_separator_alignment_markers():
    document = BlockParser().parse(
        "| Left | Center | Right |\n"
        "| :- | :-: | -: |\n"
        "| A | B | C |"
    )

    table = document.children[0]

    assert isinstance(table, TableBlock)
    assert table.alignments == ["left", "center", "right"]


def test_short_separator_end_to_end():
    document = Orchestrator().parse(
        "| Name |\n"
        "| - |\n"
        "| Alice |"
    )

    assert len(document.children) == 1
    assert isinstance(document.children[0], TableBlock)
