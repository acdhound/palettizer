from telegram import Update
from telegram.ext import CallbackContext
import logging
from palettizer.quantize import quantize
from palettizer.imgutils import image_to_bytes
from palettizer.palette import get_predefined_palette
from palettizer.palette import PREDEFINED_PALETTES


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
        out_image, hist = quantize(img=image_as_bytearray,
                                   palette=get_predefined_palette(palette_ids),
                                   n_colors=n_colors)
    except Exception as e:
        raise IOError("Failed to process image", e)

    try:
        logger.debug("Processing finished, sending the result to the chat")
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=image_to_bytes(out_image))
        response_text = '\n'.join(
            [f"{x['color']['vendor']} {x['color']['name']} (RGB {str(x['color']['color'])}) - {x['pixels']}"
             for x in hist.values()]
        )
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=response_text)
    except Exception as e:
        raise Exception("Failed to send response to chat", e)


def __parse_params_from_message(update: Update) -> (list, int):
    palette_ids = [PREDEFINED_PALETTES[0]]
    n_colors = 0

    caption = update.message.caption
    if caption and len(caption) > 0:
        params = caption.split(' ')
        if len(params) >= 1:
            palette_ids = params[0].split(',')

        for p in palette_ids:
            if p not in PREDEFINED_PALETTES:
                raise ParseParameterException(f'Unknown palette ID: {p}, expected one of the following: {PREDEFINED_PALETTES}')

        if len(params) >= 2:
            try:
                n_colors = int(params[1])
            except Exception as e:
                logger.debug(e)
                raise ParseParameterException(f'Invalid parameter {params[1]}, a positive integer expected')
            if n_colors < 0:
                raise ParseParameterException(f'Invalid number of colors {n_colors}, a positive integer expected')

    return palette_ids, n_colors


def on_start_command(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="""
  Hi, I'm Palettizer bot!

  I can decompose an image by a given color palette.
  My mission is to help artists who do large-scaled murals and want to chose the right colors from a palette provided by a paint vendor.
  Just send me a sketch for your future painting and select the palettes you'd like to use and I will show you which colors and in what proportion fit the most.

  Currently supported palettes (use their IDs to select palettes as described below):
    - Montana Black (ID mtnblack)
    - Montana 94 (ID mtn94)
    - Arton (ID arton)
    - Tikkurila (ID tikkurila)

  How to use me:
    - Attach your sketch to the message
    - Write the palette IDs you need separated by comma (see the full list above)
    - Write the maximum number of colors you'd like to use (default is 30)
    - The full message should look like this: arton,mtn94 15
    - Send the message and wait a couple of minutes. I'll pick up the colors for you.
    """)
