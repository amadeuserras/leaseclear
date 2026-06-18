from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

import fitz
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data import ALL, BY_ID  # noqa: E402
from models.lease import Lease  # noqa: E402

TEMPLATE_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "generated"


def render_html(lease: Lease) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("lease.html.j2")
    return template.render(**asdict(lease))


def render_pdf(lease: Lease, output_path: Path) -> None:
    html = render_html(lease)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    story = fitz.Story(html=html)
    mediabox = fitz.paper_rect("letter")
    margin = 54
    where = fitz.Rect(margin, margin, mediabox.width - margin, mediabox.height - margin)
    writer = fitz.DocumentWriter(str(output_path))

    more = True
    while more:
        device = writer.begin_page(mediabox)
        more, _ = story.place(where)
        story.draw(device)
        writer.end_page()

    writer.close()


def output_path(lease: Lease) -> Path:
    return OUTPUT_DIR / f"{lease.meta.id}.pdf"


def generate_one(lease: Lease) -> Path:
    out = output_path(lease)
    render_pdf(lease, out)
    return out


def generate_all() -> list[Path]:
    return [generate_one(lease) for lease in ALL]


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)

    if len(args) > 1:
        print("usage: generate.py [lease-id]", file=sys.stderr)
        raise SystemExit(2)

    if len(args) == 1:
        lease_id = args[0]
        if lease_id not in BY_ID:
            print(f"unknown lease id: {lease_id}", file=sys.stderr)
            raise SystemExit(1)
        outputs = [generate_one(BY_ID[lease_id])]
    else:
        outputs = generate_all()

    for out in outputs:
        print(f"generated {out}")
    print(f"done ({len(outputs)} PDFs)")


if __name__ == "__main__":
    main()
