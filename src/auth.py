from functools import wraps

from telegram import *
from telegram.ext import *

from src.utils import reply, reply_error
from config import WHITELIST_FILE, ADMIN_USID



def require_admin(f) -> callable:
    """ Permit callback execution only if requests originate from admin usid """

    @wraps(f)
    def decorated(update: Update, ctx: CallbackContext):
        
        usid = update.message.from_user.id

        if is_admin(usid):
            return f(update, ctx)

        reply_error(update.message, "not authorized.")
        

    return decorated

def require_whitelist(f) -> callable:
    """ Permit callback execution only if requests originate from whitelisted usid """

    @wraps(f)
    def decorated(update: Update, ctx: CallbackContext):
        
        usid = update.message.from_user.id

        if is_whitelisted(usid):
            return f(update, ctx)

        reply_error(update.message, "not authorized.")
        

    return decorated


def is_admin(usid: int) -> bool:
    """ Determine if usid is admin """

    # always permit access for admin
    if ADMIN_USID and usid == ADMIN_USID:
        return True
    
    # deny access otherwise..
    return False

def is_whitelisted(usid: int) -> bool:
    """ Determine if usid is whitelisted """

    # always permit access for admin
    if is_admin(usid):
        return True

    # check if usid is whitelisted
    whitelist = load_whitelist(WHITELIST_FILE)
    if usid in whitelist:
        return True
    
    # deny access otherwise..
    return False



def load_whitelist(filename: str) -> list:
    """ Load usids from whitelist.txt into list """

    with open(filename, "r") as whitelist:
        return list(map(lambda x: int(x.strip()), whitelist.readlines()))

def save_whitelist(filename:str, new: list) -> bool:
    """ Save usid list into whitelist.txt """

    with open(filename, "w") as whitelist:
        new = list(map(lambda x: str(x), new))
        whitelist.write("\n".join(new))
        return True