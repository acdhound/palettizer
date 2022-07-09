import faiss
import numpy as np
from sklearn.metrics import pairwise_distances_argmin
from sklearn.cluster import KMeans
from typing import Union
from . imgutils import read_rgb_image
from . palette import Palette


def image_to_flat_array(img):
    w, h, d = tuple(img.shape)
    return np.reshape(img, (w * h, d))


def recreate_image(codebook, labels, w, h, palette: Palette = None) -> (np.ndarray, dict):
    """Recreate the (compressed) image from the code book & labels"""
    d = codebook.shape[1]
    image = np.zeros(shape=(w, h, d), dtype=codebook.dtype)
    label_idx = 0
    palette_histogram = {}
    for i in range(w):
        for j in range(h):
            label = labels[label_idx]
            image[i][j] = codebook[label]
            if label not in palette_histogram:
                if palette is None:
                    palette_histogram[label] = {'color': codebook[label], 'pixels': 1}
                else:
                    palette_histogram[label] = {'color': palette.colors[label], 'pixels': 1}
            else:
                palette_histogram[label]['pixels'] += 1
            label_idx += 1
    return image, palette_histogram


def quantize(img: Union[str, bytes, bytearray], palette: Palette, n_colors=0) -> (np.ndarray, dict):
    codebook_palette = np.zeros((palette.size(), 3), dtype=np.float64)
    codebook_palette_uint8 = np.zeros((palette.size(), 3), dtype=np.uint8)
    i = 0
    for clr in palette.colors:
        np.put(codebook_palette[i], [0, 1, 2], [float(clr.r) / 255, float(clr.g) / 255, float(clr.b) / 255])
        np.put(codebook_palette_uint8[i], [0, 1, 2], [clr.r, clr.g, clr.b])
        i = i + 1

    image = read_rgb_image(img)
    image_array = image_to_flat_array(np.array(image, dtype=np.float64) / 255)

    if 0 < n_colors < palette.size():
        print("Reducing color space of the image to " + str(n_colors) + " colors")
        # kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(image_array)
        # kmeans_palette = kmeans.cluster_centers_
        # kmeans_labels = kmeans.predict(image_array)
        # kmeans_image, hist = recreate_image(kmeans_palette, kmeans_labels, image.shape[0], image.shape[1])
        # image_array = image_to_flat_array(kmeans_image)
        # image = kmeans_image

        kmeans = faiss.Kmeans(d=image_array.shape[1], k=n_colors)
        image_array_32 = image_array.astype(np.float32)
        kmeans.train(image_array_32)
        kmeans_palette = kmeans.centroids
        kmeans_labels = kmeans.index.search(image_array_32, 1)[1]
        kmeans_labels = [i[0] for i in kmeans_labels]
        kmeans_image, hist = recreate_image(kmeans_palette, kmeans_labels, image.shape[0], image.shape[1])
        kmeans_image = kmeans_image.astype(np.float64)
        image_array = image_to_flat_array(kmeans_image)
        image = kmeans_image

    print("Converting image colors to the palette")
    labels_palette = pairwise_distances_argmin(codebook_palette, image_array, axis=0)

    return recreate_image(codebook_palette_uint8, labels_palette, image.shape[0], image.shape[1], palette)
