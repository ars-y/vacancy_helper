from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
)

from .constants import END_ROUTES, START_ROUTES
from vacscoll.workers import get_vacsid


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

    context.user_data['src_name'] = query.data

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('Назад', callback_data='back')]]
    )
    await query.edit_message_text(
        'Перечислите ключевые слова для поиска',
        reply_markup=reply_markup
    )

    return START_ROUTES


async def collect_all(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('Назад', callback_data='back')]]
    )

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

    name: str = context.user_data['src_name']
    del context.user_data['src_name']

    vacs_ids: list = await get_vacsid(name, keywords)

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton('Назад', callback_data='back')]]
    )
    await update.message.reply_text(
        f'Найдено вакансий: {len(vacs_ids)}',
        reply_markup=reply_markup
    )

    return END_ROUTES


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation with bot."""
    user_data = context.user_data
    if 'keywords' in user_data:
        del user_data['keywords']
    
    if 'src_name' in user_data:
        del user_data['src_name']

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
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex('^Done$')),
                    recieve_keywords
                ),
                CallbackQueryHandler(menu, pattern='back'),
            ],
            END_ROUTES: [
                CallbackQueryHandler(menu, pattern='back'),
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )
