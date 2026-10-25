
import pytest

from md2pdf.renderer.html_renderer import HTMLRenderer
from md2pdf.parser.ast import (
    CodeBlock,
    Document,
    Emphasis,
    Heading,
    Link,
    Paragraph,
    RawText,
    Strong,
    Text,
    ThematicBreak,
    HTMLBlock,
    InlineHTML,
)


def test_render_complete_document():
    document = Document(children=[
        Heading(level=1, children=[Text("Hello")]),
        Paragraph(children=[
            Text("Hello "),
            Strong(children=[Text("world")]),
        ]),
        ThematicBreak(),
    ])

    html = HTMLRenderer().render(document)

    assert "<h1>Hello</h1>" in html
    assert "<p>Hello <strong>world</strong></p>" in html
    assert "<hr>" in html
    assert html.startswith("<!doctype html>")


def test_escape_text():
    document = Document(children=[
        Paragraph(children=[Text("<script>alert('x')</script>")])
    ])

    html = HTMLRenderer().render(document)

    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_render_nested_inline_nodes():
    document = Document(children=[
        Paragraph(children=[
            Emphasis(children=[
                Text("some "),
                Strong(children=[Text("important")]),
                Text(" text"),
            ])
        ])
    ])

    html = HTMLRenderer().render(document)

    assert "<em>some <strong>important</strong> text</em>" in html


def test_render_code_block():
    document = Document(children=[
        CodeBlock(content="print('<hello>')", language="python")
    ])

    html = HTMLRenderer().render(document)

    assert 'class="language-python"' in html
    assert "print(&#x27;&lt;hello&gt;&#x27;)" in html


def test_reject_unresolved_inline_nodes():
    document = Document(children=[
        Paragraph(children=[RawText("unparsed text")])
    ])

    with pytest.raises(ValueError, match="Unresolved RawText"):
        HTMLRenderer().render(document)


def test_reject_unsafe_link():
    document = Document(children=[
        Paragraph(children=[
            Link(
                children=[Text("click")],
                url="javascript:alert(1)",
            )
        ])
    ])

    html = HTMLRenderer().render(document)

    assert "javascript:" not in html
    assert ">click</p>" in html


def test_render_inline_html():
    document = Document(children=[
        Paragraph(children=[
            Text("Hello "),
            InlineHTML("<strong>world</strong>"),
        ])
    ])

    html = HTMLRenderer().render(document)

    assert "<p>Hello <strong>world</strong></p>" in html


def test_render_block_html():
    document = Document(children=[
        HTMLBlock("<div><p>Hello</p></div>")
    ])

    html = HTMLRenderer().render(document)

    assert "<div><p>Hello</p></div>" in html


def test_raw_html_removes_scripts_and_event_handlers():
    document = Document(children=[
        HTMLBlock(
            '<div onclick="alert(1)">'
            '<script>alert(2)</script>'
            '<p>Safe content</p>'
            "</div>"
        )
    ])

    html = HTMLRenderer().render(document)

    assert "<div>" in html
    assert "<p>Safe content</p>" in html
    assert "onclick" not in html
    assert "<script>" not in html
    assert "alert(2)" not in html


def test_raw_html_rejects_javascript_urls():
    document = Document(children=[
        Paragraph(children=[
            InlineHTML('<a href="javascript:alert(1)">click</a>')
        ])
    ])

    html = HTMLRenderer().render(document)

    assert "javascript:" not in html
    assert '<a>click</a>' in html

def test_raw_html_preserves_anchor_id():
    document = Document(children=[
        Paragraph(children=[
            InlineHTML('<a id="mci"></a>')
        ])
    ])

    html = HTMLRenderer().render(document)

    assert '<a id="mci"></a>' in html

def test_raw_html_preserves_br():
    document = Document(children=[
        Paragraph(children=[
            InlineHTML("first<br>second")
        ])
    ])

    html = HTMLRenderer().render(document)

    assert "first<br>second" in html