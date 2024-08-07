from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import CallbackContext
import logging
import os
from typing import Optional, Union
from palettizer.palette import Palette
from palettizer.quantize import quantize, InvalidImageException, MAX_IMAGE_SIZE_BYTES, MAX_IMAGE_SIZE_MB, DELTA_E_METRIC, EUCLIDEAN_METRIC
from palettizer.htmlview import image_and_palette_as_html
from palettizer.imgutils import image_to_bytes

logger = logging.getLogger(__name__)


def on_error(update: object, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Something has gone wrong, please contact support @aleave")


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


def on_file(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Please, send a picture as .png, .jpg or other image format")


def on_query(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    tokens = query.data.split(" ")
    if len(tokens) <= 0:
        return
    if tokens[0] == "palette":
        if len(tokens) >= 2:
            __set_palette_to_context(context, tokens[1])
        else:
            __set_palette_to_context(context, None)
        __send_n_colors_message(query, context)
    elif tokens[0] == "no_colors":
        __set_n_colors_to_context(context, 0)
        __send_start_processing_message(update, context)
    elif tokens[0] == "processing":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Processing is in progress, please wait. It might take a few minutes.")
        __do_processing_and_send_result(update, context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Unexpected data, lease type /start")


def on_text(update: Update, context: CallbackContext):
    if (__get_picture_from_context(context) is None
            or __get_n_colors_from_context(context) is not None):
        return
    try:
        n_colors: int = int(update.message.text)
    except Exception as e:
        logger.info("Could not parse number of colors from the message")
        logger.debug(e)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter only numbers")
        return
    __set_n_colors_to_context(context, n_colors)
    __send_start_processing_message(update, context)


def __send_palettes(update: Update, context: CallbackContext):
    markup_buttons = list(map(
        lambda i: [
            InlineKeyboardButton(text=i[1].name, callback_data="palette " + i[0]),
            InlineKeyboardButton(text="See colors", url=i[1].url)
        ],
        [(i, Palette.from_predefined(i)) for i in Palette.PREDEFINED_PALETTES]
    ))
    markup_buttons.append(
        [InlineKeyboardButton(text="Don't use a palette", callback_data="palette")]
    )
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Which palette would you like to use?",
                             reply_markup=InlineKeyboardMarkup(markup_buttons))


def __send_n_colors_message(query: CallbackQuery, context: CallbackContext):
    palette = __get_palette_from_context(context)
    text = ("Chosen palette: " + palette.name + os.linesep) if palette else ""
    text += "How many colors would you like to use? Type the number into the chat or press the button."
    query.edit_message_text(text)
    query.edit_message_reply_markup(InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Unlimited colors", callback_data="no_colors")]
    ]))


def __send_start_processing_message(update: Update, context: CallbackContext):
    palette = __get_palette_from_context(context)
    palette_name = "not set" if not palette else palette.name

    n_colors = __get_n_colors_from_context(context)
    n_colors = "unlimited" if n_colors <= 0 else "up to {}".format(n_colors)

    text = """Your choice:
    Palette: {}
    Colors: {}""".format(palette_name, n_colors)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Get result!", callback_data="processing")]
    ])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             reply_markup=markup)


def __do_processing_and_send_result(update: Update, context: CallbackContext):
    picture: bytes = __get_picture_from_context(context)
    palette: Palette = __get_palette_from_context(context)
    n_colors: int = __get_n_colors_from_context(context)

    try:
        logger.info("Processing image file from the message")
        q_image = quantize(img=picture, palette=palette, n_colors=n_colors,
                           metric=(DELTA_E_METRIC if n_colors > 0 else EUCLIDEAN_METRIC))
    except InvalidImageException as e:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sorry, your request can't be processed: " + str(e))
        return
    except Exception as e:
        raise Exception("Image quantization failed") from e

    try:
        logger.info("Processing finished, sending the result to the chat")
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=image_to_bytes(q_image.image))
        response_html = image_and_palette_as_html(q_image)
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=str.encode(response_html),
                                  filename="result.html")
        __cleanup_context(context)
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


def __set_picture_to_context(context: CallbackContext, picture: Union[bytes, bytearray, None]):
    if picture is None:
        if "picture" in context.user_data:
            context.user_data.pop("picture")
        return
    context.user_data["picture"] = picture


def __get_palette_from_context(context: CallbackContext):
    if "palette" not in context.user_data:
        return None
    palette = context.user_data["palette"]
    if not isinstance(palette, Palette):
        raise Exception("Can't get the palette from the context")
    return palette


def __set_palette_to_context(context: CallbackContext, palette_id: Union[str, None]):
    if not palette_id:
        if "palette" in context.user_data:
            context.user_data.pop("palette")
        return
    try:
        palette = Palette.from_predefined([palette_id])
    except Exception as e:
        raise Exception("Failed to find a palette by ID " + palette_id) from e
    if palette is None:
        raise Exception("Palette for ID {} is None".format(palette_id))
    context.user_data["palette"] = palette


def __get_n_colors_from_context(context: CallbackContext):
    if "n_colors" not in context.user_data:
        return None
    n_colors = context.user_data["n_colors"]
    if isinstance(n_colors, int):
        return n_colors
    else:
        return None


def __set_n_colors_to_context(context: CallbackContext, n_colors: Union[int, None]):
    if n_colors is None:
        if "n_colors" in context.user_data:
            context.user_data.pop("n_colors")
        return
    if n_colors <= 0:
        n_colors = 0
    context.user_data["n_colors"] = n_colors


def __cleanup_context(context: CallbackContext):
    __set_picture_to_context(context, None)
    __set_palette_to_context(context, None)
    __set_n_colors_to_context(context, None)


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
    if file.file_size > MAX_IMAGE_SIZE_BYTES:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please, send a picture up to {} MB size".format(MAX_IMAGE_SIZE_MB))
        return None

    try:
        image_binary = file.download_as_bytearray()
        logger.info(f"A file of {len(image_binary)} bytes downloaded from the message")
        return image_binary
    except Exception as e:
        raise IOError("Failed to download file attached to the message") from e
