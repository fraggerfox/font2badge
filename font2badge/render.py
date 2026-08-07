"""Shape with HarfBuzz, rasterize with FreeType, threshold to an LED strip.

Default sizing is per-message self-scaling: the string's own ink span is
stretched to the full strip height. Pin ppem instead for native-size
renders of true pixel fonts (with mono) or for fair A/B comparisons.
"""

import sys

import freetype
import numpy as np
import uharfbuzz as hb


def shape(hb_font, text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hb_font, buf)
    return list(zip(buf.glyph_infos, buf.glyph_positions))


def ink_span(hb_font, run):
    """(bottom, top) of the shaped run's ink, in font units."""
    bottom, top = 1e9, -1e9
    for info, pos in run:
        ext = hb_font.get_glyph_extents(info.codepoint)
        if ext.width == 0 and ext.height == 0:
            continue
        t = pos.y_offset + ext.y_bearing
        top = max(top, t)
        bottom = min(bottom, t + ext.height)
    if top <= bottom:
        raise SystemExit("no ink in shaped text")
    return bottom, top


def render(font_path, text, height=11, threshold=0.5, ppem=None, mono=False):
    """Render text to a boolean (height x width) strip; returns (bits, ppem)."""
    blob = hb.Blob.from_file_path(str(font_path))
    hb_face = hb.Face(blob)
    upem = hb_face.upem
    ft = freetype.Face(str(font_path))

    probe = hb.Font(hb_face)  # default scale = upem
    bottom, top = ink_span(probe, shape(probe, text))
    if ppem is None:
        ppem = height * upem / (top - bottom)

    ft.set_char_size(int(round(ppem * 64)))
    hb_font = hb.Font(hb_face)
    hb_font.scale = (int(round(ppem * 64)),) * 2
    run = shape(hb_font, text)

    width = int(sum(p.x_advance for _, p in run) / 64) + int(ppem) + 8
    panel = np.zeros((height, width), np.uint8)
    span_px = (top - bottom) * ppem / upem
    top_px = top * ppem / upem + max(0, (height - round(span_px)) // 2)

    flags = freetype.FT_LOAD_RENDER
    if mono:
        flags |= freetype.FT_LOAD_TARGET_MONO

    pen_x, clipped = 2.0, 0
    for info, pos in run:
        ft.load_glyph(info.codepoint, flags)
        g, bm = ft.glyph, ft.glyph.bitmap
        if bm.width and bm.rows:
            raw = np.frombuffer(bytes(bm.buffer), np.uint8).reshape(bm.rows, bm.pitch)
            if mono:
                arr = np.unpackbits(raw, axis=1)[:, : bm.width] * np.uint8(255)
            else:
                arr = raw[:, : bm.width]
            x = int(round(pen_x + pos.x_offset / 64 + g.bitmap_left))
            y = int(round(top_px - (pos.y_offset / 64 + g.bitmap_top)))
            r0, c0 = max(y, 0), max(x, 0)
            r1, c1 = min(y + arr.shape[0], height), min(x + arr.shape[1], width)
            if r1 > r0 and c1 > c0:
                dst = panel[r0:r1, c0:c1]
                np.maximum(dst, arr[r0 - y : r1 - y, c0 - x : c1 - x], out=dst)
            clipped += int((arr > 0).sum()) - int(
                (arr[r0 - y : r1 - y, c0 - x : c1 - x] > 0).sum()
            )
        pen_x += pos.x_advance / 64
    if clipped:
        print(f"WARNING: {clipped} ink pixels fell outside the strip", file=sys.stderr)

    if mono:
        bits = panel > 0
    else:
        bits = panel >= max(int(panel.max() * threshold), 1)
    cols = np.where(bits.any(axis=0))[0]
    if len(cols) == 0:
        raise SystemExit("threshold erased all ink — try a lower --threshold")
    lo, hi = max(cols.min() - 1, 0), min(cols.max() + 2, bits.shape[1])
    return bits[:, lo:hi], ppem
