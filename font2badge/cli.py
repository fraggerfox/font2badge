import argparse
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

from font2badge.render import render


def main():
    ap = argparse.ArgumentParser(
        description="Render text with a raw outline font into a badge-ready "
        "LED strip PNG (shaped by HarfBuzz, self-scaled to the strip height)."
    )
    ap.add_argument("font", type=Path, help="path to a .ttf/.otf")
    ap.add_argument("text", help="text to render (shaped as one run)")
    ap.add_argument(
        "-o", "--out", type=Path, help="output PNG (default: <font>-<md5:8>.png)"
    )
    ap.add_argument(
        "-H", "--height", type=int, default=11, help="strip height in px (default 11)"
    )
    ap.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=0.5,
        help="on/off cut as fraction of peak gray (default 0.5; dotted fonts "
        "like Nupuram Dots need ~0.25)",
    )
    ap.add_argument(
        "--ppem",
        type=float,
        help="pin the pixel size instead of self-scaling the ink span to the "
        "strip height",
    )
    ap.add_argument(
        "--mono",
        action="store_true",
        help="1-bit FreeType raster (for true pixel fonts at native --ppem); "
        "ignores --threshold",
    )
    ap.add_argument(
        "--dots", action="store_true", help="also print the strip as ●/· rows"
    )
    args = ap.parse_args()

    bits, ppem = render(
        args.font, args.text, args.height, args.threshold, args.ppem, args.mono
    )
    out = args.out
    if out is None:
        digest = hashlib.md5(args.text.encode()).hexdigest()[:8]
        out = Path(f"{args.font.stem.lower()}-{digest}.png")
    Image.fromarray(np.where(bits, 255, 0).astype(np.uint8), mode="L").save(out)
    print(f"{out} ({bits.shape[1]}x{bits.shape[0]}, ppem {ppem:.1f})")
    if args.dots:
        for row in bits:
            print("".join("●" if p else "·" for p in row))


if __name__ == "__main__":
    main()
