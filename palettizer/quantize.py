import faiss
import numpy as np
from sklearn.metrics import pairwise_distances_argmin
from typing import Union
import logging
from . imgutils import read_rgb_image, np_image_to_flat_array
from . palette import Palette, Color

DEFAULT_N_COLORS = 50
MAX_K_MEANS = 100
MAX_IMAGE_SIZE_PIXELS = 3500
MAX_IMAGE_SIZE_BYTES = 3 * (MAX_IMAGE_SIZE_PIXELS ** 2)  # assuming an uncompressed bitmap image of th max size
MAX_IMAGE_SIZE_MB = int(MAX_IMAGE_SIZE_BYTES / (1024 * 1024))


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
        d = codebook.shape[1]
        image = np.zeros(shape=(w, h, d), dtype=codebook.dtype)
        label_idx = 0
        color_pixels: dict[Color, int] = {}
        colors: list[Color] = palette.colors if palette is not None else [None] * len(codebook)
        for i in range(w):
            for j in range(h):
                label = labels[label_idx]
                image[i][j] = codebook[label]
                color = colors[label]
                if color is None:
                    color = Color(codebook[label][0], codebook[label][1], codebook[label][2])
                    colors[label] = color
                if color not in color_pixels:
                    color_pixels[color] = 1
                else:
                    color_pixels[color] += 1
                label_idx += 1
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
        raise InvalidImageException("The image is too large, please, provide an image not bigger than {}x{} pixels"
                                    .format(MAX_IMAGE_SIZE_PIXELS, MAX_IMAGE_SIZE_PIXELS))

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
        codebook_palette = codebook_palette_uint8.astype(dtype=np.float32) / 255
        pairwise_distances_argmin(codebook_palette, kmeans_palette, axis=0)
        kmeans_to_palette = pairwise_distances_argmin(codebook_palette, kmeans_palette, axis=0)
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
    labels_palette = pairwise_distances_argmin(codebook_palette, image_array, axis=0)

    return QuantizedImage.from_codebook_labels(codebook_palette_uint8, labels_palette,
                                               image.shape[0], image.shape[1],
                                               palette)
