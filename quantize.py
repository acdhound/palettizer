import skimage.color as skcolor
from skimage import io
import numpy as np


def quantize_cie76(img_path, palette):
    img = io.imread(img_path)
    if len(img.shape) < 3 or img.shape[2] != 3:
        raise Exception("3 channel image expected, but given an image of shape " + img.shape)
    img_lab = skcolor.rgb2lab(img)

    palette_lab = [skcolor.rgb2lab(np.array(c, dtype=np.uint8)) for c in palette]

    img_lab_quant = np.zeros(img_lab.shape, dtype=img_lab.dtype)
    for x in range(0, img_lab.shape[0]):
        for y in range(0, img_lab.shape[1]):
            c0 = img_lab[x][y]
            min_distance = 0.00
            closest_clr = None
            first = True
            for c1 in palette_lab:
                d = c1 - c0
                distance = d[0] * d[0] + d[1] * d[1] + d[2] * d[2]
                if first or distance < min_distance:
                    min_distance = distance
                    closest_clr = c1
                    first = False
            img_lab_quant[x][y] = closest_clr

    return skcolor.lab2rgb(img_lab_quant)



def quantize(img, palette):
    if img.mode not in ('RGB', 'RGBA'):
        raise Exception(f"Can't work with {img.mode}, RGB or RGBA expected")

    for x in range(0, img.size[0]):
        for y in range(0, img.size[1]):
            color = img.getpixel((x, y))
            palette_color = find_closest(color, palette)
            img.putpixel((x, y), palette_color)


def find_closest(color, palette):
    first = True
    min_diff = 0
    closest_color = None
    for p in palette:
        dr = p[0] - color[0]
        dg = p[1] - color[1]
        db = p[2] - color[2]
        diff = dr * dr + dg * dg + db * db
        if first:
            min_diff = diff
            closest_color = p
            first = False
        elif diff < min_diff:
            min_diff = diff
            closest_color = p
    return closest_color
