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
    BACK_BUTTON,
    CHUNK_SIZE,
    DELIVERY_VACS,
    END_ROUTES,
    FIND_BUTTON,
    HH_BUTTON,
    NEXT_BUTTON,
    SELECT_SRC,
    SKIP_BUTTON,
    TYPING_AREA,
    TYPING_KEYWORDS,
)
from .keyboards import (
    next_skip_back,
    move_to_keyboard,
    select_keyboard,
    url_keyboard
)
from .utils import format_message
from vacscoll.workers import get_areas, get_vacs, remove_unrecieved


filterwarnings('ignore', r'.*CallbackQueryHandler', PTBUserWarning)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start bot with inline keyboard."""
    await update.message.reply_text(
        'Выберите источник вакансий',
        reply_markup=select_keyboard(),
    )

    return TYPING_KEYWORDS


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

    return TYPING_KEYWORDS


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

    return TYPING_KEYWORDS


async def keywords_prompt(
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

    await update.message.reply_text(
        'Указать город?',
        reply_markup=next_skip_back('Далее', 'Пропустить', 'Назад')
    )

    return TYPING_AREA


async def location_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Sending location request to user."""
    await update.callback_query.answer()

    await update.callback_query.edit_message_text(
        'Введите название города или области',
        reply_markup=move_to_keyboard('Назад', BACK_BUTTON)
    )

    return TYPING_AREA


async def location_prompt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Getting location entered from user."""
    logging.info('User entered location')
    location = update.message.text

    src_name = context.user_data['src_name']
    area_id = await get_areas(src_name, location)

    if not area_id:
        logging.info('Entered location not found')
        await update.message.reply_text(
            'Введенного города не существует',
            reply_markup=next_skip_back(
                'Ввести ещё раз', 'Пропустить', 'Назад'
            )
        )

        return TYPING_AREA

    context.user_data['area'] = area_id
    await update.message.reply_text(
        'Начать поиск вакансий',
        reply_markup=move_to_keyboard('Найти', FIND_BUTTON)
    )

    return DELIVERY_VACS


async def skip_location(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Selected to skip enter location."""
    logging.info('User skip entered location')
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        'Начать поиск вакансий',
        reply_markup=move_to_keyboard('Найти', FIND_BUTTON)
    )
    return DELIVERY_VACS


async def recieve_vacancies(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Recieve vacancies from vacancy collector."""
    query = update.callback_query
    await query.answer()

    src_name: str = context.user_data['src_name']
    del context.user_data['src_name']

    keywords = context.user_data['keywords']
    del context.user_data['keywords']

    area = context.user_data.get('area')
    if area:
        del context.user_data['area']

    logging.info('Trying get vacancies')
    vacancies: list = await get_vacs(src_name, keywords, area)

    if not vacancies:
        logging.info('Not found vacancies')
        await query.edit_message_text(
            'По вашему запросу вакансий не найдено',
            reply_markup=move_to_keyboard('Назад', BACK_BUTTON)
        )

        return END_ROUTES

    logging.info('Vacancies received successfully')
    context.user_data['vacs'] = vacancies
    vacs_info_message: str = f'Надено вакансий: {len(vacancies)}'
    vsize: int = len(vacancies)
    total_vacs: int = CHUNK_SIZE if CHUNK_SIZE < vsize else vsize

    await query.edit_message_text(
        vacs_info_message,
        reply_markup=move_to_keyboard(
            f'Показать {total_vacs} вакансии', NEXT_BUTTON
        )
    )

    return DELIVERY_VACS


async def retrieve_vacancies(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Sending chunk of vacancy to user."""
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

    return DELIVERY_VACS


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
            SELECT_SRC: [
                CallbackQueryHandler(collect_from_hh, pattern=HH_BUTTON),
                CallbackQueryHandler(menu, pattern=BACK_BUTTON),
            ],
            TYPING_KEYWORDS: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND), keywords_prompt
                ),
                CallbackQueryHandler(collect_from_hh, pattern=HH_BUTTON),
                CallbackQueryHandler(menu, pattern=BACK_BUTTON),
            ],
            TYPING_AREA: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND), location_prompt
                ),
                CallbackQueryHandler(skip_location, pattern=SKIP_BUTTON),
                CallbackQueryHandler(location_request, pattern=NEXT_BUTTON),
                CallbackQueryHandler(menu, pattern=BACK_BUTTON),
            ],
            DELIVERY_VACS: [
                CallbackQueryHandler(recieve_vacancies, pattern=FIND_BUTTON),
                CallbackQueryHandler(retrieve_vacancies, pattern=NEXT_BUTTON),
            ],
            END_ROUTES: [
                CallbackQueryHandler(menu, pattern=BACK_BUTTON),
            ]
        },
        fallbacks=[CommandHandler('done', done)],
    )
