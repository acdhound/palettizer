import numpy as np
import imageio.v2 as imageio
from skimage import io
from skimage.util import img_as_ubyte
from typing import Union
from io import BytesIO
import base64
from skimage.color import rgb2hsv
import cv2
from colour import delta_E


def read_rgb_image(path: Union[str, bytes, bytearray]) -> np.ndarray:
    if isinstance(path, str):
        img = io.imread(path)
    elif isinstance(path, bytes):
        img = imageio.imread(path)
    elif isinstance(path, bytearray):
        img = imageio.imread(bytes(path))
    else:
        raise Exception(f"Cannot read image, expected a path or bytes array, but got {type(path)}")
    if len(img.shape) != 3 or img.shape[2] < 3 or img.shape[2] > 4:
        raise Exception(f"3 channel RGB image expected, but given an image of shape {img.shape}")
    if img.dtype != np.uint8:
        print("conversion from {} to {}, possible lose of data".format(img.dtype, np.uint8))
        img = img_as_ubyte(img)
    if img.shape[2] == 4:
        print("ignoring alpha channel of the image")
        img = img[:, :, :3]
    return img


def image_to_bytes(img: np.ndarray, file_format='png') -> bytes:
    with BytesIO() as buf:
        imageio.imwrite(buf, img, format=file_format)
        image_bin = buf.getvalue()
    return image_bin


def np_image_to_base64(img: np.ndarray, img_format: str):
    with BytesIO() as buf:
        imageio.imwrite(buf, img, format=img_format)
        image_bin = buf.getvalue()
        image_b64 = base64.b64encode(image_bin).decode("utf-8")
        return image_b64


def np_image_to_flat_array(img: np.ndarray):
    w, h, d = tuple(img.shape)
    return np.reshape(img, (w * h, d))


def to_hsv(r: int, g: int, b: int) -> np.ndarray:
    return rgb2hsv(np.array([[[r, g, b]]], dtype=np.uint8))[0][0]


def rgb_flat_array_to_lab(arr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(np.array([arr]), cv2.COLOR_RGB2Lab)[0]


def delta_e_2000(u, v):
    return delta_E(u, v, 'CIE 2000')
