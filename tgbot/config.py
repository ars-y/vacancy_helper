import os
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())


TELEGRAM_TOKEN: str | None = os.getenv('TELEGRAM_TOKEN')

TELEGRAM_CHAT_ID: str | None = os.getenv('TELEGRAM_CHAT_ID')
