from functools import wraps

from telegram import *
from telegram.ext import *

from src.utils import reply, reply_error
from config import WHITELIST_FILE, ADMIN_UID



def require_admin(f) -> callable:
    """ Permit callback execution only if requests originate from admin uid """

    @wraps(f)
    def decorated(update: Update, ctx: CallbackContext):
        
        uid = update.message.from_user.id

        if is_admin(uid):
            return f(update, ctx)

        reply_error(update.message, "not authorized.")
        

    return decorated

def require_whitelist(f) -> callable:
    """ Permit callback execution only if requests originate from whitelisted uid """

    @wraps(f)
    def decorated(update: Update, ctx: CallbackContext):

        uid = update.message.from_user.id

        if is_whitelisted(uid):
            return f(update, ctx)

        reply_error(update.message, "not authorized. /request_access")
        

    return decorated


def is_admin(uid: int) -> bool:
    """ Determine if uid is admin """

    # always permit access for admin
    if ADMIN_UID and uid == ADMIN_UID:
        return True
    
    # deny access otherwise..
    return False

def is_whitelisted(uid: int) -> bool:
    """ Determine if uid is whitelisted """

    # always permit access for admin
    if is_admin(uid):
        return True

    # check if uid is whitelisted
    whitelist = load_whitelist(WHITELIST_FILE)
    if uid in whitelist:
        return True
    
    # deny access otherwise..
    return False



def load_whitelist(filename: str) -> list:
    """ Load uids from whitelist.txt into list """

    with open(filename, "r") as whitelist:
        return list(map(lambda x: int(x.strip()), whitelist.readlines()))

def save_whitelist(filename:str, new: list) -> bool:
    """ Save uid list into whitelist.txt """

    with open(filename, "w") as whitelist:
        new = list(map(lambda x: str(x), new))
        whitelist.write("\n".join(new))
        return True