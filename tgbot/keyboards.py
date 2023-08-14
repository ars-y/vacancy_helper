from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def url_keyboard(text: str, url: str) -> InlineKeyboardMarkup:
    """Make url button under vacancy info."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text, url=url)]]
    )


def build_keyboard(button_rows: list[tuple]) -> InlineKeyboardMarkup:
    """
    One column keyboard constructor.
    Args:
        list of tuple: (label text, callback_data)
    """
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text, callback_data=callback_data)]
            for text, callback_data in button_rows
        ]
    )
