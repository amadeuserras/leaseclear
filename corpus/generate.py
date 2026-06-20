from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

import fitz

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from doc_meta import doc_id  # noqa: E402
from registry import BY_ID, FAMILIES, FamilySpec  # noqa: E402
from themes import PdfTheme  # noqa: E402

OUTPUT_DIR = ROOT / "generated"

ACCENT_BAR_HEIGHT = 6
TOP_MARGIN = 54 + ACCENT_BAR_HEIGHT + 8


def render_pdf(html: str, output_path: Path, theme: PdfTheme) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    story = fitz.Story(html=html)
    mediabox = fitz.paper_rect("letter")
    margin = 54
    where = fitz.Rect(
        margin,
        TOP_MARGIN,
        mediabox.width - margin,
        mediabox.height - margin,
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

    accent = theme.accent_rgb()
    doc = fitz.open(tmp_path)
    for page in doc:
        bar = fitz.Rect(0, 0, page.rect.width, ACCENT_BAR_HEIGHT)
        page.draw_rect(bar, color=accent, fill=accent)
    doc.save(str(output_path))
    doc.close()
    tmp_path.unlink()


def clear_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT_DIR.iterdir():
        if path.is_file():
            path.unlink()


def output_path(doc_id: str) -> Path:
    return OUTPUT_DIR / f"{doc_id}.pdf"


def generate_one(family: FamilySpec, instance: Any) -> Path:
    lease_id = doc_id(family.name, family.doc_meta(instance).name)
    html = family.render_html(instance)
    out = output_path(lease_id)
    render_pdf(html, out, family.theme)
    return out


def generate_all() -> list[Path]:
    clear_output_dir()
    return [
        generate_one(family, instance)
        for family in FAMILIES
        for instance in family.instances
    ]


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)

    if len(args) > 1:
        print("usage: generate.py [doc-id]", file=sys.stderr)
        raise SystemExit(2)

    if len(args) == 1:
        doc_id = args[0]
        if doc_id not in BY_ID:
            print(f"unknown doc id: {doc_id}", file=sys.stderr)
            raise SystemExit(1)
        family, instance = BY_ID[doc_id]
        outputs = [generate_one(family, instance)]
    else:
        outputs = generate_all()

    for out in outputs:
        print(f"generated {out}")
    print(f"done ({len(outputs)} PDFs)")


if __name__ == "__main__":
    main()
