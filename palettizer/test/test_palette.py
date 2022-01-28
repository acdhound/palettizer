from palettizer.palette import parse_palette
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


def test_parse_palette__real_colors():
    palette = parse_palette(PALETTE_3)

    assert palette == [
        {'color': (252, 249, 151), 'name': "BLK 1005 Smash137's Potato", 'vendor': "Montana Black"},
        {'color': (255, 229, 112), 'name': 'BLK 1010 Easter yellow', 'vendor': "Montana Black"},
        {'color': (255, 220, 20), 'name': 'BLK 1025 Kicking yellow', 'vendor': "Montana Black"}
    ]
