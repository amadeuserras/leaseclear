from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PdfTheme:
    accent: str
    title_color: str
    body_color: str
    font_family: str
    font_size: str
    line_height: str
    header_brand: str
    header_tagline: str | None = None

    def accent_rgb(self) -> tuple[float, float, float]:
        hex_color = self.accent.lstrip("#")
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return (r, g, b)


THEMES: dict[str, PdfTheme] = {
    "simple": PdfTheme(
        accent="#3d6b8e",
        title_color="#2a4a63",
        body_color="#2c2c2c",
        font_family="Georgia, 'Times New Roman', serif",
        font_size="11pt",
        line_height="1.45",
        header_brand="",
        header_tagline=None,
    ),
    "standard": PdfTheme(
        accent="#1a6b4a",
        title_color="#145a3c",
        body_color="#1a1a1a",
        font_family="'Helvetica Neue', Helvetica, Arial, sans-serif",
        font_size="10.5pt",
        line_height="1.4",
        header_brand="Greenfield Properties",
        header_tagline="Residential Lease Administration",
    ),
    "complex": PdfTheme(
        accent="#5c3d6e",
        title_color="#3d2850",
        body_color="#222222",
        font_family="'Times New Roman', Times, serif",
        font_size="10.5pt",
        line_height="1.42",
        header_brand="Meridian Legal Forms",
        header_tagline="Multi-State Residential Agreement",
    ),
}
