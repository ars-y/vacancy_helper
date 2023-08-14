import logging
import os
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())


TELEGRAM_TOKEN: str | None = os.getenv('TELEGRAM_TOKEN')


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s: %(asctime)s : %(message)s ',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.getLogger('httpx').setLevel(logging.WARNING)
