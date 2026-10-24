from dataclasses import fields, is_dataclass

from md2pdf.orchestrator import Orchestrator
from md2pdf.ast import (
    Document,
    Paragraph,
    RawText,
    Strong,
    Text,
)


def print_ast(node, indent=0):
    prefix = " " * indent

    if not is_dataclass(node):
        print(f"{prefix}{node!r}")
        return

    print(f"{prefix}{type(node).__name__}")

    for field in fields(node):
        value = getattr(node, field.name)

        if isinstance(value, list):
            print(f"{prefix}  {field.name}:")

            for child in value:
                print_ast(child, indent + 4)

        elif is_dataclass(value):
            print(f"{prefix}  {field.name}:")
            print_ast(value, indent + 4)

        else:
            print(f"{prefix}  {field.name}: {value!r}")


def test_orchestrator_prints_document_and_ast():
    source = "Hello **world**"

    document = Orchestrator().parse(source)

    print("\n=== Document object ===")
    print(document)

    print("\n=== AST tree ===")
    print_ast(document)

def test_parses_all_inline_content():
    document = Orchestrator().parse(
        "Hello **world**"
    )

    assert document == Document(children=[
        Paragraph(children=[
            Text("Hello "),
            Strong(children=[
                Text("world"),
            ]),
        ]),
    ])


def test_no_raw_text_remains():
    document = Orchestrator().parse(
        "Hello **world**"
    )

    def contains_raw_text(node):
        from dataclasses import fields, is_dataclass

        if isinstance(node, RawText):
            return True

        if not is_dataclass(node):
            return False

        return any(
            contains_raw_text(getattr(node, field.name))
            for field in fields(node)
        )

    assert not contains_raw_text(document)