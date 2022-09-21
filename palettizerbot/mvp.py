from telegram import Update
from telegram.ext import CallbackContext
from palettizer.palette import Palette
from typing import Union


class Model:
    def __init__(self, context: CallbackContext):
        self.context = context

    def set_picture(self, picture: Union[bytes, bytearray]):
        self.context.user_data["picture"] = picture

    def get_picture(self):
        if "picture" not in self.context.user_data:
            return None
        picture = self.context.user_data["picture"]
        if not isinstance(picture, bytes) and not isinstance(picture, bytearray):
            raise Exception("Can't get the picture from the context")
        return picture

    def add_palette(self, palette_id: str, palette: Palette):
        if palette is None:
            raise Exception("Palette can't be None")
        if palette_id is None:
            raise Exception("ID can't be None")
        palettes = self.context.user_data["palettes"]
        if not palettes:
            palettes = {palette_id: palette}
            self.context.user_data["palettes"] = palettes
        elif isinstance(palettes, dict):
            palettes[palette_id] = palette
            self.context.user_data["palettes"] = palettes
        else:
            raise Exception("Context object with key 'palettes' has a wrong type:"
                            " expected dict, actual " + type(palettes))

    def get_palettes(self) -> dict:
        if "palettes" not in self.context.user_data:
            return {}
        palettes = self.context.user_data["palettes"]
        if not isinstance(palettes, dict):
            raise Exception("Can't get the palettes from the context")
        return palettes

    def set_num_colors(self, n_colors: int):
        if n_colors <= 0:
            n_colors = 0
        self.context.user_data["n_colors"] = n_colors

    def get_num_colors(self):
        n_colors = self.context.user_data["n_colors"]
        if n_colors is not None and isinstance(n_colors, int):
            return n_colors
        else:
            return 0


class Presenter:
    def start(self, update: Update):
        pass

    def read_picture(self, update: Update, model: Model):
        pass

    def add_palette(self, palette_id: str, update: Update, model: Model):
        pass

    def request_num_colors(self, update: Update):
        pass

    def read_num_colors(self, n_colors: int, model: Model):
        pass

    def start_processing(self, model: Model):
        pass


class View:
    def show_start_message(self, update: Update, context: CallbackContext):
        pass

    def show_palettes(self, palettes: list[Palette], selected: list[int],
                      update: Update, context: CallbackContext):
        pass

    def show_num_colors_inout(self, update: Update, context: CallbackContext):
        pass

    def show_start_processing_button(self, update: Update, context: CallbackContext):
        pass

    def show_result(self, update: Update, context: CallbackContext):
        pass
