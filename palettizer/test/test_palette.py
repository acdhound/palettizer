from palettizer.palette import parse_palette, get_predefined_palette
from testutils import get_test_resource


PALETTE_1 = str(get_test_resource("test-palette-1.json"))
PALETTE_2 = str(get_test_resource("test-palette-2.json"))
PALETTE_3 = str(get_test_resource("test-palette-3.json"))


def test_parse_palette__single_file():
    palette = parse_palette(PALETTE_1)

    assert palette == [
        {'color': (255, 0, 0), 'name': 'Red', 'vendor': 'ABC Paints'},
        {'color': (0, 255, 0), 'name': 'Green', 'vendor': 'ABC Paints'},
        {'color': (0, 0, 255), 'name': 'Blue', 'vendor': 'ABC Paints'}
    ]


def test_parse_palette__multiple_files():
    palette = parse_palette("{},{}".format(PALETTE_1, PALETTE_2))

    assert palette == [
        {'color': (255, 0, 0), 'name': 'Red', 'vendor': 'ABC Paints'},
        {'color': (0, 255, 0), 'name': 'Green', 'vendor': 'ABC Paints'},
        {'color': (0, 0, 255), 'name': 'Blue', 'vendor': 'ABC Paints'},
        {'color': (255, 255, 0), 'name': 'Yellow', 'vendor': 'ABC Paints'},
        {'color': (0, 255, 255), 'name': 'Cyan', 'vendor': 'ABC Paints'},
        {'color': (255, 0, 255), 'name': 'Magenta', 'vendor': 'ABC Paints'}
    ]


def test_get_predefined_palette__single_file():
    palette = get_predefined_palette(['mtnblack'])

    assert palette is not None
    assert len(palette) == 189
    assert {'color': (252, 249, 151), 'name': "BLK 1005 Smash137's Potato", 'vendor': "Montana Black"} in palette
    assert {'color': (255, 229, 112), 'name': 'BLK 1010 Easter yellow', 'vendor': "Montana Black"} in palette
    assert {'color': (255, 220, 20), 'name': 'BLK 1025 Kicking yellow', 'vendor': "Montana Black"} in palette


def test_get_predefined_palette__multiple_files():
    palette = get_predefined_palette(['mtnblack', 'mtn94'])

    assert palette is not None
    assert len(palette) == (189 + 136)
    assert {'color': (252, 249, 151), 'name': "BLK 1005 Smash137's Potato", 'vendor': "Montana Black"} in palette
    assert {'color': (255, 229, 112), 'name': 'BLK 1010 Easter yellow', 'vendor': "Montana Black"} in palette
    assert {"color": (107, 99, 15), "name": "RV-112 Mission Green", "vendor": "MTN 94"} in palette
    assert {"color": (77, 73, 15), "name": "RV-113 Gragon Green", "vendor": "MTN 94"} in palette
