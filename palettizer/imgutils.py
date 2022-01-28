import numpy as np
import imageio
from skimage import io
from skimage.util import img_as_ubyte
from typing import Union
from io import BytesIO


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
