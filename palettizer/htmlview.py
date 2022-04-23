from jinja2 import Environment, PackageLoader, select_autoescape
import numpy as np
from . imgutils import np_image_to_base64


__ENV = Environment(loader=PackageLoader("palettizer"), autoescape=select_autoescape())


def image_and_palette_as_html(image: np.ndarray, palette_hist: dict):
    img_base64 = np_image_to_base64(image, "jpg")
    return __render_template("template.html", {
        "image": {"format": "jpg", "base64": img_base64},
        "colors": palette_hist})


def __render_template(template: str, variables: dict):
    template = __ENV.get_template(template)
    return template.render(variables)
