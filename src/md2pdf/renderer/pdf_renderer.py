from pathlib import Path
from weasyprint import HTML


class PDFRenderer:
    """Convert an HTML document into a PDF file."""

    def render(
        self,
        html: str,
        output_path: str | Path,
        base_url: str | Path | None = None,
    ) -> None:
        """Render HTML into a PDF at the given output path."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        HTML(
            string=html,
            base_url=str(base_url) if base_url is not None else None,
        ).write_pdf(output_path)
