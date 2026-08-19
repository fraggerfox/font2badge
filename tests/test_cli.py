"""CLI: argument handling, output naming, --dots."""

import hashlib
from pathlib import Path

from PIL import Image

from font2badge import cli

FONT = Path(__file__).parent / "fonts" / "Manjari-Regular.ttf"


def run(monkeypatch, tmp_path, *args):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["font2badge", str(FONT), *args])
    cli.main()


def test_default_output_name(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, "കേരളം")
    digest = hashlib.md5("കേരളം".encode()).hexdigest()[:8]
    out = tmp_path / f"manjari-regular-{digest}.png"
    assert out.exists()
    assert out.name in capsys.readouterr().out


def test_output_path_and_png_contents(monkeypatch, tmp_path):
    run(monkeypatch, tmp_path, "ക", "-o", "strip.png")
    img = Image.open(tmp_path / "strip.png")
    assert img.height == 11
    assert img.mode == "L"
    colors = {value for _, value in img.getcolors()}
    assert colors <= {0, 255}  # strictly white-on-black


def test_height_flag(monkeypatch, tmp_path):
    run(monkeypatch, tmp_path, "ക", "-H", "16", "-o", "tall.png")
    assert Image.open(tmp_path / "tall.png").height == 16


def test_dots_prints_the_strip(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, "ക", "--dots", "-o", "ka.png")
    out = capsys.readouterr().out
    cells = {"●", "·", " "}
    dot_rows = [line for line in out.splitlines() if line and set(line) <= cells]
    assert len(dot_rows) == 11
    assert any("●" in row for row in dot_rows)
