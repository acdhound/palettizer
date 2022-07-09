import numpy as np
from palettizer.quantize import quantize
from palettizer.palette import Palette, Color
from testutils import get_test_resource


IMAGE_4_SQUARES = str(get_test_resource("4_squares.png"))
IMAGE_2_SQUARES = str(get_test_resource("2_squares.png"))
IMAGE_BLISS = str(get_test_resource("bliss.jpg"))

RED = Color(255, 0, 0, name='red', vendor='ABC Paints')
YELLOW = Color(255, 255, 0, name='yellow', vendor='ABC Paints')
GREEN = Color(0, 255, 0, name='green', vendor='ABC Paints')
BLUE = Color(0, 0, 255, name='blue', vendor='ABC Paints')
PALETTE_4_COLORS = Palette([RED, YELLOW, GREEN, BLUE])
RED_PIXEL = np.array([255, 0, 0], dtype=np.uint8)
YELLOW_PIXEL = np.array([255, 255, 0], dtype=np.uint8)
GREEN_PIXEL = np.array([0, 255, 0], dtype=np.uint8)
BLUE_PIXEL = np.array([0, 0, 255], dtype=np.uint8)

PALETTE_MTN_BLACK = Palette.from_file(str(get_test_resource("mtnblack-palette.json")))
BLK_6725 = Color(70, 89, 13, name="BLK 6725 Troops", vendor="Montana Black")
BLK_4320 = Color(146, 167, 227, name="BLK 4320 Brunhilde", vendor="Montana Black")
BLK_5230 = Color(27, 144, 222, name="BLK 5230 Blue Lagoon", vendor="Montana Black")
BLK_TR5010_PIXEL = np.array([84, 174, 227], dtype=np.uint8)
BLK_6710_PIXEL = np.array([147, 184, 39], dtype=np.uint8)
BLK_9100_PIXEL = np.array([255, 255, 255], dtype=np.uint8)


def test_quantize__4_colors_palette():
    output_img, histogram = quantize(img=IMAGE_4_SQUARES,
                                     palette=PALETTE_4_COLORS,
                                     n_colors=0)

    assert output_img is not None
    assert output_img.shape == (40, 40, 3)
    assert output_img.dtype == np.uint8
    assert np.array_equal(output_img[0][0], RED_PIXEL)
    assert np.array_equal(output_img[10][10], RED_PIXEL)
    assert np.array_equal(output_img[18][18], RED_PIXEL)
    assert np.array_equal(output_img[0][20], YELLOW_PIXEL)
    assert np.array_equal(output_img[10][30], YELLOW_PIXEL)
    assert np.array_equal(output_img[18][38], YELLOW_PIXEL)
    assert np.array_equal(output_img[20][0], BLUE_PIXEL)
    assert np.array_equal(output_img[30][10], BLUE_PIXEL)
    assert np.array_equal(output_img[38][18], BLUE_PIXEL)
    assert np.array_equal(output_img[20][20], GREEN_PIXEL)
    assert np.array_equal(output_img[30][30], GREEN_PIXEL)
    assert np.array_equal(output_img[38][38], GREEN_PIXEL)

    assert histogram is not None
    assert {'color': RED, 'pixels': 400} in histogram.values()
    assert {'color': YELLOW, 'pixels': 400} in histogram.values()
    assert {'color': GREEN, 'pixels': 400} in histogram.values()
    assert {'color': BLUE, 'pixels': 400} in histogram.values()


def test_quantize__4_colors_palette__max_2_colors():
    output_img, histogram = quantize(img=IMAGE_2_SQUARES,
                                     palette=PALETTE_4_COLORS,
                                     n_colors=2)

    assert output_img is not None
    assert output_img.shape == (20, 40, 3)
    assert output_img.dtype == np.uint8
    assert np.array_equal(output_img[0][0], RED_PIXEL)
    assert np.array_equal(output_img[10][10], RED_PIXEL)
    assert np.array_equal(output_img[18][18], RED_PIXEL)
    assert np.array_equal(output_img[0][20], YELLOW_PIXEL)
    assert np.array_equal(output_img[10][30], YELLOW_PIXEL)
    assert np.array_equal(output_img[18][38], YELLOW_PIXEL)

    assert histogram is not None
    assert len(histogram.keys()) == 2
    assert {'color': RED, 'pixels': 400} in histogram.values()
    assert {'color': YELLOW, 'pixels': 400} in histogram.values()


def test_quantize__large_image__4_colors_palette():
    output_img, histogram = quantize(img=IMAGE_BLISS,
                                     palette=PALETTE_4_COLORS,
                                     n_colors=0)

    assert output_img is not None
    assert output_img.shape == (1080, 1920, 3)
    assert output_img.dtype == np.uint8
    assert np.array_equal(output_img[221][779], BLUE_PIXEL)
    assert np.array_equal(output_img[411][1503], YELLOW_PIXEL)
    assert np.array_equal(output_img[737][1175], GREEN_PIXEL)
    assert np.array_equal(output_img[1019][477], RED_PIXEL)

    assert histogram is not None
    assert {'color': RED, 'pixels': 4176} in histogram.values()
    assert {'color': YELLOW, 'pixels': 234877} in histogram.values()
    assert {'color': GREEN, 'pixels': 780095} in histogram.values()
    assert {'color': BLUE, 'pixels': 1054452} in histogram.values()


def test_quantize__large_image__real_palette():
    output_img, histogram = quantize(img=IMAGE_BLISS,
                                     palette=PALETTE_MTN_BLACK,
                                     n_colors=0)

    assert output_img is not None
    assert output_img.shape == (1080, 1920, 3)
    assert output_img.dtype == np.uint8
    assert np.array_equal(output_img[79][260], BLK_TR5010_PIXEL)
    assert np.array_equal(output_img[644][160], BLK_6710_PIXEL)
    assert np.array_equal(output_img[374][1500], BLK_9100_PIXEL)

    assert histogram is not None
    assert {'color': BLK_6725, 'pixels': 241127} in histogram.values()
    assert {'color': BLK_4320, 'pixels': 241503} in histogram.values()
    assert {'color': BLK_5230, 'pixels': 276362} in histogram.values()


def test_quantize__binary_image():
    with open(IMAGE_4_SQUARES, 'rb') as f:
        image_bin = f.read()

    output_img, histogram = quantize(img=image_bin,
                                     palette=PALETTE_4_COLORS,
                                     n_colors=0)

    assert output_img is not None
    assert output_img.shape == (40, 40, 3)
    assert output_img.dtype == np.uint8
    assert np.array_equal(output_img[0][0], RED_PIXEL)
    assert np.array_equal(output_img[0][20], YELLOW_PIXEL)
    assert np.array_equal(output_img[20][0], BLUE_PIXEL)
    assert np.array_equal(output_img[20][20], GREEN_PIXEL)

    assert histogram is not None
    assert {'color': RED, 'pixels': 400} in histogram.values()
    assert {'color': YELLOW, 'pixels': 400} in histogram.values()
    assert {'color': GREEN, 'pixels': 400} in histogram.values()
    assert {'color': BLUE, 'pixels': 400} in histogram.values()
