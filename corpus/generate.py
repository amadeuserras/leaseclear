from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import fitz
from jinja2 import Environment, FileSystemLoader  # pyright: ignore[reportMissingImports]

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "generated"
MARGIN = 54


def load_case(case_path: Path):
    """Import a case file and return its LEASE object."""
    spec = importlib.util.spec_from_file_location(case_path.stem, case_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.LEASE


def render_html(template_dir: Path, context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env.get_template("template.j2").render(lease=context)


def render_pdf(html: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    story = fitz.Story(html=html)
    mediabox = fitz.paper_rect("letter")
    where = fitz.Rect(MARGIN, MARGIN, mediabox.width - MARGIN, mediabox.height - MARGIN)

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


def discover() -> list[tuple[Path, Path]]:
    """Return (template_dir, case_file) pairs for every corpus/cases/*.py."""
    pairs = []
    for cases_dir in sorted(ROOT.glob("*/cases")):
        template_dir = cases_dir.parent
        for case_file in sorted(cases_dir.glob("*.py")):
            if case_file.name == "__init__.py":
                continue
            pairs.append((template_dir, case_file))
    return pairs


def main() -> None:
    pairs = discover()
    if not pairs:
        print("no cases found")
        return

    for template_dir, case_file in pairs:
        corpus = template_dir.name
        case = case_file.stem
        lease = load_case(case_file)
        html = render_html(template_dir, lease.to_context())
        output_path = OUTPUT_DIR / f"{corpus}-{case}.pdf"
        render_pdf(html, output_path)
        print(f"generated {output_path}")


if __name__ == "__main__":
    main()
