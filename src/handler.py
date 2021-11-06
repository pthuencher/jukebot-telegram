from subprocess import check_output, CalledProcessError

from telegram import *
from telegram.ext import *

from src.utils import reply, reply_error
from src.auth import require_whitelist, require_admin, load_whitelist, save_whitelist

from config import WHITELIST_FILE, ADMIN_UID



def error_handler(update: Update, ctx: CallbackContext):
    """ Error handler """

    reply_error(update.message, ctx.error)
    raise ctx.error

@require_whitelist
def start_handler(update: Update, ctx: CallbackContext):
    """ Handler of /start command """
    
    reply(update.message, """ 
<strong>JukeBot</strong>
<i>v2021.11.06</i>
https://github.com/pthuencher/jukebot-telegram

<strong>Share a link or enter a URL to download audio file.</strong>
Use /update to fetch most recent youtube-dl /version.
    """)
    
@require_whitelist
def version_handler(update: Update, ctx: CallbackContext):
    """ Handler of /version command """
      
    try:
        resp = check_output(['youtube-dl', '--version'])
        reply(update.message, '<strong>youtube-dl:</strong> %s' % resp.decode('utf-8'))

    except CalledProcessError as e:
        reply_error(update.message, 'failed to determine version of youtube-dl\n%r' % e)

@require_admin
def update_handler(update: Update, ctx: CallbackContext):
    """ Handler of /update command """
        
    try:
        resp = check_output(['pip', 'install', 'youtube-dl', '--upgrade'])
        reply(update.message, resp.decode('utf-8'))

    except CalledProcessError as e:
        reply_error(update.message, 'failed to update youtube-dl\n%r' % e)

@require_admin
def grant_handler(update: Update, ctx: CallbackContext):
    """ Handler of /grant command """

    try:
        uid = update.message.text.split(" ")[1]
        uid = int(uid)
    except (IndexError, ValueError):
        reply_error(update.message, 
            "invalid input.\n<i>Usage: /grant uid</i>")
        return

    # update whitelist.txt
    whitelist = load_whitelist(WHITELIST_FILE)
    whitelist.append(uid)
    save_whitelist(WHITELIST_FILE, whitelist)

    reply(update.message, f"added '{uid}' to the whitelist.")

@require_admin
def revoke_handler(update: Update, ctx: CallbackContext):
    """ Handler of /revoke command """

    try:
        uid = update.message.text.split(" ")[1]
        uid = int(uid)
    except (IndexError, ValueError):
        reply_error(update.message, 
            "invalid input.\n<i>Usage: /revoke uid</i>")
        return

    # update whitelist.txt
    whitelist = load_whitelist(WHITELIST_FILE)
    whitelist.remove(uid)
    save_whitelist(WHITELIST_FILE, whitelist)

    reply(update.message, f"removed '{uid}' from the whitelist.")


def request_access_handler(update: Update, ctx: CallbackContext):
    """ Handler of /request_access command """
    
    user: User = update.message.from_user
    # send message to requesting user
    ctx.bot.send_message(chat_id=user.id, text='Access request send.')
    # send message to admin
    ctx.bot.send_message(chat_id=ADMIN_UID, 
        text=f'<b>Access Request</b> by {user.username} ({user.first_name} {user.last_name}). Use /grant {user.id} to grant access.',
        parse_mode=ParseMode.HTML)