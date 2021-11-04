import logging
import re
import os
from uuid import uuid4
from glob import glob

from telegram import *
from telegram.ext import *
import youtube_dl
from pydub import AudioSegment

from config import WORK_DIR, CREDENTIALS

YTDL_COMMON_OPTS = {
    'logger': logging.getLogger('youtube-dl'),
    'username': CREDENTIALS['youtube']['username'],
    'password': CREDENTIALS['youtube']['password'],
}


logger = logging.getLogger(__name__)


def reply_error(message: Message, text: str, keyboard: ReplyKeyboardMarkup = None) -> None:
    """ Reply error """
    return reply(
        message=message, 
        text=f"<b>Error:</b> {text}", 
        keyboard=keyboard)

def reply(message: Message, text: str, keyboard: ReplyKeyboardMarkup = None) -> None:
    """ Common reply"""

    # indicate that bot is responding
    message.bot.send_chat_action(message.chat_id, action=ChatAction.TYPING)

    return message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )



def sanitize_url(url: str):
    YT_URL_PLAYLIST_ATTR = "&list="

    # remove playlist information from url
    # example: https://www.youtube.com/watch?v=dQw4w9WgXcQ [ &list=PL634F2B56B8C346A2 ]
    if YT_URL_PLAYLIST_ATTR in url:
        url = url[:url.index(YT_URL_PLAYLIST_ATTR)]

    return url

def validate_ext(ext: str):
    if ext == "video" or ext == "audio": return ext
    return False

def validate_length(length: str):
    if length == "full": return length

    try:
        [start, end] = length.split("-")
        [SH, SM, SS] = start.split(":")
        [EH, EM, ES] = end.split(":")
    except (IndexError, ValueError):
        return False

    return length


def youtube_dl_info(url: str) -> dict:
    opts = {
        **YTDL_COMMON_OPTS,
        'format': 'bestvideo+bestaudio/best'
    }

    # load audio information
    with youtube_dl.YoutubeDL(opts) as ydl:
        logger.debug('using youtube-dl opts: %r' % opts)
        info = ydl.extract_info(url, download=False)

    return info

def progress_hook(p):
    print("progress " + str(p))

def youtube_dl_download(url: str, ext: str, progress_cb: callable = None) -> str:
    
    # format correction
    if ext == 'video': ext = 'bestvideo+bestaudio/best'
    elif ext == 'audio': ext = 'bestaudio/best'

    filename = os.path.join(WORK_DIR, str(uuid4()))
    opts = {
        **YTDL_COMMON_OPTS,
        'outtmpl': filename,
        'format': ext,
        'forceid': True,
        #'progress_hooks': [progress_cb]
    }

    # load audio information
    with youtube_dl.YoutubeDL(opts) as ydl:
        logger.debug('using youtube-dl opts: %r' % opts)
        ydl.download([url])

    filename = glob(filename + '*') # workaround for unexpected extensions amend by youtube-dl
    return filename[0]

def pydub_cut(filename: str, length: str) -> int:

    length = length.split('-')
    start = length_to_msec(length[0])
    end = length_to_msec(length[1])

    segment = AudioSegment.from_file(filename)
    partial_segement = segment[start:end]
    partial_segement.export(filename, format="mp3")

    new_duration_in_sec = (end - start) / 1000

    return new_duration_in_sec


def length_to_msec(length):
    v = [int(x) for x in length.split(':')]
    return v[0]*60*60*1000 + v[1]*60*1000 + v[2]*1000

# from: https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
ansi_escape = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)