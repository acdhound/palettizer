# todo this is a hack to configure logging before a logger is initialized in each imported module
from . import initlogging
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import Filters
import sys
from . handlers2 import on_start, on_error, on_picture, on_palette, on_text
import logging


logger = logging.getLogger(__name__)


def main():
    token = sys.argv[1]

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_error_handler(on_error)

    start_handler = CommandHandler(command='start', callback=on_start, run_async=True)
    dispatcher.add_handler(start_handler)

    img_filter = Filters.photo | Filters.document.image
    picture_handler = MessageHandler(filters=img_filter, callback=on_picture, run_async=True)
    dispatcher.add_handler(picture_handler)

    palette_handler = CommandHandler(command='palette', callback=on_palette, run_async=True)
    dispatcher.add_handler(palette_handler)

    text_handler = MessageHandler(filters=Filters.text, callback=on_text, run_async=True)
    dispatcher.add_handler(text_handler)

    updater.start_polling()
    logger.info("Message polling for Telegram bot has started")
    updater.idle()


if __name__ == '__main__':
    main()
