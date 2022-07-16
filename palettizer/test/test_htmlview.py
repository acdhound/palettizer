from palettizer.htmlview import image_and_palette_as_html
from palettizer.imgutils import read_rgb_image
from palettizer.quantize import quantize
from palettizer.palette import Palette, Color
from testutils import get_test_resource


RED = Color(255, 0, 0, name='red', vendor='ABC Paints')
YELLOW = Color(255, 255, 0, name='yellow', vendor='ABC Paints')
GREEN = Color(0, 255, 0, name='green', vendor='ABC Paints')
BLUE = Color(0, 0, 255, name='blue', vendor='ABC Paints')
PALETTE = Palette([RED, YELLOW, GREEN, BLUE])
IMAGE_PATH = str(get_test_resource("bliss.jpg"))


def test_image_and_palette_as_html():
    img = read_rgb_image(IMAGE_PATH)
    area = (img.shape[0] * img.shape[1]) // 4
    colors = {
        1: {'color': RED, "pixels": area},
        2: {'color': YELLOW, "pixels": area},
        3: {'color': GREEN, "pixels": area},
        4: {'color': BLUE, "pixels": area}
    }

    rendered_html = image_and_palette_as_html(img, colors)

    assert rendered_html is not None
    assert len(rendered_html) > 100000
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(255, 0, 0)\"></div></td>" in rendered_html
    assert "<div class=\"color-block\" style=\"background-color: rgb(255, 0, 0); width: 200.0px\">" in rendered_html
    assert "<td>red</td>" in rendered_html
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(255, 255, 0)\"></div></td>" in rendered_html
    assert "<div class=\"color-block\" style=\"background-color: rgb(255, 255, 0); width: 200.0px\">" in rendered_html
    assert "<td>yellow</td>" in rendered_html
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(0, 255, 0)\"></div></td>" in rendered_html
    assert "<div class=\"color-block\" style=\"background-color: rgb(0, 255, 0); width: 200.0px\">" in rendered_html
    assert "<td>green</td>" in rendered_html
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(0, 0, 255)\"></div></td>" in rendered_html
    assert "<div class=\"color-block\" style=\"background-color: rgb(0, 0, 255); width: 200.0px\">" in rendered_html
    assert "<td>blue</td>" in rendered_html
    assert "<td>25.0</td>" in rendered_html


def test_image_and_palette_as_html__with_quantize():
    img, colors = quantize(IMAGE_PATH, PALETTE)

    rendered_html = image_and_palette_as_html(img, colors)

    assert rendered_html is not None
    assert len(rendered_html) > 100000
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(0, 255, 0)\"></div></td>" in rendered_html
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(0, 0, 255)\"></div></td>" in rendered_html
    assert "<td>green</td>" in rendered_html
    assert "<td>blue</td>" in rendered_html
