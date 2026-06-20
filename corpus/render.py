from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from themes import PdfTheme

ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT / "templates"


def _content_env(family_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(family_dir),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _document_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_document(family_dir: Path, theme: PdfTheme, ctx: dict[str, object]) -> str:
    content = _content_env(family_dir).get_template("template.j2").render(**ctx)
    return (
        _document_env()
        .get_template("document.html.j2")
        .render(
            content=content,
            theme=theme,
        )
    )
