from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
)

from .constants import (
    ALL_BUTTON,
    BACK_BUTTON,
    END_ROUTES,
    HH_BUTTON,
    START_ROUTES,
)
from .keyboards import back_keyboard, select_keyboard
from vacscoll.workers import get_vacs


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start bot with inline keyboard."""
    await update.message.reply_text(
        'Выберите источник вакансий',
        reply_markup=select_keyboard(),
    )

    return START_ROUTES


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        'Выберите источник вакансий',
        reply_markup=select_keyboard(),
    )

    return START_ROUTES


async def collect_from_hh(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data['src_name'] = query.data

    await query.edit_message_text(
        'Перечислите ключевые слова для поиска',
        reply_markup=back_keyboard()
    )

    return START_ROUTES


async def collect_all(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        'Функция в разработке...',
        reply_markup=back_keyboard()
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

    vacancies: list = await get_vacs(name, keywords)

    await update.message.reply_text(
        f'Найдено вакансий: {len(vacancies)}',
        reply_markup=back_keyboard()
    )

    return END_ROUTES


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation with bot."""
    await update.message.reply_text(
        'Подбор остановлен.\nДля запуска используйте команду /start'
    )

    context.user_data.clear()
    return ConversationHandler.END


def create_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(collect_from_hh, pattern=HH_BUTTON),
                CallbackQueryHandler(collect_all, pattern=ALL_BUTTON),
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex('^Done$')),
                    recieve_keywords
                ),
                CallbackQueryHandler(menu, pattern=BACK_BUTTON),
            ],
            END_ROUTES: [
                CallbackQueryHandler(menu, pattern=BACK_BUTTON),
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )
