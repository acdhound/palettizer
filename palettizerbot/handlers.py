from telegram import Update
from telegram.ext import CallbackContext
import logging
from palettizer.quantize import quantize


logger = logging.getLogger(__name__)


def handle_message_with_image(update: Update, context: CallbackContext):
    if not update.message:
        raise Exception("Can't get a message from an Update")
    if not update.message.document and not update.message.photo:
        raise Exception("Message contains no photo or file")

    if update.message.document:
        mime_type = update.message.document.mime_type
        if not mime_type or (not mime_type.startswith("image")):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="File is not an image")
            return
        file = update.message.document.get_file()
    else:
        photos = update.message.photo
        if len(photos) == 0:
            raise Exception("Message contains an empty PhotoSize array")
        file = photos[-1].get_file()

    if not file.file_size:
        raise Exception("Can't define file size")
    if file.file_size > 5 * 1024 * 1024:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="File must be less than 5 MB")
        return
    try:
        image_as_bytearray = file.download_as_bytearray()
        palette = [
            {'color': (255, 0, 0), 'name': 'Red'},
            {'color': (0, 255, 0), 'name': 'Green'},
            {'color': (0, 0, 255), 'name': 'Blue'}
        ]
        out_image, hist = quantize(image_as_bytearray, palette, n_colors=0)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=str(hist))
    except Exception as e:
        raise IOError("Failed to read image from the message", e)
