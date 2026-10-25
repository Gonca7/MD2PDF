import mermaidx


class MermaidRenderError(Exception):
    """Raised when a Mermaid diagram cannot be rendered."""


def render_mermaid(source: str) -> str:
    """Render Mermaid source into an SVG string."""
    try:
        return mermaidx.render(
            source,
            theme="neutral",
            config={
                "htmlLabels": False,
            }
        ).svg()
    except Exception as exc:
        raise MermaidRenderError(
            "Failed to render Mermaid diagram."
        ) from exc