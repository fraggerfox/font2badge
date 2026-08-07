"""render(): sizing, thresholds, mono, and failure modes."""

import numpy as np
import pytest

from font2badge.render import render


def test_self_scale_fills_the_strip(manjari):
    bits, ppem = render(manjari, "കേരളം")
    assert bits.dtype == bool
    assert bits.shape[0] == 11
    # self-scaling stretches this word's ink across every row
    assert all(bits[row].any() for row in range(11))
    # trimming leaves at most one blank column at each edge
    assert bits[:, :2].any() and bits[:, -2:].any()
    assert 16 < ppem < 18  # known landscape: കേരളം self-scales to ~16.9


def test_height_is_configurable(manjari):
    bits11, ppem11 = render(manjari, "കേരളം", height=11)
    bits16, ppem16 = render(manjari, "കേരളം", height=16)
    assert bits16.shape[0] == 16
    # more rows -> proportionally larger ppem and wider strip
    assert ppem16 > ppem11
    assert bits16.shape[1] > bits11.shape[1]


def test_pinned_ppem_overrides_self_scaling(manjari):
    bits, ppem = render(manjari, "കേരളം", ppem=9)
    assert ppem == 9
    # at 9 ppem the word is far short of the 11-row strip -> blank rows
    assert not all(bits[row].any() for row in range(11))


def test_lower_threshold_keeps_more_ink(manjari):
    faint, _ = render(manjari, "കേരളം", threshold=0.25)
    strict, _ = render(manjari, "കേരളം", threshold=0.75)
    assert faint.sum() > strict.sum()


def test_mono_returns_clean_bits(manjari):
    bits, ppem = render(manjari, "ക", ppem=12, mono=True)
    assert bits.dtype == bool
    assert bits.any()
    assert ppem == 12


def test_pixel_fonts_at_native_grid(fonts_dir):
    # true pixel fonts at their native 12 ppem in 1-bit: known widths
    k8, _ = render(fonts_dir / "k8x12.ttf", "Keralam", ppem=12, mono=True)
    tv, _ = render(fonts_dir / "TerminalVector.ttf", "Keralam", ppem=12, mono=True)
    assert k8.shape == (11, 29)
    assert tv.shape == (11, 57)


def test_other_donors_shape_and_fill(fonts_dir):
    # Noto (Malayalam) and Mukta (Devanagari) self-scale to the strip too
    noto, noto_ppem = render(fonts_dir / "NotoSansMalayalam-Regular.ttf", "കേരളം")
    mukta, _ = render(fonts_dir / "Mukta-Regular.ttf", "केरलम")
    assert noto.shape[0] == 11 and noto.any()
    assert 13 < noto_ppem < 15  # roomier marks than Manjari's 16.9
    # Mukta's shirorekha: one row is a near-continuous run of ink
    coverage = mukta.sum(axis=1) / mukta.shape[1]
    assert coverage.max() > 0.8


def test_shaping_is_applied(manjari):
    # ക്ക must form the k1k1 conjunct ligature, not render as ക + ് + ക:
    # the shaped strip is therefore narrower than two bare കക
    conjunct, _ = render(manjari, "ക്ക", ppem=14)
    two_kas, _ = render(manjari, "കക", ppem=14)
    assert conjunct.shape[1] < two_kas.shape[1]


def test_whitespace_only_text_fails(manjari):
    with pytest.raises(SystemExit, match="no ink"):
        render(manjari, "   ")


def test_impossible_threshold_fails(manjari):
    with pytest.raises(SystemExit, match="threshold erased"):
        render(manjari, "കേരളം", threshold=5.0)


def test_ink_is_where_the_dots_say(manjari):
    # the boolean grid is the PNG: row/column counts match a fresh render
    bits, _ = render(manjari, "ക")
    again, _ = render(manjari, "ക")
    assert np.array_equal(bits, again)
