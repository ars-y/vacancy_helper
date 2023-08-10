import logging
from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
)
from telegram.warnings import PTBUserWarning
from warnings import filterwarnings

from .constants import (
    ALL_BUTTON,
    BACK_BUTTON,
    CHUNK_SIZE,
    END_ROUTES,
    HH_BUTTON,
    NEXT_BUTTON,
    SEND_VACS,
    START_ROUTES,
)
from .keyboards import (
    move_to_keyboard,
    select_keyboard,
    url_keyboard
)
from .utils import format_message
from vacscoll.workers import get_vacs, remove_unrecieved


filterwarnings('ignore', r'.*CallbackQueryHandler', PTBUserWarning)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start bot with inline keyboard."""
    await update.message.reply_text(
        'Выберите источник вакансий',
        reply_markup=select_keyboard(),
    )

    return START_ROUTES


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Main menu with inline keyboard.
    Handle user select buttons.
    """
    logging.info('User return in main menu')

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
    """Select hh button handler."""
    logging.info('User select collect from api.hh.ru')

    query = update.callback_query
    await query.answer()

    context.user_data['src_name'] = query.data

    await query.edit_message_text(
        'Перечислите ключевые слова для поиска',
        reply_markup=move_to_keyboard('Назад', BACK_BUTTON)
    )

    return START_ROUTES


async def collect_all(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Select all button handler."""
    logging.info('User select collect from all aggregators')

    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        'Функция в разработке...',
        reply_markup=move_to_keyboard('Назад', BACK_BUTTON)
    )
    return END_ROUTES


async def recieve_keywords(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Message handler recieve keywords from user input
    to get vacancies from aggregator API.
    """
    logging.info('User input keywords')
    keywords = update.message.text
    context.user_data['keywords'] = keywords

    name: str = context.user_data['src_name']
    del context.user_data['src_name']

    logging.info('Trying get vacancies')
    vacancies: list = await get_vacs(name, keywords)

    if not vacancies:
        logging.info('Not found vacancies')
        await update.message.reply_text(
            'По вашему запросу вакансий не найдено',
            reply_markup=move_to_keyboard('Назад', BACK_BUTTON)
        )

        return END_ROUTES

    logging.info('Vacancies received successfully')
    context.user_data['vacs'] = vacancies
    vacs_info_message: str = f'Надено вакансий: {len(vacancies)}'
    vsize: int = len(vacancies)
    total_vacs: int = CHUNK_SIZE if CHUNK_SIZE < vsize else vsize

    await update.message.reply_text(
        vacs_info_message,
        reply_markup=move_to_keyboard(
            f'Показать {total_vacs} вакансии', NEXT_BUTTON
        )
    )

    return SEND_VACS


async def retrieve_vacancies(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    vacancies = context.user_data['vacs']
    vacs_chunk, vacancies = vacancies[:CHUNK_SIZE], vacancies[CHUNK_SIZE:]
    context.user_data['vacs'] = vacancies
    while vacs_chunk:
        logging.info('Bot sending vacancy info message')
        vacancy = vacs_chunk.pop()
        await query.message.reply_text(
            format_message(vacancy),
            reply_markup=url_keyboard(vacancy.url)
        )

    if not vacancies:
        logging.info('Vacancies are over. Bot offers to return to main menu')
        del context.user_data['vacs']
        await query.message.reply_text(
            'Больше вакансий нет',
            reply_markup=move_to_keyboard('Назад', BACK_BUTTON)
        )

        return END_ROUTES

    vsize: int = len(vacancies)
    total_vacs: int = CHUNK_SIZE if CHUNK_SIZE < vsize else vsize
    await query.message.reply_text(
        f'Показать ещё {total_vacs} вакансии',
        reply_markup=move_to_keyboard('Далее', NEXT_BUTTON)
    )

    return SEND_VACS


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation with bot."""
    logging.info('User cancel collecting')

    if 'vacs' in context.user_data:
        remove_unrecieved(context.user_data['vacs'])
        del context.user_data['vacs']

    await update.message.reply_text(
        'Подбор остановлен.\nДля запуска используйте команду /start'
    )

    context.user_data.clear()
    return ConversationHandler.END


def create_conversation_handler() -> ConversationHandler:
    """Creating ConversationHandler instance."""
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(collect_from_hh, pattern=HH_BUTTON),
                CallbackQueryHandler(collect_all, pattern=ALL_BUTTON),
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND), recieve_keywords
                ),
                CallbackQueryHandler(menu, pattern=BACK_BUTTON),
            ],
            SEND_VACS: [
                CallbackQueryHandler(retrieve_vacancies, pattern=NEXT_BUTTON),
            ],
            END_ROUTES: [
                CallbackQueryHandler(menu, pattern=BACK_BUTTON),
            ]
        },
        fallbacks=[CommandHandler('done', done)],
    )
