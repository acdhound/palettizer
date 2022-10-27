import json
from pathlib import Path
import os
from typing import Union
from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Color:
    r: int
    g: int
    b: int
    name: str = "Color"
    vendor: str = "Unknown"

    # rgb is either a string like "ffffff" or a tuple like (255,255,255)
    @staticmethod
    def from_hex_rgb(rgb: Union[str, tuple, list], name: str, vendor: str):
        if isinstance(rgb, tuple) or isinstance(rgb, list):
            r, g, b = rgb
        else:
            r, g, b = Color.__parse_hex_rgb(rgb)
        return Color(r, g, b, name, vendor)

    @staticmethod
    def __parse_hex_rgb(hex_rgb: str):
        if len(hex_rgb) != 6:
            raise Exception("Expected hexadecimal RGB value as string, but given " + hex_rgb)
        r = int(hex_rgb[0:2], 16)
        g = int(hex_rgb[2:4], 16)
        b = int(hex_rgb[4:6], 16)
        return r, g, b


class Palette:
    # TODO get palette names from the resources instead of hardcoding
    PREDEFINED_PALETTES = ("mtnblack", "mtn94", "arton", "tikkurila")

    def __init__(self, colors: list[Color] = None, name="", url=""):
        self.colors = [] if colors is None else colors
        self.name = name
        self.url = url

    def size(self):
        return len(self.colors)

    @staticmethod
    def from_file(path: str):
        return Palette.from_files([path])

    @staticmethod
    def from_files(paths: Union[list, tuple]):
        colors = []
        palette_names = []
        palette_urls = []
        for file in paths:
            with open(file) as json_file:
                data = json.load(json_file)
                if 'name' in data:
                    palette_names.append(data['name'])
                if 'url' in data:
                    palette_urls.append(data['url'])
                arr = data['palette']
                for item in arr:
                    colors.append(Color.from_hex_rgb(item['color'], item['name'], item['vendor']))
        return Palette(colors, ' + '.join(palette_names), ', '.join(palette_urls))

    @staticmethod
    def from_predefined(palette_ids: Union[str, list, tuple]):
        if not palette_ids:
            return None
        if isinstance(palette_ids, str):
            palette_ids = [palette_ids]
        palette_paths = [Palette.__get_palette_path(x) for x in palette_ids]
        return Palette.from_files(palette_paths)

    @staticmethod
    def __get_palette_path(palette_id: str) -> str:
        if palette_id not in Palette.PREDEFINED_PALETTES:
            raise Exception(f"No palette found {palette_id}")
        return str(
            Path(os.path.realpath(__file__)).parent.absolute().joinpath(
                f"resources/{palette_id}-palette.json")
        )
