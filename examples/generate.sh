#!/usr/bin/env bash
# Regenerate the README example strips + their 8x display copies.
# Run from the repo root inside `nix develop`. Font locations are the
# sibling checkouts under ~/dev-stuff/projects/led-badge/.
set -e
cd "$(dirname "$0")"
LB=~/dev-stuff/projects/led-badge
MANJARI=$LB/pixelshaper/examples/manjari-pixel/fonts/Manjari-Regular.ttf
MUKTA=$LB/pixelshaper/examples/mukta-pixel/fonts/Mukta-Regular.ttf
FT=$LB/freetype

font2badge "$MANJARI" "കേരളം" -o manjari-keralam.png
font2badge "$FT/NotoSansMalayalam-Regular.ttf" "നമസ്കാരം" -o noto-namaskaram.png
font2badge "$FT/Nupuram-Dots.ttf" "കേരളം" -t 0.25 -o nupuram-dots-keralam.png
font2badge "$FT/k8x12.ttf" "Keralam" --ppem 12 --mono -o k8x12-keralam-native.png
font2badge "$FT/TerminalVector.ttf" "Keralam" --ppem 12 --mono -o terminalvector-keralam-native.png
font2badge "$MANJARI" "കേരളം" -H 16 -o manjari-keralam-h16.png
font2badge "$MUKTA" "केरलम" --ppem 9 -o mukta-keralam-ppem9.png

python3 - <<'EOF'
from pathlib import Path

from PIL import Image

for src in sorted(Path(".").glob("*.png")):
    if "@8x" in src.name:
        continue
    img = Image.open(src)
    big = img.resize((img.width * 8, img.height * 8), Image.NEAREST)
    big.save(src.with_name(f"{src.stem}@8x.png"))
    print(f"{src.name}: {img.width}x{img.height} -> @8x")
EOF
