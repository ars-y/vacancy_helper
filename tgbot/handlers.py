from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
)

from .constants import START_ROUTES, KEYWORDS_INPUT, END_ROUTES


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start bot with inline keyboard."""
    keyboard: list = [
        [InlineKeyboardButton('Подбор с hh.ru', callback_data='hh')],
        [InlineKeyboardButton('Подбор всех', callback_data='all')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Выберите источник вакансий',
        reply_markup=reply_markup,
    )

    return START_ROUTES


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    keyboard: list = [
        [InlineKeyboardButton('Подбор с hh.ru', callback_data='hh')],
        [InlineKeyboardButton('Подбор всех', callback_data='all')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        'Выберите источник вакансий',
        reply_markup=reply_markup,
    )

    return START_ROUTES


async def collect_from_hh(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    keyboard: list = [
        [InlineKeyboardButton('Назад', callback_data='back')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        'Перечислите ключевые слова для поиска',
        reply_markup=reply_markup
    )

    return KEYWORDS_INPUT


async def collect_all(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    keyboard: list = [
        [InlineKeyboardButton('Назад', callback_data='back')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        'Функция в разработке...',
        reply_markup=reply_markup
    )
    return END_ROUTES


async def recieve_keywords(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    keywords = update.message.text
    context.user_data['keywords'] = keywords

    keyboard: list = [
        [InlineKeyboardButton('Назад', callback_data='back')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f'Ты ввел следующие ключевые слова: {keywords.lower()}',
        reply_markup=reply_markup
    )

    return END_ROUTES


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation with bot."""
    user_data = context.user_data
    if 'keywords' in user_data:
        del user_data['keywords']

    await update.message.reply_text(
        'Подбор остановлен.\nДля запуска используйте команду /start'
    )

    user_data.clear()
    return ConversationHandler.END


def create_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
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
