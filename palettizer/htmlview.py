from jinja2 import Environment, FunctionLoader, select_autoescape
import numpy as np
from . imgutils import np_image_to_base64
from importlib import resources


def image_and_palette_as_html(image: np.ndarray, palette_hist: dict):
    colors_sorted = sorted(palette_hist.values(), key=lambda i: i['pixels'], reverse=True)
    colors_percentage = map(lambda i: __pixels_to_percentage(i, image), colors_sorted)
    img_base64 = np_image_to_base64(image, "jpg")
    return __render_template("template.html", {
        "image": {"format": "jpg", "base64": img_base64},
        "colors": colors_percentage})


def __load_template(name: str) -> str:
    try:
        return resources.read_text("palettizer.templates", name)
    except Exception as e:
        raise Exception(f"Failed to load template: ${name}") from e


__ENV = Environment(loader=FunctionLoader(__load_template), autoescape=select_autoescape())


def __render_template(template: str, variables: dict):
    template = __ENV.get_template(template)
    return template.render(variables)


def __pixels_to_percentage(color: dict, img: np.ndarray) -> dict:
    percentage = (color['pixels'] * 100.00) / (img.shape[0] * img.shape[1])
    return {'color': color['color'], 'percentage': percentage}
