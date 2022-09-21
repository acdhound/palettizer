from telegram import Update
from telegram.ext import CallbackContext
from palettizer.palette import Palette


class Model:
    def __init__(self, context: CallbackContext):
        self.context = context

    def set_image(self, image: bytearray):
        pass

    def add_palette(self, palette: Palette):
        pass

    def set_num_colors(self, num: int):
        pass


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
