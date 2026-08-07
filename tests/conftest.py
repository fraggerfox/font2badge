from pathlib import Path

import pytest

FONTS_DIR = Path(__file__).parent / "fonts"
FONT = FONTS_DIR / "Manjari-Regular.ttf"


@pytest.fixture()
def manjari():
    """The vendored donor most tests use."""
    return FONT


@pytest.fixture()
def fonts_dir():
    """All vendored fonts: Manjari, Noto, Mukta, k8x12, TerminalVector."""
    return FONTS_DIR
