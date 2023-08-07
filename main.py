from telegram import Update
from telegram.ext import Application

from tgbot.config import TELEGRAM_TOKEN
from tgbot.handlers import create_conversation_handler


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = create_conversation_handler()

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
