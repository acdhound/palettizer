import numpy as np
import pytest
from palettizer.imgutils import read_rgb_image
from testutils import get_test_resource


IMAGE_PATH = str(get_test_resource("4_squares.png"))


def test_read_rgb_image__from_path():
    img = read_rgb_image(IMAGE_PATH)

    assert img is not None
    assert img.shape == (40, 40, 3)
    assert img.dtype == np.uint8


def test_read_rgb_image__from_binary():
    with open(IMAGE_PATH, 'rb') as f:
        image_bin = f.read()

    img = read_rgb_image(image_bin)

    assert img is not None
    assert img.shape == (40, 40, 3)
    assert img.dtype == np.uint8


def test_read_rgb_image__unknown_format():
    with pytest.raises(Exception):
        read_rgb_image(123)
