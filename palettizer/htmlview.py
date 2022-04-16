import base64
import numpy as np
from io import BytesIO
import imageio
from jinja2 import Environment, PackageLoader, select_autoescape
from palettizer.imgutils import read_rgb_image


def render_html(variables):
    env = Environment(
        loader=PackageLoader("htmlview"), #this causes recursion while loading module 'htmlview', need to fix this
        autoescape=select_autoescape()
    )
    template = env.get_template("template.html")
    return template.render(variables)


def np_image_to_base64(img: np.ndarray):
    print("1")
    with BytesIO() as buf:
        imageio.imwrite(buf, img, format='png')
        image_bin = buf.getvalue()
        image_b64 = base64.b64encode(image_bin).decode("utf-8")
        return image_b64


img = read_rgb_image("C:\\Users\\adiva\\PycharmProjects\\palettizer\\palettizer\\resources\\bliss.jpg")
img_base64 = np_image_to_base64(img)
rendered_html = render_html({"img_base64": img_base64})
print(rendered_html)
