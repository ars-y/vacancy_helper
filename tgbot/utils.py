import logging
import sys

from vacscoll.models import VacancyHH


def tokens_is_exists(*args) -> bool:
    """Checking tokens is exists."""
    return all((*args, ))


def check_tokens(*args) -> None:
    """Run checking tokens."""
    logging.info('Checking telegram token')
    if not tokens_is_exists(*args):
        logging.critical(
            'Missing telegram token. Execution of the program is terminated'
        )
        sys.exit()


def format_message(vacancy: VacancyHH) -> str:
    """Construct message with info about vacancy."""
    vacancy_info: str = (
        f'{vacancy.name}\n'
        f'{vacancy.employment}\n'
        f'Компания: {vacancy.employer}\n\n'
    )

    if vacancy.requirements:
        vacancy_info += f'Требования:\n{vacancy.requirements}\n\n'

    if vacancy.responsibility:
        vacancy_info += f'Обязанности:\n{vacancy.responsibility}\n'

    return vacancy_info
