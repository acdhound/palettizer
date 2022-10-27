import faiss
import numpy as np
from sklearn.metrics import pairwise_distances_argmin
from typing import Union
from . imgutils import read_rgb_image, np_image_to_flat_array
from . palette import Palette, Color

DEFAULT_N_COLORS = 50
MAX_K_MEANS = 100


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


def quantize(img: Union[str, bytes, bytearray], palette: Palette = None, n_colors=0) -> QuantizedImage:
    image = read_rgb_image(img)
    image_array = np_image_to_flat_array(np.array(image, dtype=np.float64) / 255)

    no_palette = palette is None or palette.size() == 0

    if no_palette or (0 < n_colors < palette.size()):
        if n_colors <= 0:
            n_colors = DEFAULT_N_COLORS
        n_colors = min(n_colors, MAX_K_MEANS)

        print("Reducing color space of the image to " + str(n_colors) + " colors")
        kmeans = faiss.Kmeans(d=image_array.shape[1], k=n_colors)
        image_array_32 = image_array.astype(np.float32)
        kmeans.train(image_array_32)
        kmeans_palette = kmeans.centroids
        kmeans_labels = kmeans.index.search(image_array_32, 1)[1]
        kmeans_labels = [i[0] for i in kmeans_labels]
        if no_palette:
            kmeans_palette = (kmeans_palette * 255.0).astype(np.uint8)
            return QuantizedImage.from_codebook_labels(kmeans_palette, kmeans_labels, image.shape[0], image.shape[1])

        kmeans_image = QuantizedImage.from_codebook_labels(kmeans_palette, kmeans_labels,
                                                           image.shape[0], image.shape[1]).image
        kmeans_image = kmeans_image.astype(np.float64)
        image_array = np_image_to_flat_array(kmeans_image)
        image = kmeans_image

    print("Converting image colors to the palette")
    codebook_palette = np.zeros((palette.size(), 3), dtype=np.float64)
    codebook_palette_uint8 = np.zeros((palette.size(), 3), dtype=np.uint8)
    i = 0
    for clr in palette.colors:
        np.put(codebook_palette[i], [0, 1, 2], [float(clr.r) / 255, float(clr.g) / 255, float(clr.b) / 255])
        np.put(codebook_palette_uint8[i], [0, 1, 2], [clr.r, clr.g, clr.b])
        i = i + 1
    labels_palette = pairwise_distances_argmin(codebook_palette, image_array, axis=0)

    return QuantizedImage.from_codebook_labels(codebook_palette_uint8, labels_palette,
                                               image.shape[0], image.shape[1],
                                               palette)
