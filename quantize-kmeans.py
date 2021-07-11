import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin
from skimage import io


def read_rgb_image(path):
    img = io.imread(path)
    if len(img.shape) < 3 or img.shape[2] < 3:
        raise Exception(f"At least 3 channel image expected, but given an image of shape {img.shape}")
    return img


def fit_to_kmeans(img, n_colors):
    img_array = image_to_flat_array(img)
    return KMeans(n_clusters=n_colors, random_state=0).fit(img_array)


def image_to_flat_array(img):
    w, h, d = tuple(img.shape)
    return np.reshape(img, (w * h, d))


def recreate_image(codebook, labels, w, h):
    """Recreate the (compressed) image from the code book & labels"""
    d = codebook.shape[1]
    image = np.zeros((w, h, d))
    label_idx = 0
    for i in range(w):
        for j in range(h):
            image[i][j] = codebook[labels[label_idx]]
            label_idx += 1
    return image


def quantize(img_path):
    n_colors = 4

    palette = read_rgb_image("palette.jpg")
    palette = np.array(palette, dtype=np.float64) / 255
    palette_kmeans = fit_to_kmeans(palette, n_colors)
    codebook_palette = palette_kmeans.cluster_centers_

    image = read_rgb_image(img_path)
    image_array = image_to_flat_array(np.array(image, dtype=np.float64) / 255)
    labels_palette = pairwise_distances_argmin(codebook_palette, image_array, axis=0)

    result = recreate_image(codebook_palette,
                            labels_palette,
                            image.shape[0],
                            image.shape[1])

    # show image for testing
    # plt.figure(0)
    # plt.clf()
    # plt.axis('off')
    # plt.title('Quantized image (12 colors, Palette)')
    # plt.imshow(result)
    # plt.show()

    return result


print(quantize("testimage2.png"))