from telegram import Update
from telegram.ext import CallbackContext
import logging
from palettizer.quantize import quantize
from palettizer.imgutils import image_to_bytes


logger = logging.getLogger(__name__)


HARDCODED_PALETTE = [
    {'color': (255, 0, 0), 'name': 'Red'},
    {'color': (0, 255, 0), 'name': 'Green'},
    {'color': (0, 0, 255), 'name': 'Blue'},
    {'color': (255, 255, 0), 'name': 'Yellow'},
    {'color': (0, 255, 255), 'name': 'Cyan'},
    {'color': (255, 0, 255), 'name': 'Magenta'},
    {'color': (255, 255, 255), 'name': 'White'},
    {'color': (0, 0, 0), 'name': 'Black'},
]


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
        logger.debug(f"A file of {len(image_as_bytearray)} bytes downloaded from the message")
    except Exception as e:
        raise IOError("Failed to download file attached to the message", e)

    try:
        logger.debug("Processing image file from the message")
        out_image, hist = quantize(image_as_bytearray, HARDCODED_PALETTE)
        logger.debug("Processing finished, sending the result to the chat")
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=image_to_bytes(out_image),
                                  caption=str(hist))
    except Exception as e:
        raise IOError("Failed to process image", e)
