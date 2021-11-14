import logging
import os

from telegram import *
from telegram.ext import *
from yt_dlp.utils import DownloadError, ExtractorError

from src.utils import reply, reply_error, youtube_dl_info, youtube_dl_download, pydub_cut, sanitize_url, validate_ext, validate_length, ansi_escape
from src.auth import require_whitelist

logger = logging.getLogger(__name__)


# Conversation stages
STATE_ENTER_EXT, STATE_ENTER_LENGTH, STATE_CONFIRM = range(3)

def keyboard(state: int) -> ReplyKeyboardMarkup:
    """ Return ReplyKeyboardMarkup for a specfic state """

    if state == STATE_ENTER_EXT:
        buttons = [['video', 'audio'], ['abort']]
    elif state == STATE_ENTER_LENGTH:
        buttons = [['abort', 'full']]
    elif state == STATE_CONFIRM:
        buttons = [['abort', 'download']]
    else:
        raise ValueError(f"invalid state ({state})")

    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True, 
        one_time_keyboard=True
    )

def prompt_text(state: int) -> str:
    """ Return prompt text for a specific state """

    if state == STATE_ENTER_EXT:
        text = 'Choose format: <b>video</b> / <b>audio</b>'
    elif state == STATE_ENTER_LENGTH:
        text = 'Choose length: <b>full</b> / <b>hh:mm:ss-hh:mm:ss</b>'
    elif state == STATE_CONFIRM:
        text = 'Confirm ...'
    else:
        raise ValueError(f"invalid state ({state})")

    return text


@require_whitelist
def handle_abort(update: Update, ctx: CallbackContext):
    """ Abort (cancle) the converstation """

    reply(update.message, 'aborted')
    return ConversationHandler.END

@require_whitelist
def conversation_entry(update: Update, ctx: CallbackContext):
    """ Handle incoming url """

    url = sanitize_url(update.message.text)

    try:
        info = youtube_dl_info(url)
    except (DownloadError, ExtractorError) as e:
        # remove ansi colors
        error = ansi_escape.sub('', str(e))
        # remove ERROR: prefix
        error = error.replace('ERROR: ', '')

        reply_error(update.message, f'{error}\n({type(e).__name__})')
        return ConversationHandler.END

    # keep track of data
    ctx.chat_data["url"] = url
    ctx.chat_data["info"] = info

    # display url info
    reply(update.message, f'<strong>{info["title"]}</strong>\n<i>by {info["uploader"]}</i>')

    reply(update.message, prompt_text(STATE_ENTER_EXT), keyboard=keyboard(STATE_ENTER_EXT))  
    return STATE_ENTER_EXT

@require_whitelist
def conversation_enter_ext(update: Update, ctx: CallbackContext):
    """ Handle format selection (video/audio) """

    if update.message.text == 'abort': 
        return handle_abort(update, ctx)

    ext = validate_ext(update.message.text)
    if not ext:
        reply_error(update.message, 
            'invalid input. enter "audio" or "video"', 
            keyboard=keyboard(STATE_ENTER_EXT))

        return STATE_ENTER_EXT

    # keep track of data
    ctx.chat_data["ext"] = ext

    # skip length selection if ext=video
    if ext == 'video':
        ctx.chat_data['length'] = 'full'
        reply(update.message, prompt_text(STATE_CONFIRM), keyboard=keyboard(STATE_CONFIRM))
        return STATE_CONFIRM

    reply(update.message, prompt_text(STATE_ENTER_LENGTH), keyboard=keyboard(STATE_ENTER_LENGTH))
    return STATE_ENTER_LENGTH

@require_whitelist
def conversation_enter_length(update: Update, ctx: CallbackContext):
    """ Handle length selection (full/custom) """

    if update.message.text == 'abort': 
        return handle_abort(update, ctx)

    length = validate_length(update.message.text)
    if not length:
        reply_error(update.message, 
            'invalid input. enter "full" or a selection in this format -> HH:MM:SS-HH:MM:SS', 
            keyboard=keyboard(STATE_ENTER_EXT))

        return STATE_ENTER_LENGTH

    # keep track of data
    ctx.chat_data["length"] = length

    reply(update.message, prompt_text(STATE_CONFIRM), keyboard=keyboard(STATE_CONFIRM))
    return STATE_CONFIRM

@require_whitelist
def conversation_confirm(update: Update, ctx: CallbackContext):
    """ Handle "checkout" / actual download """

    if update.message.text != 'download': 
        return handle_abort(update, ctx)   

    try:

        reply(update.message, "Download started. Please wait ...")

        # 1.) download file
        logger.info(f"start download of {ctx.chat_data['url']} for {update.message.from_user.id}")
        ctx.bot.send_chat_action(update.message.chat_id, action=ChatAction.RECORD_AUDIO)
        filename = youtube_dl_download(ctx.chat_data['url'], ctx.chat_data['ext'])

        reply(update.message, "Download finished. Sending ...")

        # 2.) cut file
        if ctx.chat_data['length'] != 'full':
            logger.debug(f"cut file to {ctx.chat_data['length']}")
            new_duration = pydub_cut(filename, ctx.chat_data['length'])
            # update duration
            ctx.chat_data["info"]["duration"] = new_duration

        # 3.) send file
        logger.debug(f"start transferring file")
        ctx.bot.send_chat_action(update.message.chat_id, action=ChatAction.UPLOAD_AUDIO)
        with open(filename, 'rb') as fd:
            logger.debug('start transfer of file %s to client' % filename)
            
            if ctx.chat_data['ext'] == 'video':
                ctx.bot.send_video(
                    chat_id=update.message.chat_id, 
                    video=fd, 
                    timeout=180,
                    caption=ctx.chat_data["info"]["title"],
                    #performer=ctx.chat_data["info"]["uploader"],
                    duration=ctx.chat_data["info"]["duration"])

            elif ctx.chat_data['ext'] == 'audio':
                ctx.bot.send_audio(
                    chat_id=update.message.chat_id, 
                    audio=fd, 
                    timeout=180,
                    title=ctx.chat_data["info"]["title"],
                    performer=ctx.chat_data["info"]["uploader"],
                    duration=ctx.chat_data["info"]["duration"])

            logger.info(f"transfer of {filename} for {update.message.from_user.id} finished")

    except youtube_dl.utils.DownloadError as e:
        # remove ansi colors
        error = ansi_escape.sub('', str(e))
        # remove ERROR: prefix
        error = error.replace('ERROR: ', '')
        
        reply_error(update.message, f'{error}\n({type(e).__name__})')

    finally:
        cleanup(filename)

    return ConversationHandler.END


def cleanup(filename: str):
    part_filename = filename + ".part"

    if os.path.isfile(filename):
        os.remove(filename)

    if os.path.isfile(part_filename):
        os.remove(part_filename)
