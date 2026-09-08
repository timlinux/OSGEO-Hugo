#!/usr/bin/env python3
"""Assemble the shortcode gallery slide deck PDF.

Takes the per-block card PNGs captured by blocks-deck.mjs and lays each
one on a 1920x1080 slide (scaled to fit, centred), preceded by a title
slide. Driven by `osgeo blocks --pdf`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL import JpegImagePlugin  # noqa: F401  (register the JPEG codec
# explicitly: PIL's PDF writer looks it up before lazy plugin init)

ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = ROOT / "artifacts" / "block-cards"
OUTPUT = ROOT / "artifacts" / "blocks-deck.pdf"
REGISTRY = ROOT / "data" / "shortcodes.json"

SLIDE_W, SLIDE_H = 1920, 1080
MARGIN = 60
TEAL = (0, 58, 64)
GREEN = (77, 176, 91)
WHITE = (255, 255, 255)


def find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in [
        "/run/current-system/sw/share/X11/fonts/DejaVuSans-Bold.ttf",
        "/run/current-system/sw/share/X11/fonts/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    # Any TTF beats the tiny bitmap fallback.
    for directory in ["/run/current-system/sw/share/X11/fonts"]:
        ttfs = sorted(Path(directory).glob("*.ttf")) if Path(directory).is_dir() else []
        for ttf in ttfs:
            try:
                return ImageFont.truetype(str(ttf), size)
            except OSError:
                continue
    return ImageFont.load_default()


def title_slide(block_count: int) -> Image.Image:
    slide = Image.new("RGB", (SLIDE_W, SLIDE_H), TEAL)
    draw = ImageDraw.Draw(slide)
    draw.rectangle([0, SLIDE_H - 24, SLIDE_W, SLIDE_H], fill=GREEN)
    big, small = find_font(96), find_font(40)
    draw.text((MARGIN, 360), "OSGeo Website", font=big, fill=WHITE)
    draw.text((MARGIN, 480), "Block & Shortcode Gallery", font=big, fill=GREEN)
    draw.text(
        (MARGIN, 640),
        f"{block_count} content blocks — regenerated from data/shortcodes.json",
        font=small,
        fill=WHITE,
    )
    return slide


def card_slide(png: Path, label: str) -> Image.Image:
    slide = Image.new("RGB", (SLIDE_W, SLIDE_H), WHITE)
    draw = ImageDraw.Draw(slide)
    card = Image.open(png).convert("RGB")
    max_w = SLIDE_W - 2 * MARGIN
    max_h = SLIDE_H - 2 * MARGIN - 40  # room for the footer label
    scale = min(max_w / card.width, max_h / card.height, 1.0)
    if scale < 1.0:
        card = card.resize((int(card.width * scale), int(card.height * scale)))
    x = (SLIDE_W - card.width) // 2
    y = (SLIDE_H - 40 - card.height) // 2
    slide.paste(card, (x, y))
    footer = find_font(28)
    draw.rectangle([0, SLIDE_H - 44, SLIDE_W, SLIDE_H], fill=TEAL)
    draw.text((MARGIN, SLIDE_H - 40), label, font=footer, fill=WHITE)
    return slide


def main() -> int:
    manifest = CARDS_DIR / "manifest.tsv"
    if not manifest.exists():
        print(f"❌ {manifest} missing — run the capture step first", file=sys.stderr)
        return 1
    entries = [
        line.split("\t") for line in manifest.read_text().splitlines() if line.strip()
    ]
    block_count = len(json.loads(REGISTRY.read_text()))

    slides = [title_slide(block_count)]
    for png, name in entries:
        label = name.removeprefix("block-") if name else Path(png).stem
        slides.append(card_slide(Path(png), label))

    slides[0].save(OUTPUT, save_all=True, append_images=slides[1:])
    print(f"✅ wrote {OUTPUT.relative_to(ROOT)} ({len(slides)} slides)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
