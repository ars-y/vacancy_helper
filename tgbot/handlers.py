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
from .keyboards import build_keyboard, url_keyboard
from .utils import format_message
from vacscoll.workers import get_areas, get_vacs, remove_unrecieved


filterwarnings('ignore', r'.*CallbackQueryHandler', PTBUserWarning)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start bot with inline keyboard."""
    await update.message.reply_text(
        'Выберите источник вакансий',
        reply_markup=build_keyboard([('Подбор с hh.ru', HH_BUTTON)])
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
        reply_markup=build_keyboard([('Подбор с hh.ru', HH_BUTTON)])
    )

    return TYPING_KEYWORDS


async def collect_from_hh(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Select hh button handler."""
    logging.info('The user is in the API HH block ')

    query = update.callback_query
    await query.answer()

    if 'src_name' not in context.user_data:
        context.user_data['src_name'] = query.data

    await query.edit_message_text(
        'Перечислите ключевые слова для поиска',
        reply_markup=build_keyboard([('Назад', BACK_BUTTON)])
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
    logging.info('User enters keywords')
    keywords = update.message.text
    context.user_data['keywords'] = keywords

    buttons: list = [
        ('Искать по России', SKIP_BUTTON),
        ('Назад', BACK_BUTTON),
    ]
    await update.message.reply_text(
        'Укажите город или область',
        reply_markup=build_keyboard(buttons)
    )

    return TYPING_AREA


async def location_prompt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Getting location entered from user."""
    logging.info('User enters location')
    location = update.message.text

    src_name = context.user_data['src_name']
    logging.info('Checking entered location')
    area_id = await get_areas(src_name, location)

    if not area_id:
        logging.info('Entered location not found')
        buttons: list = [
            ('Искать по России', SKIP_BUTTON),
            ('Назад', BACK_BUTTON),
        ]
        text_message: str = (
            'Такого города или области не существует.\n'
            'Попробуйте указать ещё раз'
        )
        await update.message.reply_text(
            text_message,
            reply_markup=build_keyboard(buttons)
        )

        return TYPING_AREA

    logging.info('Location confirmed')
    buttons: list = [
        ('Найти', FIND_BUTTON),
        ('Назад', BACK_BUTTON),
    ]
    context.user_data['area'] = area_id
    keywords = context.user_data['keywords']
    text_message: str = (
        f'Поиск по ключевыми словам: {keywords}\n'
        f'Локация: {location.capitalize()}'
    )
    await update.message.reply_text(
        text_message,
        reply_markup=build_keyboard(buttons)
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

    buttons: list = [
        ('Найти', FIND_BUTTON),
        ('Назад', BACK_BUTTON),
    ]
    keywords = context.user_data['keywords']
    text_message: str = (
        f'Поиск по ключевыми словам: {keywords}\n'
        f'Локация: Россия'
    )
    await query.edit_message_text(
        text_message,
        reply_markup=build_keyboard(buttons)
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
            reply_markup=build_keyboard([('В начало', BACK_BUTTON)])
        )

        return END_ROUTES

    logging.info('Vacancies received successfully')
    context.user_data['vacs'] = vacancies
    vacs_info_message: str = f'Надено вакансий: {len(vacancies)}'
    vsize: int = len(vacancies)
    total_vacs: int = CHUNK_SIZE if CHUNK_SIZE < vsize else vsize

    await query.edit_message_text(
        vacs_info_message,
        reply_markup=build_keyboard(
            [(f'Показать {total_vacs} вакансии', NEXT_BUTTON)]
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
            reply_markup=url_keyboard('Подробнее', vacancy.url)
        )

    if not vacancies:
        logging.info('Vacancies are over. Bot offers to return to main menu')
        del context.user_data['vacs']
        await query.message.reply_text(
            'Больше вакансий нет',
            reply_markup=build_keyboard([('В начало', BACK_BUTTON)])
        )

        return END_ROUTES

    vsize: int = len(vacancies)
    total_vacs: int = CHUNK_SIZE if CHUNK_SIZE < vsize else vsize
    await query.message.reply_text(
        f'Показать ещё {total_vacs} вакансии',
        reply_markup=build_keyboard([('Далее', NEXT_BUTTON)])
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
                CallbackQueryHandler(collect_from_hh, pattern=BACK_BUTTON),
            ],
            DELIVERY_VACS: [
                CallbackQueryHandler(recieve_vacancies, pattern=FIND_BUTTON),
                CallbackQueryHandler(retrieve_vacancies, pattern=NEXT_BUTTON),
                CallbackQueryHandler(collect_from_hh, pattern=BACK_BUTTON),
            ],
            END_ROUTES: [
                CallbackQueryHandler(menu, pattern=BACK_BUTTON),
            ]
        },
        fallbacks=[CommandHandler('done', done)],
    )
