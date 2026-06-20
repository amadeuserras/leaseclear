from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import fitz
from jinja2 import (  # pyright: ignore[reportMissingImports]
    Environment,
    FileSystemLoader,
)

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import LEASE  # noqa: E402

OUTPUT_DIR = ROOT / "generated"
MARGIN = 54


def render_html(context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(ROOT),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env.get_template("template.j2").render(lease=context)


def render_pdf(html: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    story = fitz.Story(html=html)
    mediabox = fitz.paper_rect("letter")
    where = fitz.Rect(
        MARGIN,
        MARGIN,
        mediabox.width - MARGIN,
        mediabox.height - MARGIN,
    )

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    writer = fitz.DocumentWriter(str(tmp_path))
    more = True
    while more:
        device = writer.begin_page(mediabox)
        more, _ = story.place(where)
        story.draw(device)
        writer.end_page()
    writer.close()

    doc = fitz.open(tmp_path)
    doc.save(str(output_path))
    doc.close()
    tmp_path.unlink()


def main() -> None:
    html = render_html(LEASE.to_context())
    output_path = OUTPUT_DIR / f"{LEASE.filename}.pdf"
    render_pdf(html, output_path)
    print(f"generated {output_path}")


if __name__ == "__main__":
    main()
