from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
)

from tgbot.config import TELEGRAM_TOKEN
from tgbot.constants import END_ROUTES, KEYWORDS_INPUT, START_ROUTES
from tgbot.handlers import (
    done,
    collect_all,
    collect_from_hh,
    menu,
    recieve_keywords,
    start
)


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(collect_from_hh, pattern='hh'),
                CallbackQueryHandler(collect_all, pattern='all'),
            ],
            KEYWORDS_INPUT: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex('^Done$')),
                    recieve_keywords
                )
            ],
            END_ROUTES: [
                CallbackQueryHandler(menu, pattern='back'),
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
