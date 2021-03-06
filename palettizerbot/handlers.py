from telegram import Update
from telegram.ext import CallbackContext
import logging
from importlib import resources
from palettizer.quantize import quantize
from palettizer.imgutils import image_to_bytes
from palettizer.palette import Palette
from palettizer.htmlview import image_and_palette_as_html


logger = logging.getLogger(__name__)


class ParseParameterException(Exception):
    pass


def on_error(update: object, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update):
        update.message.reply_text(text="Something went badly wrong, please contact support")


def on_invalid_message(update: Update, context: CallbackContext):
    update.message.reply_text(text="Invalid message, type /start for help")


def on_message_with_image(update: Update, context: CallbackContext):
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
        palette_ids, n_colors = __parse_params_from_message(update)
    except ParseParameterException as e:
        logger.debug(e)
        context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
        return

    try:
        image_as_bytearray = file.download_as_bytearray()
        logger.debug(f"A file of {len(image_as_bytearray)} bytes downloaded from the message")
    except Exception as e:
        raise IOError("Failed to download file attached to the message", e)

    try:
        logger.debug("Processing image file from the message")
        q_image = quantize(img=image_as_bytearray,
                           palette=Palette.from_predefined(palette_ids),
                           n_colors=n_colors)
    except Exception as e:
        raise IOError("Failed to process image") from e

    try:
        logger.debug("Processing finished, sending the result to the chat")
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=image_to_bytes(q_image.image))
        response_html = image_and_palette_as_html(q_image)
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=str.encode(response_html),
                                  filename="result.html")
    except Exception as e:
        raise Exception("Failed to send response to chat") from e


def __parse_params_from_message(update: Update) -> (list, int):
    palette_ids = []
    n_colors = 0

    caption = update.message.caption
    if caption and len(caption) > 0:
        try:
            n_colors = __parse_n_colors(caption)
            return palette_ids, n_colors
        except ParseParameterException as e:
            logger.debug(e)

        params = caption.split(' ')
        if len(params) >= 1:
            palette_ids = params[0].split(',')

        for p in palette_ids:
            if p not in Palette.PREDEFINED_PALETTES:
                raise ParseParameterException(
                    f'Unknown palette ID: {p}, expected one of the following: {Palette.PREDEFINED_PALETTES}')

        if len(params) >= 2:
            n_colors = __parse_n_colors(params[1])

    return palette_ids, n_colors


def __parse_n_colors(input_str: str) -> int:
    try:
        n_colors = int(input_str)
    except Exception as e:
        logger.debug(e)
        raise ParseParameterException(f'Invalid parameter {input_str}, a positive integer expected')
    if n_colors < 0:
        raise ParseParameterException(f'Invalid number of colors {n_colors}, a positive integer expected')
    return n_colors


def on_start_command(update: Update, context: CallbackContext):
    try:
        text = resources.read_text("palettizerbot.resources", "help.txt")
    except Exception as e:
        raise Exception(f"Failed to help.txt from resources") from e

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
