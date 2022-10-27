from palettizer.palette import Palette, Color
from testutils import get_test_resource


PALETTE_1 = str(get_test_resource("test-palette-1.json"))
PALETTE_2 = str(get_test_resource("test-palette-2.json"))
PALETTE_3 = str(get_test_resource("test-palette-3.json"))
PALETTE_4 = str(get_test_resource("test-palette-4.json"))


def test_parse_palette__single_file():
    palette = Palette().from_file(PALETTE_1)

    assert len(palette.colors) == 3
    assert Color(255, 0, 0, name='Red', vendor='ABC Paints') in palette.colors
    assert Color(0, 255, 0, name='Green', vendor='ABC Paints') in palette.colors
    assert Color(0, 0, 255, name='Blue', vendor='ABC Paints') in palette.colors


def test_parse_palette__multiple_files():
    palette = Palette.from_files([PALETTE_1, PALETTE_2])

    assert len(palette.colors) == 6
    assert Color(255, 0, 0, name='Red', vendor='ABC Paints') in palette.colors
    assert Color(0, 255, 0, name='Green', vendor='ABC Paints') in palette.colors
    assert Color(0, 0, 255, name='Blue', vendor='ABC Paints') in palette.colors
    assert Color(255, 255, 0, name='Yellow', vendor='ABC Paints') in palette.colors
    assert Color(0, 255, 255, name='Cyan', vendor='ABC Paints') in palette.colors
    assert Color(255, 0, 255, name='Magenta', vendor='ABC Paints') in palette.colors


def test_parse_palette__url_and_name():
    palette = Palette().from_file(PALETTE_4)

    assert "My palette" == palette.name
    assert "https://google.com" == palette.url
    assert len(palette.colors) == 3
    assert Color(255, 0, 0, name='Red', vendor='ABC Paints') in palette.colors
    assert Color(0, 255, 0, name='Green', vendor='ABC Paints') in palette.colors
    assert Color(0, 0, 255, name='Blue', vendor='ABC Paints') in palette.colors


def test_get_predefined_palette__single_file():
    palette = Palette.from_predefined(['mtnblack'])

    assert palette is not None
    assert len(palette.colors) == 189
    assert Color(252, 249, 151, name="BLK 1005 Smash137's Potato", vendor="Montana Black") in palette.colors
    assert Color(255, 229, 112, name='BLK 1010 Easter yellow', vendor="Montana Black") in palette.colors
    assert Color(255, 220, 20, name='BLK 1025 Kicking yellow', vendor="Montana Black") in palette.colors


def test_get_predefined_palette__multiple_files():
    palette = Palette.from_predefined(['mtnblack', 'mtn94'])

    assert palette is not None
    assert len(palette.colors) == (189 + 136)
    assert Color(252, 249, 151, name="BLK 1005 Smash137's Potato", vendor="Montana Black") in palette.colors
    assert Color(255, 229, 112, name='BLK 1010 Easter yellow', vendor="Montana Black") in palette.colors
    assert Color(107, 99, 15, name="RV-112 Mission Green", vendor="MTN 94") in palette.colors
    assert Color(77, 73, 15, name="RV-113 Gragon Green", vendor="MTN 94") in palette.colors
