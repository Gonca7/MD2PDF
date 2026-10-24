from md2pdf.parser.ast import TableBlock
from md2pdf.parser.block_parser import BlockParser


def test_basic_table():
    document = BlockParser().parse(
        "| Name | Age |\n"
        "| --- | --- |\n"
        "| Alice | 21 |\n"
        "| Bob | 25 |"
    )

    assert len(document.children) == 1

    table = document.children[0]
    assert isinstance(table, TableBlock)
    assert len(table.header.cells) == 2
    assert len(table.rows) == 2

    assert table.header.cells[0].children[0].content == "Name"
    assert table.rows[0].cells[0].children[0].content == "Alice"


def test_table_alignment():
    document = BlockParser().parse(
        "| Left | Center | Right |\n"
        "| :--- | :---: | ---: |\n"
        "| A | B | C |"
    )

    table = document.children[0]

    assert isinstance(table, TableBlock)
    assert table.alignments == ["left", "center", "right"]


def test_table_without_outer_pipes():
    document = BlockParser().parse(
        "Name | Age\n"
        "--- | ---\n"
        "Alice | 21"
    )

    table = document.children[0]

    assert isinstance(table, TableBlock)
    assert len(table.header.cells) == 2
    assert len(table.rows) == 1