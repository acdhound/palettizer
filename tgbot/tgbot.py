from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import Filters
import sys
from handlers import handle_message_with_image


def start(update: Update, context: CallbackContext):
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
    - Write the comma-separated list of palette IDs you need (see the full list above)
    - Write the maximum number of colors you'd like to use (default is 30)
    - The full message should look like this: arton,mtn94 15
    - Send the message and wait a couple of minutes. I'll pick up the colors for you.
""")


def img(update: Update, context: CallbackContext):
    handle_message_with_image(update, context)


def reject(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid message, type /start for help")


token = sys.argv[1]

updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler(command='start', callback=start)
dispatcher.add_handler(start_handler)

img_filter = Filters.photo | Filters.document.image
img_handler = MessageHandler(filters=img_filter, callback=img)
dispatcher.add_handler(img_handler)

reject_handler = MessageHandler(filters=(~Filters.command & ~img_filter), callback=reject)
dispatcher.add_handler(reject_handler)

updater.start_polling()
