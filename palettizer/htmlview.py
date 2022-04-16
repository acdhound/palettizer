import base64
import numpy as np
from io import BytesIO
import imageio


def np_image_to_base64(img: np.ndarray):
    with BytesIO() as buf:
        imageio.imwrite(buf, img, format='png')
        image_bin = buf.getvalue()
        image_b64 = base64.b64encode(image_bin).decode("utf-8")
        return image_b64
