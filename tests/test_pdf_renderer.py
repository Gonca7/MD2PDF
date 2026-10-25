from md2pdf.renderer.pdf_renderer import PDFRenderer


def test_render_creates_pdf(tmp_path):
    output_path = tmp_path / "output.pdf"

    renderer = PDFRenderer()
    renderer.render(
        "<html><body><h1>Hello, PDF!</h1></body></html>",
        output_path,
    )

    assert output_path.exists()
    assert output_path.read_bytes().startswith(b"%PDF-")
