import pytest

from md2pdf.renderer.mermaid_renderer import (
    MermaidRenderError,
    render_mermaid,
)


def test_render_mermaid_returns_svg():
    source = """
    flowchart TD
        A[Start] --> B[Finish]
    """

    svg = render_mermaid(source)

    assert "<svg" in svg
    assert "</svg>" in svg


def test_render_invalid_mermaid_raises_error():
    source = "this is not a valid Mermaid diagram"

    with pytest.raises(MermaidRenderError):
        render_mermaid(source)