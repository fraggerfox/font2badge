# font2badge

Any font + some text → a badge-ready PNG. Shapes the text with HarfBuzz
(conjuncts, matra reordering, mark positioning — Indic scripts come out
right), rasterizes with FreeType, and writes a white-on-black strip PNG
at exactly your badge's pixel height, ready to feed to
[led-name-badge-ls32](https://github.com/fossasia/led-name-badge-ls32)
for pushing to the badge.

This is the **simple pipeline**: no font conversion, no hand-editing —
one command from TTF to badge. Its sibling
[pixelshaper](https://github.com/fraggerfox/pixelshaper) is the crafted
pipeline: it freezes the same intermediate bitmaps into an editable
pixel font you can hand-tune glyph by glyph. Start here; graduate to
pixelshaper when the thresholding artifacts start to bother you.

## Usage

```sh
nix develop            # uv dev shell, venv activated

# Malayalam, self-scaled so the message's ink fills all 11 rows
font2badge fonts/Manjari-Regular.ttf "പക്ഷി വാഴ" --dots

# a different badge? set its pixel height
font2badge fonts/Manjari-Regular.ttf "കേരളം" -H 16

# dotted fonts need a lower threshold or the dots vanish
font2badge fonts/Nupuram-Dots.ttf "കേരളം" -t 0.25

# true pixel fonts: render at native size, 1-bit
font2badge fonts/k8x12.ttf "Keralam" --ppem 12 --mono

# pin ppem for a fair A/B against a pixel font of that size
font2badge fonts/Mukta-Regular.ttf "केरलम" --ppem 9
```

Flags: `-H/--height` strip height in px (default 11, the FOSSASIA LS32
badge), `-t/--threshold` on/off cut (default 0.5), `--ppem` to pin the
size instead of self-scaling, `--mono` for 1-bit rendering of true
pixel fonts, `--dots` to print the strip as ●/· rows in the terminal,
`-o` for the output path (default `<font>-<md5:8>.png`).

Push the result to the badge:

```sh
python3 lednamebadge.py -s 4 -m 4 strip.png   # mode 4 = still-centered
```

## How it sizes

By default the whole string is shaped once, its ink span measured in
font units, and the ppem chosen so *this message's* ink exactly fills
the strip height (`ppem = H × upem ÷ span`). That differs from
corpus-keyed scaling (sizing for the worst-case conjunct stack), which
leaves ordinary words half-height — here every message gets the largest
size its own shapes allow.

The grayscale raster is cut to on/off at `--threshold` × peak gray.
Antialiased curves hovering near the cut flip between 1 px and 2 px
thick — that raggedness is inherent to thresholding outlines at LED
sizes, and is exactly what pixelshaper's hand-tuned pixel fonts fix.
