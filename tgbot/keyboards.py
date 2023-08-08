from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .constants import ALL_BUTTON, BACK_BUTTON, HH_BUTTON, NEXT_BUTTON


def select_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to choosing vacancy aggregator."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Подбор с hh.ru', callback_data=HH_BUTTON)],
            [InlineKeyboardButton('Подбор всех', callback_data=ALL_BUTTON)],
        ]
    )


def back_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to back at main menu."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton('Назад', callback_data=BACK_BUTTON)]]
    )


def next_keyboard() -> InlineKeyboardMarkup:
    """Show next vacancies keyboard."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton('Далее', callback_data=NEXT_BUTTON)]]
    )


def url_keyboard(url: str) -> InlineKeyboardMarkup:
    """Make url button under vacancy info."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton('Подробнее', url=url)]]
    )
