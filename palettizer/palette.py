import json
from pathlib import Path
import os


def get_predefined_palette(*palette_ids) -> list:
    palette_paths = [__get_palette_path(x) for x in palette_ids]
    return parse_palette(','.join(palette_paths))


def __get_palette_path(palette_id: str) -> str:
    return str(
        Path(os.path.realpath(__file__)).parent.absolute().joinpath(
            f"resources/{palette_id}-palette.json")
    )


def parse_palette(palette_paths) -> list:
    palette = []
    for file in palette_paths.split(","):
        with open(file) as json_file:
            data = json.load(json_file)
            arr = data['palette']
            for item in arr:
                color = __parse_hexrgb(item['color'])
                palette.append({"color": color, "name": item["name"], "vendor": item["vendor"]})
    return palette


# accepts a string representing a hexadecimal RGB value like "ffffff"
def __parse_hexrgb(hexrgb):
    if len(hexrgb) != 6:
        raise Exception("Expected hexadecimal RGB value as string, but given " + hexrgb)
    r = int(hexrgb[0:2], 16)
    g = int(hexrgb[2:4], 16)
    b = int(hexrgb[4:6], 16)
    return r, g, b
