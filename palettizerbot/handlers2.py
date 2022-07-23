from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import CallbackContext
import logging
from palettizer.palette import Palette
from typing import Optional


logger = logging.getLogger(__name__)


def on_error(update: object, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update):
        update.message.reply_text(text="Something went badly wrong, please contact support")


def on_start(update: Update, context: CallbackContext):
    text = """
Hi, I'm Palettizer bot. I will pick the right colors for you to paint anything.
Send me the picture you'd like paint.
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def on_picture(update: Update, context: CallbackContext):
    picture: bytes = __read_picture_as_bytes(update, context)
    if picture is not None:
        __set_picture_to_context(context, picture)
        __send_palettes(update, context)


def on_query(update: Update, context: CallbackContext):
    query = update.callback_query
    tokens = query.data.split(" ")
    if tokens[0] == "palette":
        __set_palette_to_context(context, tokens[1])
        __request_n_colors(query)
    elif tokens[0] == "processing":
        pass


def on_text(update: Update, context: CallbackContext):
    pass


def __send_palettes(update: Update, context: CallbackContext):
    inline_markup: InlineKeyboardMarkup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="Montana Black", callback_data="palette mtnblack"),
            InlineKeyboardButton(text="See colors", url="https://google.com")
        ],
        [
            InlineKeyboardButton(text="Montana 94", callback_data="palette mtn94"),
            InlineKeyboardButton(text="See colors", url="https://google.com")
        ],
        [
            InlineKeyboardButton(text="Arton", callback_data="palette arton"),
            InlineKeyboardButton(text="See colors", url="https://google.com")
        ],
        [
            InlineKeyboardButton(text="Tikkurila", callback_data="palette tikkurila"),
            InlineKeyboardButton(text="See colors", url="https://google.com")
        ],
    ])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Which palette would you like to use?",
                             reply_markup=inline_markup)


def __request_n_colors(query: CallbackQuery):
    query.edit_message_text("How many colors would you like?")
    query.edit_message_reply_markup(InlineKeyboardMarkup([
        [InlineKeyboardButton(text="No limits", callback_data="no_colors")]
    ]))


def __get_picture_from_context(context: CallbackContext):
    picture = context.user_data["picture"]
    if not isinstance(picture, bytes):
        raise Exception("Can't get the picture from the context")
    return picture


def __set_picture_to_context(context: CallbackContext, picture: bytes):
    context.user_data["picture"] = picture


def __get_palette_from_context(context: CallbackContext):
    palette = context.user_data["palette"]
    if not isinstance(palette, Palette):
        raise Exception("Can't get the palette from the context")
    return palette


def __set_palette_to_context(context: CallbackContext, palette_id: str):
    try:
        palette = Palette.from_predefined([palette_id])
    except Exception as e:
        raise Exception("Failed to find a palette by ID " + palette_id, e)
    if palette is None:
        raise Exception("Palette for ID {} is None".format(palette_id))
    context.user_data["palette"] = palette


def __read_picture_as_bytes(update: Update, context: CallbackContext) -> Optional[bytes]:
    if not update.message:
        raise Exception("Can't get a message from an Update")
    if not update.message.document and not update.message.photo:
        raise Exception("Message contains no photo or file")

    if update.message.document:
        mime_type = update.message.document.mime_type
        if not mime_type or (not mime_type.startswith("image")):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="File is not an image")
            return None
        file = update.message.document.get_file()
    else:
        photos = update.message.photo
        if len(photos) == 0:
            raise Exception("Message contains an empty PhotoSize array")
        file = photos[-1].get_file()

    if not file.file_size:
        raise Exception("Can't define file size")
    if file.file_size > 10 * 1024 * 1024:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please send a picture up to 10 MB size")
        return None

    try:
        image_as_bytearray: bytes = file.download_as_bytearray()
        logger.debug(f"A file of {len(image_as_bytearray)} bytes downloaded from the message")
        return image_as_bytearray
    except Exception as e:
        raise IOError("Failed to download file attached to the message", e)
