import faiss
import numpy as np
from sklearn.metrics import pairwise_distances_argmin
import cv2
from typing import Union
import logging
from . imgutils import read_rgb_image, np_image_to_flat_array, rgb_flat_array_to_lab, delta_e_2000
from . palette import Palette, Color

DEFAULT_N_COLORS = 50
MAX_K_MEANS = 150
MAX_IMAGE_SIZE_PIXELS = 2000
MAX_IMAGE_SIZE_MB = 30
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
DELTA_E_METRIC = "delta_e"
EUCLIDEAN_METRIC = "euclidean"


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


def quantize(img: Union[str, bytes, bytearray],
             palette: Palette = None,
             n_colors=0,
             metric=EUCLIDEAN_METRIC) -> QuantizedImage:

    if (isinstance(img, bytes) or isinstance(img, bytearray)) and len(img) > MAX_IMAGE_SIZE_BYTES:
        raise InvalidImageException("The file is too large, please, provide a file not bigger than {} MB"
                                    .format(MAX_IMAGE_SIZE_MB))

    image = __resize_image_if_too_large(read_rgb_image(img))

    # Case 1: palette not set
    if palette is None or palette.size() == 0:
        return quantize_to_n_colors(image, n_colors)

    # Case 2: colors count is limited
    if n_colors > 0:
        return quantize_to_n_colors_with_palette(image, palette, metric, n_colors)

    # Case 3: colors count is not limited
    if metric == DELTA_E_METRIC:
        # unlimited colors with delta E would take too long time
        logging.info("Can't convert an image using Delta E metric with unlimited colors" +
                     ", taking {} as max colors count", MAX_K_MEANS)
        return quantize_to_n_colors_with_palette(image, palette, metric, MAX_K_MEANS)

    return quantize_with_palette(image, palette, metric)


def quantize_to_n_colors(image: np.ndarray, n_colors: int):
    n_colors = DEFAULT_N_COLORS if n_colors <= 0 else n_colors
    n_colors = min(n_colors, MAX_K_MEANS)

    logging.info("Quantizing image to {} colors", n_colors)

    image_array = np_image_to_flat_array(np.array(image, dtype=np.float64) / 255)
    kmeans_labels, kmeans_palette = __apply_kmeans_to_flat_array(image_array, n_colors)

    return QuantizedImage.from_codebook_labels((kmeans_palette * 255.0).astype(np.uint8),
                                               kmeans_labels,
                                               image.shape[0], image.shape[1])


def quantize_to_n_colors_with_palette(image: np.ndarray,
                                      palette: Palette,
                                      metric: str,
                                      n_colors: int):
    n_colors = min(n_colors, MAX_K_MEANS)

    logging.info("Converting image colors palette {} using up to {} colors and metric {}",
                 palette.name, n_colors, metric)

    # first, perform K-means in order to reduce color space to N colors
    # then the palette will be matched with the vector of K-means colors instead of the whole image
    image_array = np_image_to_flat_array(np.array(image, dtype=np.float64) / 255)
    kmeans_labels, kmeans_palette = __apply_kmeans_to_flat_array(image_array, n_colors)

    logging.info("Converting " + str(n_colors) + " image colors to the palette")
    codebook_palette_uint8 = palette.to_codebook_palette_unit8()
    codebook_palette_float32 = codebook_palette_uint8.astype(dtype=np.float32) / 255

    # find the closest color from the original palette for each from the K-means palette
    # if j = closest_codebook_for_kmeans[i] then codebook_palette_uint8[j] is the closest to kmeans_palette[i]
    if metric == DELTA_E_METRIC:
        closest_codebook_for_kmeans = pairwise_distances_argmin(rgb_flat_array_to_lab(kmeans_palette),
                                                                rgb_flat_array_to_lab(codebook_palette_float32),
                                                                metric=delta_e_2000)
    else:
        closest_codebook_for_kmeans = pairwise_distances_argmin(kmeans_palette,
                                                                codebook_palette_float32,
                                                                metric=metric)

    # the K-means palette colors are mapped to the closest colors from the original palette
    # n_colors_codebook_palette_uint8 and colors might contain duplicates!
    n_colors_codebook_palette_uint8 = np.zeros(shape=kmeans_palette.shape, dtype=np.uint8)
    colors = []
    for i in range(0, kmeans_palette.shape[0]):
        n_colors_codebook_palette_uint8[i] = codebook_palette_uint8[closest_codebook_for_kmeans[i]]
        colors.append(palette.colors[closest_codebook_for_kmeans[i]])

    # ordering of the mapped colors is the same as in K-means palette, so kmeans_labels can be used as indexes
    return QuantizedImage.from_codebook_labels(n_colors_codebook_palette_uint8, kmeans_labels,
                                               image.shape[0], image.shape[1],
                                               Palette(colors=colors, name=palette.name, url=palette.url))


def quantize_with_palette(image: np.ndarray,
                          palette: Palette,
                          metric: str):
    logging.info("Converting image colors palette {} using metric {}", palette.name, metric)

    image_array = np_image_to_flat_array(np.array(image, dtype=np.float64) / 255)

    codebook_palette_uint8 = palette.to_codebook_palette_unit8()
    codebook_palette_float32 = codebook_palette_uint8.astype(dtype=np.float32) / 255
    # delta E metric is not supported here because it would be too slow
    labels_palette = pairwise_distances_argmin(image_array, codebook_palette_float32, metric=metric)

    return QuantizedImage.from_codebook_labels(codebook_palette_uint8, labels_palette,
                                               image.shape[0], image.shape[1],
                                               palette)


def __resize_image_if_too_large(image: np.ndarray):
    if image.shape[0] > MAX_IMAGE_SIZE_PIXELS or image.shape[1] > MAX_IMAGE_SIZE_PIXELS:
        logging.info("The image is too big: {}x{}".format(image.shape[0], image.shape[1]))
        k = MAX_IMAGE_SIZE_PIXELS / max(image.shape[0], image.shape[1])
        new_size = (int(image.shape[1] * k), int(image.shape[0] * k))
        logging.info("Resizing the image to {}x{}".format(new_size[0], new_size[1]))
        return cv2.resize(image, dsize=new_size, interpolation=cv2.INTER_CUBIC)
    return image


def __apply_kmeans_to_flat_array(image_array: np.ndarray, n_colors: int):
    logging.info("Running K-Means: reducing color space of the image to " + str(n_colors) + " colors")
    kmeans = faiss.Kmeans(d=image_array.shape[1], k=n_colors)
    image_array_32 = image_array.astype(np.float32)
    kmeans.train(image_array_32)
    kmeans_palette = kmeans.centroids
    kmeans_labels = kmeans.index.search(image_array_32, 1)[1]
    kmeans_labels = kmeans_labels[:, 0]
    return kmeans_labels, kmeans_palette
