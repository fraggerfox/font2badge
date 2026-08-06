# stripshaper

Render text with a **raw outline font** into an LED-badge-ready strip
PNG: white-on-black, exactly the strip height (11 px for the FOSSASIA
LS32 badge), shaped by HarfBuzz so conjuncts, matra reordering and mark
positioning come out right for Indic scripts.

This is the "no pixel font" half of the badge workflow — the A/B
partner to [pixelshaper](https://github.com/fraggerfox/pixelshaper),
which derives hand-tunable pixel fonts from the same donors.

## Usage

```sh
nix develop            # uv dev shell, venv activated

# Malayalam, self-scaled so the message's ink fills all 11 rows
stripshaper fonts/Manjari-Regular.ttf "പക്ഷി വാഴ" --dots

# dotted fonts need a lower threshold or the dots vanish
stripshaper fonts/Nupuram-Dots.ttf "കേരളം" -t 0.25

# true pixel fonts: render at native size, 1-bit
stripshaper fonts/k8x12.ttf "Keralam" --ppem 12 --mono

# pin ppem for a fair A/B against a pixel font of that size
stripshaper fonts/Mukta-Regular.ttf "केरलम" --ppem 9
```

Output defaults to `<font>-<md5:8>.png` in the current directory;
`-o` overrides. Push to the badge with
[led-name-badge-ls32](https://github.com/fossasia/led-name-badge-ls32):

```sh
python3 lednamebadge.py -s 4 -m 4 strip.png   # mode 4 = still-centered
```

## How it sizes

By default the whole string is shaped once, its ink span measured in
font units, and the ppem chosen so *this message's* ink exactly fills
the strip height (`ppem = H × upem ÷ span`). That differs from
corpus-keyed scaling (sizing for the worst-case conjunct stack, as the
[malayalam-led-simulator](https://labs.thottingal.in/malayalam-led-simulator/)
does), which leaves ordinary words half-height.

The grayscale raster is cut to on/off at `--threshold` × peak gray.
Antialiased curves hovering near the cut flip between 1 px and 2 px
thick — that raggedness is inherent to thresholding outlines at LED
sizes, and is exactly what hand-tuned pixel fonts fix.
