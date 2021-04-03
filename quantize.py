
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
