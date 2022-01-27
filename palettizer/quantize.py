import numpy as np
from sklearn.metrics import pairwise_distances_argmin
from sklearn.cluster import KMeans
from skimage import io
from skimage.util import img_as_ubyte


def read_rgb_image(path):
    img = io.imread(path)
    if len(img.shape) != 3 or img.shape[2] < 3 or img.shape[2] > 4:
        raise Exception(f"3 channel RGB image expected, but given an image of shape {img.shape}")
    if img.dtype != np.uint8:
        print("conversion from {} to {}, possible lose of data".format(img.dtype, np.uint8))
        img = img_as_ubyte(img)
    if img.shape[2] == 4:
        print("ignoring alpha channel of the image")
        img = img[:, :, :3]
    return img


def image_to_flat_array(img):
    w, h, d = tuple(img.shape)
    return np.reshape(img, (w * h, d))


def recreate_image(codebook, labels, w, h):
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
                palette_histogram[label] = 1
            else:
                palette_histogram[label] += 1
            label_idx += 1
    return image, palette_histogram


def quantize(img_path, palette, n_colors=0):
    codebook_palette = np.zeros((len(palette), 3), dtype=np.float64)
    codebook_palette_uint8 = np.zeros((len(palette), 3), dtype=np.uint8)
    i = 0
    for clr in palette:
        codebook_palette[i][0] = float(clr["color"][0]) / 255
        codebook_palette[i][1] = float(clr["color"][1]) / 255
        codebook_palette[i][2] = float(clr["color"][2]) / 255
        codebook_palette_uint8[i][0] = clr["color"][0]
        codebook_palette_uint8[i][1] = clr["color"][1]
        codebook_palette_uint8[i][2] = clr["color"][2]
        i = i + 1

    image = read_rgb_image(img_path)
    image_array = image_to_flat_array(np.array(image, dtype=np.float64) / 255)

    if n_colors > 0:
        print("Reducing color space of the image to " + str(n_colors) + " colors")
        kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(image_array)
        kmeans_palette = kmeans.cluster_centers_
        kmeans_labels = kmeans.predict(image_array)
        kmeans_image, hyst = recreate_image(kmeans_palette, kmeans_labels, image.shape[0], image.shape[1])
        # io.imsave("./kmeans.png", kmeans_image)
        image_array = image_to_flat_array(kmeans_image)
        image = kmeans_image

    print("Converting image colors to the palette")
    labels_palette = pairwise_distances_argmin(codebook_palette, image_array, axis=0)

    return recreate_image(codebook_palette_uint8, labels_palette, image.shape[0], image.shape[1])
