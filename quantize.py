import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin
from skimage import io


def read_rgb_image(path):
    img = io.imread(path)
    if len(img.shape) != 3 or img.shape[2] < 3 or img.shape[2] > 4:
        raise Exception(f"3 channel RGB image expected, but given an image of shape {img.shape}")
    print("ignoring alpha channel of the image")
    if img.shape[2] == 4:
        img = img[:, :, :3]
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


def quantize(img_path, palette):
    # todo remove this conversion and instead provide palette as a numpy array
    codebook_palette = np.zeros((len(palette), 3), dtype=np.float64)
    i = 0
    for clr in palette:
        codebook_palette[i][0] = float(clr[0]) / 255
        codebook_palette[i][1] = float(clr[1]) / 255
        codebook_palette[i][2] = float(clr[2]) / 255
        i = i + 1

    image = read_rgb_image(img_path)
    image_array = image_to_flat_array(np.array(image, dtype=np.float64) / 255)
    labels_palette = pairwise_distances_argmin(codebook_palette, image_array, axis=0)

    result = recreate_image(codebook_palette,
                            labels_palette,
                            image.shape[0],
                            image.shape[1])

    # todo convert image to uint8 array
    return result
