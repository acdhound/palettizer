import base64
import numpy as np
from io import BytesIO
import imageio
from jinja2 import Environment, PackageLoader, select_autoescape
from palettizer.imgutils import read_rgb_image


def render_html(variables):
    env = Environment(
        loader=PackageLoader("palettizer"),
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

colors = {
    1: {'color': {'color': (255, 0, 0), 'name': 'red', 'vendor': 'ABC Paints'}, "pixels": 100},
    2: {'color': {'color': (255, 255, 0), 'name': 'yellow', 'vendor': 'ABC Paints'}, "pixels": 60},
    3: {'color': {'color': (0, 255, 0), 'name': 'green', 'vendor': 'ABC Paints'}, "pixels": 300},
    4: {'color': {'color': (0, 0, 255), 'name': 'blue', 'vendor': 'ABC Paints'}, "pixels": 10}
     }

rendered_html = render_html({"img_base64": img_base64,
                             "colors": colors})

with open("./output.html", mode="w") as output:
    output.write(rendered_html)

exit(0)
