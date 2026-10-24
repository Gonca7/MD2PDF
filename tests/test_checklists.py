from md2pdf.parser.ast import ListBlock, Paragraph, RawText
from md2pdf.parser.block_parser import BlockParser


def test_checked_task():
    document = BlockParser().parse("- [x] Completed task")

    result = document.children[0]

    assert isinstance(result, ListBlock)
    assert result.items[0].checked is True
    assert result.items[0].children == [
        Paragraph(children=[RawText("Completed task")])
    ]


def test_unchecked_task():
    document = BlockParser().parse("- [ ] Incomplete task")

    result = document.children[0]

    assert isinstance(result, ListBlock)
    assert result.items[0].checked is False
    assert result.items[0].children == [
        Paragraph(children=[RawText("Incomplete task")])
    ]


def test_normal_list_item_has_no_checkbox():
    document = BlockParser().parse("- Ordinary item")

    result = document.children[0]

    assert isinstance(result, ListBlock)
    assert result.items[0].checked is None


def test_mixed_checklist():
    document = BlockParser().parse(
        "- [x] Completed task\n"
        "- [ ] Incomplete task\n"
        "- [ ] Another task"
    )

    result = document.children[0]

    assert isinstance(result, ListBlock)
    assert [item.checked for item in result.items] == [
        True,
        False,
        False,
    ]