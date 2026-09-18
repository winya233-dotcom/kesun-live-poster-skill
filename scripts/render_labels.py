from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = SKILL_DIR / "assets" / "kesun-blue-manifest.json"


def rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha


def draw_vertical(draw: ImageDraw.ImageDraw, text: str, box: dict[str, float], font: ImageFont.FreeTypeFont, color: tuple[int, int, int, int], tracking: float) -> None:
    y = box["top"] + 16
    center_x = box["left"] + box["width"] / 2
    for char in text:
        bounds = draw.textbbox((0, 0), char, font=font)
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        draw.text((center_x - width / 2, y), char, font=font, fill=color)
        y += height + tracking


def main() -> None:
    parser = argparse.ArgumentParser(description="Render dynamic vertical name and role labels")
    parser.add_argument("layout", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    data = json.loads(args.layout.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    style = manifest["label_style"]
    font_path = SKILL_DIR / "assets" / manifest["fonts"][style["font"]]["file"]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for template_id, layout in data["layouts"].items():
        width = layout["canvas"]["width"]
        height = layout["canvas"]["height"]
        scale = width / 1080
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        for label in layout["labels"]:
            x0, y0 = label["left"], label["top"]
            x1, y1 = x0 + label["width"], y0 + label["height"]
            shadow_draw.rectangle((x0 + 8 * scale, y0 + 10 * scale, x1 + 8 * scale, y1 + 10 * scale), fill=(0, 54, 120, 80))
        canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(max(1, round(6 * scale)))))

        draw = ImageDraw.Draw(canvas)
        for label in layout["labels"]:
            is_name = label["kind"] == "name"
            fill = rgba(style["name_fill"] if is_name else style["role_fill"])
            font_size = round((style["name_font_size"] if is_name else style["role_font_size"]) * scale)
            tracking = (style["name_tracking"] if is_name else style["role_tracking"]) * scale
            draw.rectangle((label["left"], label["top"], label["left"] + label["width"], label["top"] + label["height"]), fill=fill)
            font = ImageFont.truetype(str(font_path), font_size)
            draw_vertical(draw, label["text"], label, font, rgba(style["text_color"]), tracking)

        output = args.output_dir / f"labels-{template_id}.png"
        canvas.save(output)
        print(output.resolve())


if __name__ == "__main__":
    main()
