from __future__ import annotations

import importlib
import shutil
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

OUTPUT_DIR = ROOT / "generated"
MARGIN = 20
PACKAGES = ("meridian", "california")


def render_html(context: dict, template_dir: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(template_dir),
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


def generate_package(name: str) -> None:
    lease = importlib.import_module(f"{name}.data").LEASE
    html = render_html(lease.to_context(), ROOT / name)
    output_path = OUTPUT_DIR / name / f"{lease.filename}.pdf"
    render_pdf(html, output_path)
    print(f"generated {output_path}")

    if name == "meridian":
        legacy_path = OUTPUT_DIR / f"{lease.filename}.pdf"
        if legacy_path != output_path:
            shutil.copy(output_path, legacy_path)
            print(f"generated {legacy_path}")


def main() -> None:
    names = sys.argv[1:] or list(PACKAGES)
    unknown = set(names) - set(PACKAGES)
    if unknown:
        print(f"unknown package(s): {', '.join(sorted(unknown))}", file=sys.stderr)
        print(f"available: {', '.join(PACKAGES)}", file=sys.stderr)
        sys.exit(1)

    for name in names:
        generate_package(name)


if __name__ == "__main__":
    main()
