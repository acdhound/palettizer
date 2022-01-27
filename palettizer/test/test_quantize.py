from palettizer.quantize import read_rgb_image
from palettizer.quantize import quantize
import os
from pathlib import Path
import numpy as np


RED = np.array([255, 0, 0], dtype=np.uint8)
YELLOW = np.array([255, 255, 0], dtype=np.uint8)
GREEN = np.array([0, 255, 0], dtype=np.uint8)
BLUE = np.array([0, 0, 255], dtype=np.uint8)
PALETTE_4_COLORS = [
    {'color': (255, 0, 0), 'name': 'red', 'vendor': 'ABC Paints'},
    {'color': (255, 255, 0), 'name': 'yellow', 'vendor': 'ABC Paints'},
    {'color': (0, 255, 0), 'name': 'green', 'vendor': 'ABC Paints'},
    {'color': (0, 0, 255), 'name': 'blue', 'vendor': 'ABC Paints'}
]

RESOURCES_DIR = Path(os.path.realpath(__file__)).parent.absolute()
IMAGE_4_SQUARES = str(RESOURCES_DIR.joinpath("resources/4_squares.png"))


def test_read_rgb_image():
    img = read_rgb_image(IMAGE_4_SQUARES)
    assert img is not None
    assert img.shape == (40, 40, 3)
    assert img.dtype == np.uint8


def test_quantize__4_colors_palette():
    output_img, hystogram = quantize(img_path=IMAGE_4_SQUARES,
                                     palette=PALETTE_4_COLORS,
                                     n_colors=0)

    assert output_img is not None
    assert output_img.shape == (40, 40, 3)
    assert output_img.dtype == np.uint8
    assert np.array_equal(output_img[0][0], RED)
    assert np.array_equal(output_img[10][10], RED)
    assert np.array_equal(output_img[18][18], RED)
    assert np.array_equal(output_img[0][20], YELLOW)
    assert np.array_equal(output_img[10][30], YELLOW)
    assert np.array_equal(output_img[18][38], YELLOW)
    assert np.array_equal(output_img[20][0], BLUE)
    assert np.array_equal(output_img[30][10], BLUE)
    assert np.array_equal(output_img[38][18], BLUE)
    assert np.array_equal(output_img[20][20], GREEN)
    assert np.array_equal(output_img[30][30], GREEN)
    assert np.array_equal(output_img[38][38], GREEN)

    # why not 400?
    assert hystogram == {0: 399, 1: 399, 2: 399, 3: 399}
