from subprocess import check_output, CalledProcessError

from telegram import *
from telegram.ext import *

from src.utils import reply, reply_error
from src.auth import require_whitelist, require_admin, load_whitelist, save_whitelist

try:
    from config import WHITELIST_FILE
except ImportError:
    WHITELIST_FILE = "whitelist.txt"



@require_whitelist
def error_handler(update: Update, ctx: CallbackContext):
    """ Error handler """

    reply_error(update.message, ctx.error)
    raise ctx.error

@require_whitelist
def start_handler(update: Update, ctx: CallbackContext):
    """ Handler of /start command """
    
    reply(update.message, """ 
<strong>JukeBot</strong>
<i>v2021.11.04</i>
https://github.com/pthuencher/python-telegram-bot-audio-downloader

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
        usid = update.message.text.split(" ")[1]
        usid = int(usid)
    except (IndexError, ValueError):
        reply_error(update.message, 
            "invalid input.\n<i>Usage: /grant usid</i>")
        return

    # update whitelist.txt
    whitelist = load_whitelist(WHITELIST_FILE)
    whitelist.append(usid)
    save_whitelist(WHITELIST_FILE, whitelist)

    reply(update.message, f"added '{usid}' to the whitelist.")

@require_admin
def revoke_handler(update: Update, ctx: CallbackContext):
    """ Handler of /revoke command """

    try:
        usid = update.message.text.split(" ")[1]
        usid = int(usid)
    except (IndexError, ValueError):
        reply_error(update.message, 
            "invalid input.\n<i>Usage: /revoke usid</i>")
        return

    # update whitelist.txt
    whitelist = load_whitelist(WHITELIST_FILE)
    whitelist.remove(usid)
    save_whitelist(WHITELIST_FILE, whitelist)

    reply(update.message, f"removed '{usid}' from the whitelist.")
