import numpy as np


def quantize(img, palette):
    if img.mode not in ('RGB', 'RGBA'):
        raise Exception(f"Can't work with {img.mode}, RGB or RGBA expected")

    for x in range(0, img.size[0]):
        for y in range(0, img.size[1]):
            color = img.getpixel((x, y))
            palette_color = find_closest(color, palette)
            img.putpixel((x, y), palette_color)
            # very slow algorythm, don't use with images larger than 500x500 px
            # apply_dithering(img, x, y, color, palette_color)


def apply_dithering(img, x, y, color, palette_color):
    width = img.size[0]
    height = img.size[1]
    err = color2nparr(color) - color2nparr(palette_color)
    if x + 1 < width:
        c1 = color2nparr(img.getpixel((x + 1, y)))
        img.putpixel((x + 1, y), nparr2color(c1 + (err * (7 / 16))))
    if y + 1 < height:
        c2 = color2nparr(img.getpixel((x, y + 1)))
        img.putpixel((x, y + 1), nparr2color(c2 + (err * (3 / 16))))
    if y + 1 < height:
        c3 = color2nparr(img.getpixel((x, y + 1)))
        img.putpixel((x, y + 1), nparr2color(c3 + (err * (5 / 16))))
    if x + 1 < width and y + 1 < height:
        c4 = color2nparr(img.getpixel((x + 1, y + 1)))
        img.putpixel((x + 1, y + 1), nparr2color(c4 + (err * (1 / 16))))


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


def nparr2color(arr):
    if arr.shape[0] < 3:
        raise Exception("Can't convert an array " + arr.shape + " to a color")
    r = num2rgbchannel(arr[0])
    g = num2rgbchannel(arr[1])
    b = num2rgbchannel(arr[2])
    return r, g, b


def color2nparr(clr):
    if len(clr) < 3:
        raise Exception("Can't convert color " + clr + ", expected at least 3 channels")
    return np.array([clr[0], clr[1], clr[2]])


def num2rgbchannel(num):
    int_num = int(num)
    if int_num < 0:
        int_num = 0
    elif int_num > 255:
        int_num = 255
    return int_num
