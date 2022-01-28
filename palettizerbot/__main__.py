# todo this is a hack to configure logging before a logger is initialized in each imported module
from . import initlogging
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import Filters
import sys
from . handlers import on_error, on_start_command, on_invalid_message, on_message_with_image


def main():
    token = sys.argv[1]

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_error_handler(on_error)

    start_handler = CommandHandler(command='start', callback=on_start_command)
    dispatcher.add_handler(start_handler)

    img_filter = Filters.photo | Filters.document.image
    img_handler = MessageHandler(filters=img_filter, callback=on_message_with_image)
    dispatcher.add_handler(img_handler)

    reject_handler = MessageHandler(filters=(~Filters.command & ~img_filter),
                                    callback=on_invalid_message)
    dispatcher.add_handler(reject_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
