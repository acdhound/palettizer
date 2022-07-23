from telegram import Update
from telegram.ext import CallbackContext
import logging
from . userstep import UserStep


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
    __set_step_to_context(context, UserStep())
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def on_picture(update: Update, context: CallbackContext):
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
    if file.file_size > 10 * 1024 * 1024:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please send a picture up to 10 MB size")
        return

    try:
        image_as_bytearray: bytes = file.download_as_bytearray()
        logger.debug(f"A file of {len(image_as_bytearray)} bytes downloaded from the message")
    except Exception as e:
        raise IOError("Failed to download file attached to the message", e)

    __set_step_to_context(context, UserStep())
    __set_picture_to_context(context, image_as_bytearray)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Picture was successfully uploaded")


def on_palette(update: Update, context: CallbackContext):
    pass


def on_text(update: Update, context: CallbackContext):
    pass


def __get_step_from_context(context: CallbackContext) -> UserStep:
    step = context.user_data["step"]
    if not isinstance(step, UserStep):
        raise Exception("Invalid user step in the context")
    return step


def __set_step_to_context(context: CallbackContext, step: UserStep):
    context.user_data["step"] = step


def __get_picture_from_context(context: CallbackContext):
    picture = context.user_data["picture"]
    if not isinstance(picture, bytes):
        raise Exception("Can't get the picture from the context")
    return picture


def __set_picture_to_context(context: CallbackContext, picture: bytes):
    context.user_data["picture"] = picture
