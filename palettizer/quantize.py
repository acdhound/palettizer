import faiss
import numpy as np
from sklearn.metrics import pairwise_distances_argmin
import cv2
from colour import delta_E
from typing import Union
import logging
from . imgutils import read_rgb_image, np_image_to_flat_array
from . palette import Palette, Color

DEFAULT_N_COLORS = 50
MAX_K_MEANS = 100
MAX_IMAGE_SIZE_PIXELS = 2000
MAX_IMAGE_SIZE_MB = 30
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024


class QuantizedImage:
    image: np.ndarray
    color_pixels: dict[Color, int]

    def __init__(self, image: np.ndarray, color_pixels: dict[Color, int]):
        self.image = image
        self.color_pixels = color_pixels

    @staticmethod
    def from_codebook_labels(codebook: np.ndarray, labels: Union[np.ndarray, list],
                             w: int, h: int,
                             palette: Palette = None):
        """Recreate the (compressed) image from the code book & labels"""

        color_pixels: dict[Color, int] = {}
        colors: list[Color] = palette.colors if palette is not None else [None] * len(codebook)

        flat_image = np.ndarray(shape=(labels.shape[0], codebook.shape[1]), dtype=codebook.dtype)
        for i in range(0, labels.shape[0]):
            flat_image[i] = codebook[labels[i]]
            color = colors[labels[i]]
            if color is None:
                color = Color(codebook[labels[i]][0], codebook[labels[i]][1], codebook[labels[i]][2])
                colors[labels[i]] = color
            if color not in color_pixels:
                color_pixels[color] = 1
            else:
                color_pixels[color] += 1

        image = flat_image.reshape((w, h, codebook.shape[1]))

        return QuantizedImage(image, color_pixels)


class InvalidImageException(Exception):
    pass


def quantize(img: Union[str, bytes, bytearray], palette: Palette = None, n_colors=0) -> QuantizedImage:
    if ((isinstance(img, bytes) or isinstance(img, bytearray))
            and len(img) > MAX_IMAGE_SIZE_BYTES):
        raise InvalidImageException("The file is too large, please, provide a file not bigger than {} MB"
                                    .format(MAX_IMAGE_SIZE_MB))

    image = read_rgb_image(img)

    if (image.shape[0] > MAX_IMAGE_SIZE_PIXELS
            or image.shape[1] > MAX_IMAGE_SIZE_PIXELS):
        logging.info("The image is too big: {}x{}".format(image.shape[0], image.shape[1]))
        k = MAX_IMAGE_SIZE_PIXELS / max(image.shape[0], image.shape[1])
        new_size = (int(image.shape[1] * k), int(image.shape[0] * k))
        logging.info("Resizing the image to {}x{}".format(new_size[0], new_size[1]))
        image = cv2.resize(image, dsize=new_size, interpolation=cv2.INTER_CUBIC)

    image_array = np_image_to_flat_array(np.array(image, dtype=np.float64) / 255)

    no_palette = palette is None or palette.size() == 0

    if no_palette or (0 < n_colors < palette.size()):
        if n_colors <= 0:
            n_colors = DEFAULT_N_COLORS
        n_colors = min(n_colors, MAX_K_MEANS)

        logging.info("Reducing color space of the image to " + str(n_colors) + " colors")
        kmeans = faiss.Kmeans(d=image_array.shape[1], k=n_colors)
        image_array_32 = image_array.astype(np.float32)
        kmeans.train(image_array_32)
        kmeans_palette = kmeans.centroids
        kmeans_labels = kmeans.index.search(image_array_32, 1)[1]
        kmeans_labels = kmeans_labels[:, 0]
        if no_palette:
            kmeans_palette = (kmeans_palette * 255.0).astype(np.uint8)
            return QuantizedImage.from_codebook_labels(kmeans_palette, kmeans_labels, image.shape[0], image.shape[1])

        logging.info("Converting image colors to the palette")
        codebook_palette_uint8 = palette.to_codebook_palette_unit8()
        codebook_palette_float32 = codebook_palette_uint8.astype(dtype=np.float32) / 255
        codebook_palette_lab = cv2.cvtColor(np.array([codebook_palette_float32]), cv2.COLOR_RGB2Lab)[0]
        kmeans_palette_lab = cv2.cvtColor(np.array([kmeans_palette]), cv2.COLOR_RGB2Lab)[0]
        kmeans_to_palette = pairwise_distances_argmin(kmeans_palette_lab, codebook_palette_lab, metric=delta_e_distance)
        reduced_codebook_palette_uint8 = np.zeros(shape=kmeans_palette.shape, dtype=np.uint8)
        reduced_colors = []
        for i in range(0, kmeans_palette.shape[0]):
            reduced_codebook_palette_uint8[i] = codebook_palette_uint8[kmeans_to_palette[i]]
            reduced_colors.append(palette.colors[kmeans_to_palette[i]])
        return QuantizedImage.from_codebook_labels(reduced_codebook_palette_uint8, kmeans_labels,
                                                   image.shape[0], image.shape[1],
                                                   Palette(colors=reduced_colors, name=palette.name, url=palette.url))

    logging.info("Converting image colors to the palette")
    codebook_palette_uint8 = palette.to_codebook_palette_unit8()
    codebook_palette = codebook_palette_uint8.astype(dtype=np.float32) / 255
    labels_palette = pairwise_distances_argmin(image_array, codebook_palette)

    return QuantizedImage.from_codebook_labels(codebook_palette_uint8, labels_palette,
                                               image.shape[0], image.shape[1],
                                               palette)


def delta_e_distance(u, v):
    return delta_E(u, v, 'CIE 2000')
