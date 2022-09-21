from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import CallbackContext
import logging
from typing import Optional, Union
from palettizer.palette import Palette
from palettizer.quantize import quantize
from palettizer.htmlview import image_and_palette_as_html
from palettizer.imgutils import image_to_bytes


logger = logging.getLogger(__name__)


def on_error(update: object, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Something went badly wrong, please contact support")


def on_start(update: Update, context: CallbackContext):
    text = """
Hi, I'm Palettizer bot. I will pick the right colors for you to paint anything.
Send me the picture you'd like paint.
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def on_picture(update: Update, context: CallbackContext):
    picture = __read_picture_as_bytes(update, context)
    if picture is not None:
        __set_picture_to_context(context, picture)
        __send_palettes(update, context)


def on_query(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    tokens = query.data.split(" ")
    if len(tokens) <= 0:
        return
    if tokens[0] == "palette":
        if len(tokens) >= 2:
            __set_palette_to_context(context, tokens[1])
        __send_n_colors_message(query)
    elif tokens[0] == "no_colors":
        __set_n_colors_to_context(context, 0)
        __send_start_processing_message(update, context)
    elif tokens[0] == "processing":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Processing is in progress, please wait. Usually it takes a few minutes.")
        __do_processing_and_send_result(update, context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Unexpected data, lease type /start")


def on_text(update: Update, context: CallbackContext):
    if __get_picture_from_context(context) is None:
        on_start(update, context)
        return
    try:
        n_colors: int = int(update.message.text)
    except Exception as e:
        logger.debug("Failed to parse number of colors from the message")
        logger.debug(e)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter only numbers")
        return
    __set_n_colors_to_context(context, n_colors)
    __send_start_processing_message(update, context)


def __send_palettes(update: Update, context: CallbackContext):
    # todo hardcode, palette names and URLs should be stored in palette JSONs
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
        [
            InlineKeyboardButton(text="Don't use a palette", callback_data="palette"),
        ]
    ])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Which palette would you like to use?",
                             reply_markup=inline_markup)


def __send_n_colors_message(query: CallbackQuery):
    query.edit_message_text("How many colors would you like to use? Type the number into the chat or press the button.")
    query.edit_message_reply_markup(InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Unlimited colors", callback_data="no_colors")]
    ]))


def __send_start_processing_message(update: Update, context: CallbackContext):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Get result!", callback_data="processing")]
    ])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Now everything is set, click the button to get the results.",
                             reply_markup=markup)


def __do_processing_and_send_result(update: Update, context: CallbackContext):
    picture: bytes = __get_picture_from_context(context)
    palette: Palette = __get_palette_from_context(context)
    n_colors: int = __get_n_colors_from_context(context)
    try:
        logger.debug("Processing image file from the message")
        q_image = quantize(img=picture, palette=palette, n_colors=n_colors)
    except Exception as e:
        raise IOError("Failed to process the image") from e
    try:
        logger.debug("Processing finished, sending the result to the chat")
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=image_to_bytes(q_image.image))
        response_html = image_and_palette_as_html(q_image)
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=str.encode(response_html),
                                  filename="result.html")
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Ready! Send another picture to start again.")
    except Exception as e:
        raise Exception("Failed to send the results to the chat") from e


def __get_picture_from_context(context: CallbackContext) -> Optional[Union[bytes, bytearray]]:
    if "picture" not in context.user_data:
        return None
    picture = context.user_data["picture"]
    if not isinstance(picture, bytes) and not isinstance(picture, bytearray):
        raise Exception("Can't get the picture from the context")
    return picture


def __set_picture_to_context(context: CallbackContext, picture: Union[bytes, bytearray]):
    context.user_data["picture"] = picture


def __get_palette_from_context(context: CallbackContext):
    if "palette" not in context.user_data:
        return None
    palette = context.user_data["palette"]
    if not isinstance(palette, Palette):
        raise Exception("Can't get the palette from the context")
    return palette


def __set_palette_to_context(context: CallbackContext, palette_id: str):
    try:
        palette = Palette.from_predefined([palette_id])
    except Exception as e:
        raise Exception("Failed to find a palette by ID " + palette_id) from e
    if palette is None:
        raise Exception("Palette for ID {} is None".format(palette_id))
    context.user_data["palette"] = palette


def __get_n_colors_from_context(context: CallbackContext):
    n_colors = context.user_data["n_colors"]
    if n_colors is not None and isinstance(n_colors, int):
        return n_colors
    else:
        return 0


def __set_n_colors_to_context(context: CallbackContext, n_colors: int):
    if n_colors <= 0:
        n_colors = 0
    context.user_data["n_colors"] = n_colors


def __read_picture_as_bytes(update: Update, context: CallbackContext) -> Optional[Union[bytes, bytearray]]:
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
        image_binary = file.download_as_bytearray()
        logger.debug(f"A file of {len(image_binary)} bytes downloaded from the message")
        return image_binary
    except Exception as e:
        raise IOError("Failed to download file attached to the message") from e