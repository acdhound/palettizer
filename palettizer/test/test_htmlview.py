from palettizer.htmlview import image_and_palette_as_html
from palettizer.imgutils import read_rgb_image
from palettizer.quantize import quantize
from testutils import get_test_resource


PALETTE = [
  {'color': (255, 0, 0), 'name': 'red', 'vendor': 'ABC Paints'},
  {'color': (255, 255, 0), 'name': 'yellow', 'vendor': 'ABC Paints'},
  {'color': (0, 255, 0), 'name': 'green', 'vendor': 'ABC Paints'},
  {'color': (0, 0, 255), 'name': 'blue', 'vendor': 'ABC Paints'}
]
IMAGE_PATH = str(get_test_resource("bliss.jpg"))


def test_image_and_palette_as_html():
    img = read_rgb_image(IMAGE_PATH)
    colors = {
        1: {'color': PALETTE[0], "pixels": 10},
        2: {'color': PALETTE[1], "pixels": 20},
        3: {'color': PALETTE[2], "pixels": 30},
        4: {'color': PALETTE[3], "pixels": 40}
    }

    rendered_html = image_and_palette_as_html(img, colors)

    assert rendered_html is not None
    assert len(rendered_html) > 100000
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(255, 0, 0)\"></div></td>" in rendered_html
    assert "<td>red</td>" in rendered_html
    assert "<td>10</td>" in rendered_html
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(255, 255, 0)\"></div></td>" in rendered_html
    assert "<td>yellow</td>" in rendered_html
    assert "<td>20</td>" in rendered_html
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(0, 255, 0)\"></div></td>" in rendered_html
    assert "<td>green</td>" in rendered_html
    assert "<td>30</td>" in rendered_html
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(0, 0, 255)\"></div></td>" in rendered_html
    assert "<td>blue</td>" in rendered_html
    assert "<td>40</td>" in rendered_html


def test_image_and_palette_as_html__with_quantize():
    img, colors = quantize(IMAGE_PATH, PALETTE)

    rendered_html = image_and_palette_as_html(img, colors)

    assert rendered_html is not None
    assert len(rendered_html) > 100000
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(0, 255, 0)\"></div></td>" in rendered_html
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(0, 0, 255)\"></div></td>" in rendered_html
    assert "<td>green</td>" in rendered_html
    assert "<td>blue</td>" in rendered_html
