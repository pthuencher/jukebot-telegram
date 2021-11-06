from telegram import *
from telegram.ext import *

from src.handler import *
from test.common import chat, message

try:
    from config import BOT_TOKEN
except ImportError:
    print("ERROR: missing BOT_TOKEN. To resolve this issue define BOT_TOKEN in config.py")
    exit(-1)

try:
    from config import ADMIN_UID
except ImportError:
    ADMIN_UID = None

class TEST_BOT():

    def __init__(self):
        self.defaults = None

def test_grant_handler():

    assert 1 == 1