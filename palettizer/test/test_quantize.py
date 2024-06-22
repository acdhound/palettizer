import numpy as np

from palettizer.quantize import quantize
from palettizer.quantize import EUCLIDEAN_METRIC, DELTA_E_METRIC
from palettizer.palette import Palette, Color
from testutils import get_test_resource

import pytest


IMAGE_4_SQUARES = str(get_test_resource("4_squares.png"))
IMAGE_2_SQUARES = str(get_test_resource("2_squares.png"))
IMAGE_BLISS = str(get_test_resource("bliss.jpg"))
IMAGE_BLISS_WDT = 1920
IMAGE_BLISS_HGT = 1080
IMAGE_BLISS_AREA = IMAGE_BLISS_HGT * IMAGE_BLISS_WDT
IMAGE_OCTOBER = str(get_test_resource("october.jpg"))

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
BLK_4320_PIXEL = np.array([146, 167, 227], dtype=np.uint8)
BLK_6725_PIXEL = np.array([70, 89, 13], dtype=np.uint8)


@pytest.mark.parametrize("metric", [EUCLIDEAN_METRIC, DELTA_E_METRIC])
def test_quantize__4_colors_palette(metric):
    result = quantize(img=IMAGE_4_SQUARES,
                      palette=PALETTE_4_COLORS,
                      n_colors=0,
                      metric=metric)

    assert result.image is not None
    assert result.image.shape == (40, 40, 3)
    assert result.image.dtype == np.uint8
    assert np.array_equal(result.image[0][0], RED_PIXEL)
    assert np.array_equal(result.image[10][10], RED_PIXEL)
    assert np.array_equal(result.image[18][18], RED_PIXEL)
    assert np.array_equal(result.image[0][20], YELLOW_PIXEL)
    assert np.array_equal(result.image[10][30], YELLOW_PIXEL)
    assert np.array_equal(result.image[18][38], YELLOW_PIXEL)
    assert np.array_equal(result.image[20][0], BLUE_PIXEL)
    assert np.array_equal(result.image[30][10], BLUE_PIXEL)
    assert np.array_equal(result.image[38][18], BLUE_PIXEL)
    assert np.array_equal(result.image[20][20], GREEN_PIXEL)
    assert np.array_equal(result.image[30][30], GREEN_PIXEL)
    assert np.array_equal(result.image[38][38], GREEN_PIXEL)

    assert result.color_pixels is not None
    assert len(result.color_pixels.keys()) == 4
    assert result.color_pixels[RED] == 400
    assert result.color_pixels[YELLOW] == 400
    assert result.color_pixels[GREEN] == 400
    assert result.color_pixels[BLUE] == 400


@pytest.mark.parametrize("metric", [EUCLIDEAN_METRIC, DELTA_E_METRIC])
def test_quantize__4_colors_palette__max_2_colors(metric):
    result = quantize(img=IMAGE_2_SQUARES,
                      palette=PALETTE_4_COLORS,
                      n_colors=2,
                      metric=metric)

    assert result.image is not None
    assert result.image.shape == (20, 40, 3)
    assert result.image.dtype == np.uint8
    assert np.array_equal(result.image[0][0], RED_PIXEL)
    assert np.array_equal(result.image[10][10], RED_PIXEL)
    assert np.array_equal(result.image[18][18], RED_PIXEL)
    assert np.array_equal(result.image[0][20], YELLOW_PIXEL)
    assert np.array_equal(result.image[10][30], YELLOW_PIXEL)
    assert np.array_equal(result.image[18][38], YELLOW_PIXEL)

    assert result.color_pixels is not None
    assert len(result.color_pixels.keys()) == 2
    assert result.color_pixels[RED] == 400
    assert result.color_pixels[YELLOW] == 400


@pytest.mark.parametrize("metric", [EUCLIDEAN_METRIC, DELTA_E_METRIC])
def test_quantize__large_image__4_colors_palette(metric):
    result = quantize(img=IMAGE_BLISS,
                      palette=PALETTE_4_COLORS,
                      n_colors=0,
                      metric=metric)

    assert result.image is not None
    assert result.image.shape == (IMAGE_BLISS_HGT, IMAGE_BLISS_WDT, 3)
    assert result.image.dtype == np.uint8
    assert np.array_equal(result.image[221][779], BLUE_PIXEL)
    assert np.array_equal(result.image[411][1503], YELLOW_PIXEL)
    assert np.array_equal(result.image[737][1175], GREEN_PIXEL)
    assert np.array_equal(result.image[1019][477], RED_PIXEL)

    assert result.color_pixels is not None
    assert len(result.color_pixels.keys()) == 4
    assert 0 < result.color_pixels[RED] < 0.1 * IMAGE_BLISS_AREA
    assert 0 < result.color_pixels[YELLOW] < 0.2 * IMAGE_BLISS_AREA
    assert 0.3 * IMAGE_BLISS_AREA < result.color_pixels[GREEN] < 0.6 * IMAGE_BLISS_AREA
    assert 0.4 * IMAGE_BLISS_AREA < result.color_pixels[BLUE] < 0.7 * IMAGE_BLISS_AREA


@pytest.mark.parametrize("n_colors,metric", [(0, EUCLIDEAN_METRIC), (0, DELTA_E_METRIC),
                                             (15, EUCLIDEAN_METRIC), (15, DELTA_E_METRIC),
                                             (50, EUCLIDEAN_METRIC), (50, DELTA_E_METRIC)])
def test_quantize__large_image__real_palette(n_colors, metric):
    result = quantize(img=IMAGE_BLISS,
                      palette=PALETTE_MTN_BLACK,
                      n_colors=n_colors,
                      metric=metric)

    assert result.image is not None
    assert result.image.shape == (IMAGE_BLISS_HGT, IMAGE_BLISS_WDT, 3)
    assert result.image.dtype == np.uint8

    assert np.array_equal(result.image[441][327], BLK_4320_PIXEL)
    assert np.array_equal(result.image[799][1761], BLK_6725_PIXEL)

    assert result.color_pixels is not None
    assert 0.1 * IMAGE_BLISS_AREA < result.color_pixels[BLK_4320] < 0.3 * IMAGE_BLISS_AREA
    assert 0.05 * IMAGE_BLISS_AREA < result.color_pixels[BLK_6725] < 0.3 * IMAGE_BLISS_AREA


def test_quantize__large_image__resize():
    result = quantize(img=IMAGE_OCTOBER,
                      palette=PALETTE_MTN_BLACK,
                      n_colors=0)

    assert result.image is not None
    assert result.image.shape == (1500, 2000, 3)
    assert result.image.dtype == np.uint8

    assert result.color_pixels is not None


def test_quantize__image_as_bytes():
    with open(IMAGE_4_SQUARES, 'rb') as f:
        image_bin = f.read()

    result = quantize(img=image_bin,
                      palette=PALETTE_4_COLORS,
                      n_colors=0)

    assert result.image is not None
    assert result.image.shape == (40, 40, 3)
    assert result.image.dtype == np.uint8
    assert np.array_equal(result.image[0][0], RED_PIXEL)
    assert np.array_equal(result.image[0][20], YELLOW_PIXEL)
    assert np.array_equal(result.image[20][0], BLUE_PIXEL)
    assert np.array_equal(result.image[20][20], GREEN_PIXEL)

    assert result.color_pixels is not None
    assert result.color_pixels[RED] == 400
    assert result.color_pixels[YELLOW] == 400
    assert result.color_pixels[GREEN] == 400
    assert result.color_pixels[BLUE] == 400


def test_quantize__no_palette():
    result = quantize(img=IMAGE_4_SQUARES,
                      palette=None,
                      n_colors=4)

    assert result.image is not None
    assert result.image.shape == (40, 40, 3)
    assert result.image.dtype == np.uint8
    red = result.image[0][0]
    assert red[0] > red[1] and red[0] > red[2]
    assert np.array_equal(result.image[10][10], red)
    assert np.array_equal(result.image[18][18], red)
    yellow = result.image[0][20]
    assert yellow[0] > yellow[2] and yellow[1] > yellow[2]
    assert np.array_equal(result.image[10][30], yellow)
    assert np.array_equal(result.image[18][38], yellow)
    blue = result.image[20][0]
    assert blue[2] > blue[0] and blue[2] > blue[1]
    assert np.array_equal(result.image[30][10], blue)
    assert np.array_equal(result.image[38][18], blue)
    green = result.image[20][20]
    assert green[1] > green[0] and green[1] > green[2]
    assert np.array_equal(result.image[30][30], green)
    assert np.array_equal(result.image[38][38], green)

    assert result.color_pixels is not None
    assert len(result.color_pixels.keys()) == 4
    for k in result.color_pixels:
        assert result.color_pixels[k] == 400
