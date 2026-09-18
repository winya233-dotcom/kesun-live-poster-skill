from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageFilter


def trim_transparent(image: Image.Image) -> Image.Image:
    box = image.getchannel("A").getbbox()
    if box is None:
        raise RuntimeError("Background removal returned an empty image")
    return image.crop(box)


def main() -> None:
    parser = argparse.ArgumentParser(description="High-quality portrait cutout with rembg/BiRefNet")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--model", default="birefnet-portrait")
    parser.add_argument("--alpha-matting", action="store_true")
    parser.add_argument("--no-trim", action="store_true")
    args = parser.parse_args()

    from rembg import new_session, remove

    source = Image.open(args.input).convert("RGBA")
    session = new_session(args.model)
    result = remove(
        source,
        session=session,
        alpha_matting=args.alpha_matting,
        post_process_mask=True,
    ).convert("RGBA")

    alpha = result.getchannel("A")
    alpha = alpha.filter(ImageFilter.MedianFilter(3))
    result.putalpha(alpha)
    if not args.no_trim:
        result = trim_transparent(result)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output)
    print(args.output.resolve())


if __name__ == "__main__":
    main()
