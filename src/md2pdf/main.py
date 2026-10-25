from md2pdf.orchestrator import Orchestrator
from md2pdf.renderer.html_renderer import HTMLRenderer
from md2pdf.renderer.pdf_renderer import PDFRenderer

import os
from pathlib import Path


TITLE = r"""
$$\      $$\ $$$$$$$\   $$$$$$\  $$$$$$$\  $$$$$$$\  $$$$$$$$\
$$$\    $$$ |$$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$  _____|
$$$$\  $$$$ |$$ |  $$ |\__/  $$ |$$ |  $$ |$$ |  $$ |$$ |
$$\$$\$$ $$ |$$ |  $$ | $$$$$$  |$$$$$$$  |$$ |  $$ |$$$$$\
$$ \$$$  $$ |$$ |  $$ |$$  ____/ $$  ____/ $$ |  $$ |$$  __|
$$ |\$  /$$ |$$ |  $$ |$$ |      $$ |      $$ |  $$ |$$ |
$$ | \_/ $$ |$$$$$$$  |$$$$$$$$\ $$ |      $$$$$$$  |$$ |
\__|     \__|\_______/ \________|\__|      \_______/ \__|   by Gonca7
"""

# Assumes the default stylesheet is bundled here.
DEFAULT_CSS = Path(__file__).parent / "styles" / "MD2PDF.css"


def clear_console() -> None:
    """Clear the terminal and move the cursor to the top-left."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header() -> None:
    print("\033[96m" + TITLE + "\033[0m")
    print()


def print_menu(title: str, description: str = "") -> None:
    clear_console()
    print_header()
    print(title)
    if description:
        print(description)
    print()


def read_path(prompt: str) -> str:
    """Read a path, allowing users to surround it with quotes."""
    return input(prompt).strip().strip('"').strip("'")


def select_markdown_file() -> Path:
    error_message = ""

    while True:
        print_menu(
            "SELECT MARKDOWN FILE",
            "Enter the path to your Markdown (.md) file.",
        )

        if error_message:
            print(f"> Error: {error_message}\n")

        raw_path = read_path("> File path (or 'q' to quit): ")

        if raw_path.lower() == "q":
            raise SystemExit(0)

        if not raw_path:
            error_message = "Please enter a file path."
            continue

        path = Path(raw_path).expanduser()

        if not path.is_file():
            error_message = f"File not found: {path}"
            continue

        if path.suffix.lower() != ".md":
            error_message = "Please select a Markdown file (.md)."
            continue

        return path.resolve()


def select_css_file() -> Path:
    """Return the default stylesheet or a validated custom CSS path."""
    error_message = ""

    while True:
        print_menu(
            "SELECT CSS STYLESHEET",
            "Press Enter to use the default stylesheet, or enter the path to a custom .css file.",
        )
        print(f"Default CSS: {DEFAULT_CSS}")
        print()

        if error_message:
            print(f"> Error: {error_message}\n")

        raw_path = read_path("> CSS path (Enter for default, 'q' to quit): ")

        if raw_path.lower() == "q":
            raise SystemExit(0)

        if not raw_path:
            if not DEFAULT_CSS.is_file():
                error_message = (
                    f"Default stylesheet not found: {DEFAULT_CSS}"
                )
                continue

            return DEFAULT_CSS.resolve()

        path = Path(raw_path).expanduser()

        if not path.is_file():
            error_message = f"File not found: {path}"
            continue

        if path.suffix.lower() != ".css":
            error_message = "Please select a CSS file (.css)."
            continue

        return path.resolve()


def select_output_format() -> str:
    """Let the user choose HTML, PDF, or both output formats."""
    error_message = ""

    while True:
        print_menu(
            "SELECT OUTPUT FORMAT",
            "Choose the format to generate.",
        )
        print("  1. HTML")
        print("  2. PDF")
        print("  3. HTML + PDF")
        print()

        if error_message:
            print(f"> Error: {error_message}\n")

        choice = input("> Choose an option (or 'q' to quit): ").strip()

        if choice.lower() == "q":
            raise SystemExit(0)

        if choice == "1":
            return "html"

        if choice == "2":
            return "pdf"

        if choice == "3":
            return "both"

        error_message = (
            "Invalid choice. Enter 1 for HTML, 2 for PDF, or 3 for both."
        )


def main() -> None:

    while(True):
        markdown_path = select_markdown_file()
        css_path = select_css_file()
        output_format = select_output_format()

        output_paths = {
            "html": markdown_path.with_suffix(".html"),
            "pdf": markdown_path.with_suffix(".pdf"),
            "both": markdown_path.with_suffix(".html"),
        }

        print_menu("CONFIGURATION COMPLETE")
        print("Markdown file:")
        print(f"  {markdown_path}")
        print()
        print("CSS stylesheet:")
        print(f"  {css_path}")
        print()
        print("Output format:")
        print(f"  {output_format.upper()}")
        print()
        print("Output file(s):")

        if output_format in ("html", "both"):
            print(f"  {output_paths['html']}")

        if output_format in ("pdf", "both"):
            print(f"  {output_paths['pdf']}")
        print()

        input("> Press Enter to render (Ctrl+C to cancel)...")

        clear_console()
        print_header()
        print("RENDERING DOCUMENT")
        print()

        try:
            # Read the Markdown source.
            source = markdown_path.read_text(encoding="utf-8")

            # Parse Markdown into your AST.
            orchestrator = Orchestrator()
            document = orchestrator.parse(source)

            # Render the AST into HTML, applying the selected stylesheet.
            html_renderer = HTMLRenderer(css_path=css_path)
            html = html_renderer.render(document)

            if output_format in ("html", "both"):
                output_paths["html"].write_text(html, encoding="utf-8")

            if output_format in ("pdf", "both"):
                pdf_renderer = PDFRenderer()
                pdf_renderer.render(
                    html,
                    output_paths["pdf"],
                    base_url=markdown_path.parent,
                )

            print("Rendering completed successfully!")
            print()
            print("Output saved to:")

            if output_format in ("html", "both"):
                print(f"  {output_paths['html']}")

            if output_format in ("pdf", "both"):
                print(f"  {output_paths['pdf']}")

        except Exception as exc:
            print("Rendering failed.")
            print()
            print(f"Error: {exc}")

        print()
        if input("> Press any key or (q) to exit... ").lower() == "q":
            clear_console()
            return

        clear_console()

if __name__ == "__main__":
    main()
