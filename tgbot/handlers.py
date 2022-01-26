from telegram import Update
from telegram.ext import CallbackContext
import logging


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
    if file.file_size > 10 * 1024 * 1024:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="File must be less than 10 MB")
        return
    bytes_array = file.download_as_bytearray()
    # todo process the image here
    logger.info("File of {} bytes was downloaded".format(len(bytes_array)))

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="The operation is not supported yet")
