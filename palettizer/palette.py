import json


def parse_palette(file):
    palette = []
    with open(file) as json_file:
        data = json.load(json_file)
        arr = data['palette']
        for item in arr:
            color = parse_hexrgb(item['color'])
            palette.append({"color": color, "name": item["name"]})
    return palette


# accepts a string representing a hexadecimal RGB value like "ffffff"
def parse_hexrgb(hexrgb):
    if len(hexrgb) != 6:
        raise Exception("Expected hexadecimal RGB value as string, but given " + hexrgb)
    r = int(hexrgb[0:2], 16)
    g = int(hexrgb[2:4], 16)
    b = int(hexrgb[4:6], 16)
    return r, g, b
