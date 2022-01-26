from palettizer.quantize import read_rgb_image
import os
from pathlib import Path


def test_read_rgb_image():
    resources_dir = Path(os.path.realpath(__file__)).parent.absolute()
    img_path = str(resources_dir.joinpath("resources/4_squares.png").absolute())
    img = read_rgb_image(img_path)
    assert img is not None
    assert img.shape == (40, 40, 3)
