python - <<'PY'
from pathlib import Path

from md2pdf.orchestrator import Orchestrator
from md2pdf.renderer.html_renderer import HTMLRenderer

source = Path("tests/example.md").read_text(encoding="utf-8")

document = Orchestrator().parse(source)
html = HTMLRenderer("src/md2pdf/styles/MD2PDF.css").render(document)

output = Path("/home/gonca7/Documents/LAB/Projects/MD2PDF/md2pdf-preview.html")
output.write_text(html, encoding="utf-8")

print(f"HTML written to: {output}")
PY