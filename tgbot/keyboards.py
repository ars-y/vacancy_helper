from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .constants import HH_BUTTON


def select_keyboard() -> InlineKeyboardMarkup:
    """Keyboard to choosing vacancy aggregator."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Подбор с hh.ru', callback_data=HH_BUTTON)],
        ]
    )


def move_to_keyboard(text: str, callback_data: str) -> InlineKeyboardMarkup:
    """Make one button with text and callback data."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text, callback_data=callback_data)]]
    )


def url_keyboard(url: str) -> InlineKeyboardMarkup:
    """Make url button under vacancy info."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton('Подробнее', url=url)]]
    )
