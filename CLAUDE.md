# CLAUDE.md — font2badge

Any font + text → a badge-ready PNG. Shape with HarfBuzz, rasterize with
FreeType, threshold to a white-on-black strip exactly the badge's pixel
height. Read `README.md` for usage and the flag reference; this is the
**simple pipeline** — the sibling [pixelshaper](https://github.com/fraggerfox/pixelshaper)
is the crafted one (hand-tunable pixel fonts). Start here; graduate there
when thresholding artifacts bite.

## Layout

```
font2badge/           the package
  render.py           shape (HarfBuzz) -> ink span -> raster (FreeType) -> threshold -> bool grid
  cli.py              argparse -> render() -> PNG (+ optional ●/· dots)
  __init__.py         no __version__ here; version lives in pyproject.toml
tests/                pytest suite (render + CLI), fonts/ vendored donors
examples/             one PNG per README example + an @8x display copy; generate.sh regenerates
```

Dev shell: `nix develop` (uv + native libs, venv activated). Run
`font2badge <font.ttf> "<text>" [flags]` directly, or `uv run pytest`.

## How it works

- **Self-scaling is the default.** The whole string is shaped once, its
  ink span measured in font units, and the ppem chosen so *this message's*
  ink fills the strip: `ppem = H × upem ÷ span`. Every message gets the
  largest size its own shapes allow — unlike corpus-keyed scaling, which
  sizes for the worst case and leaves ordinary words half-height.
- **Thresholding turns grayscale into on/off** at `--threshold` × peak
  gray. Solid fonts: 0.5. Dotted fonts (Nupuram Dots): ~0.25, or the dots
  vanish. The 1px/2px stroke flicker near the cut is inherent — it's what
  pixelshaper's hand-tuning fixes.
- **`--mono` is for true pixel fonts on their native grid** (`--ppem
  <native> --mono`): 1-bit rendering reproduces the design bit-for-bit.
  Never use it on outline fonts (thin strokes drop) or with self-scaling
  (fractional ppem straddles pixels). This rule is the README's core.

## Conventions

- **Keep the CLI a thin wrapper** over `render()`. Sizing/raster logic
  lives in `render.py`; `cli.py` only parses args and writes the PNG.
- **`render()` returns a boolean grid** (`height × width`) plus the ppem —
  the grid *is* the PNG (True = lit). Tests assert on the grid, not files.
- **Read/write nothing but fonts (in) and PNGs (out).** No config files,
  no state; every invocation is one font, one string.
- **Example PNGs are generated, not hand-made:** `examples/generate.sh`
  produces both the 1:1 strip and the `@8x` nearest-neighbour display copy
  (GitHub blur-scales `<img>`; the `@8x` is how the README shows crisp
  pixels). Regenerate rather than edit.

## Commits & releases

- **Conventional Commits are required for PR titles** (enforced by
  `.github/workflows/pr-title.yml`). We squash-merge, so the PR title is
  the commit on main — write it `type: summary` (`feat`, `fix`, `docs`,
  `ci`, `test`, `build`, `chore`, `refactor`, `perf`, `style`, `revert`;
  `type!:` / `BREAKING CHANGE:` for breaking).
- **Only `feat:`/`fix:`/breaking bump the version;** everything else just
  lands in the changelog.
- **Releases are automated by release-please** (`.github/workflows/cd.yaml`).
  It keeps a release PR that bumps `pyproject.toml` (via the `python`
  release-type) and CHANGELOG; merging it tags `vX.Y.Z`. Never bump the
  version by hand. Seed is `.release-please-manifest.json`; pre-1.0 bump
  flags in `release-please-config.json` keep breaking changes inside 0.x.
- The CD run needs **"Allow GitHub Actions to create and approve pull
  requests"** on in Settings → Actions → General, or the release PR can't
  open.

## Related (not in this repo)

- [pixelshaper](https://github.com/fraggerfox/pixelshaper) — the crafted
  pipeline; font2badge's self-scaled bitmaps are what it freezes into
  editable pixel-font glyphs.
- Display consumer: `led-name-badge-ls32` — push a strip with
  `lednamebadge.py -s 4 -m 4 strip.png` (mode 4 = still-centered); the PNG
  must be exactly the badge's pixel height.
