from palettizer.htmlview import image_and_palette_as_html
from palettizer.imgutils import read_rgb_image
from testutils import get_test_resource


def test_image_and_palette_as_html():
    img = read_rgb_image(str(get_test_resource("bliss.jpg")))
    colors = {
        1: {'color': {'color': (255, 0, 0), 'name': 'red', 'vendor': 'ABC Paints'}, "pixels": 10},
        2: {'color': {'color': (255, 255, 0), 'name': 'yellow', 'vendor': 'ABC Paints'}, "pixels": 60},
        3: {'color': {'color': (0, 255, 0), 'name': 'green', 'vendor': 'ABC Paints'}, "pixels": 300},
        4: {'color': {'color': (0, 0, 255), 'name': 'blue', 'vendor': 'ABC Paints'}, "pixels": 100}
    }

    rendered_html = image_and_palette_as_html(img, colors)

    assert rendered_html is not None
    assert "BDAQkJCQwLDBgNDRgyIRwhM" in rendered_html
    assert "<td><div class=\"color-block\" style=\"background-color: rgb(0, 255, 0)\"></div></td>" in rendered_html
    assert "<td>blue</td>" in rendered_html
    assert "<td>10</td>" in rendered_html
