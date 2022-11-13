from jinja2 import Environment, FunctionLoader, select_autoescape
import numpy as np
from . imgutils import np_image_to_base64, to_hsv
from . palette import Color
from . quantize import QuantizedImage
from importlib import resources


def image_and_palette_as_html(q_image: QuantizedImage):
    colors_sorted = sorted(q_image.color_pixels.items(), key=lambda i: __get_hue(i[0]), reverse=True)
    colors_percentage = list(map(lambda i: __pixels_to_percentage(i, q_image.image), colors_sorted))
    max_percentage = max(map(lambda i: i['percentage'], colors_percentage))
    img_base64 = np_image_to_base64(q_image.image, "jpg")
    return __render_template("template.html", {
        "image": {"format": "jpg", "base64": img_base64},
        "colors": colors_percentage,
        "max_percentage": max_percentage})


def __load_template(name: str) -> str:
    try:
        return resources.read_text("palettizer.templates", name)
    except Exception as e:
        raise Exception(f"Failed to load template: ${name}") from e


__ENV = Environment(loader=FunctionLoader(__load_template), autoescape=select_autoescape())


def __render_template(template: str, variables: dict):
    template = __ENV.get_template(template)
    return template.render(variables)


def __pixels_to_percentage(color_pixel: tuple[Color, int], img: np.ndarray) -> dict:
    percentage = (color_pixel[1] * 100.00) / (img.shape[0] * img.shape[1])
    return {'color': color_pixel[0], 'percentage': percentage}


def __get_hue(c: Color):
    return to_hsv(c.r, c.g, c.b)[0]
