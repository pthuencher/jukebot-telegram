from sys import exit
from os import mkdir
from argparse import ArgumentParser

from telegram import *
from telegram.ext import *

from src.handler import *
from src.conversation import *

from config import WORK_DIR, WHITELIST_FILE

try:
    from config import BOT_TOKEN
except ImportError:
    print("ERROR: missing BOT_TOKEN. To resolve this issue define BOT_TOKEN in config.py")
    exit(-1)



def register_handlers(dispatcher: Dispatcher) -> bool:
    """ Register all Command/Message Handlers """

    # error handler
    dispatcher.add_error_handler(error_handler)

    # basic command handlers
    dispatcher.add_handler(CommandHandler("start", start_handler))
    dispatcher.add_handler(CommandHandler("version", version_handler))
    dispatcher.add_handler(CommandHandler("update", update_handler))

    # permission handlers
    dispatcher.add_handler(CommandHandler("grant", grant_handler))
    dispatcher.add_handler(CommandHandler("revoke", revoke_handler))

    # converstation handler
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.all, conversation_entry, pass_chat_data=True)],

        states={
            STATE_ENTER_EXT: [MessageHandler(Filters.all, conversation_enter_ext, pass_chat_data=True)],
            STATE_ENTER_LENGTH: [MessageHandler(Filters.all, conversation_enter_length, pass_chat_data=True)],

            STATE_CONFIRM: [MessageHandler(Filters.all, conversation_confirm, pass_chat_data=True)]
        },

        fallbacks=[CommandHandler('abort', handle_abort)]
    ))


def start() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    register_handlers(dispatcher)

    # Initialize working directory
    try:
        mkdir(WORK_DIR)
    except FileExistsError:
        pass # ignore if already exists

    # create whitelist.txt
    open(WHITELIST_FILE, "w")

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

