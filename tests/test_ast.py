from md2pdf.parser.ast import Document, Heading, Paragraph, Text


def test_document_contains_heading_and_paragraph():
    document = Document(children=[
        Heading(1, [Text("Hello")]),
        Paragraph([Text("World")]),
    ])

    assert len(document.children) == 2
    assert document.children[0].level == 1
    assert document.children[0].children[0].content == "Hello"
    assert document.children[1].children[0].content == "World"


def test_documents_have_independent_children():
    first = Document()
    second = Document()

    first.children.append(Paragraph([Text("Hello")]))

    assert len(first.children) == 1
    assert len(second.children) == 0