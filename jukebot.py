import logging
import sys
from argparse import ArgumentParser

from telegram import *
from telegram.ext import *

from src.core import start

logger = logging.getLogger(__name__)

try:
    from config import BOT_TOKEN
except ImportError:
    print("Error: Bot token not found. Define BOT_TOKEN in config.py to resolve this issue.")
    sys.exit(-1)

def parse_arguments() -> dict:
    parser = ArgumentParser(description="youtube-dl telegram bot interface")

    parser.add_argument("-d", "--debug", 
        help="set log-level to DEBUG", 
        action="store_true")

    parser.add_argument("-i", "--info", 
        help="set log-level to INFO", 
        action="store_true")
        
    return parser.parse_args()

if __name__ == '__main__':
    args: dict = parse_arguments()    

    log_level: int = logging.ERROR

    if args.debug:
        logger.debug(args)
        log_level = logging.DEBUG
    elif args.info:
        log_level = logging.INFO

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level
    )

    start()
    
