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
    vacancy_info: list = [
        f'{vacancy.name}\n',
        f'{vacancy.employment}\n',
    ]

    if vacancy.salary:
        vacancy_info.append('ЗП: ')
        min_bound, max_bound, currency = vacancy.salary
        if min_bound and not max_bound:
            vacancy_info.append(f'от {str(min_bound)} {currency}')
        elif not min_bound and max_bound:
            vacancy_info.append(f'до {str(max_bound)} {currency}')
        else:
            vacancy_info.append(
                f'от {str(min_bound)} до {str(max_bound)} {currency}'
            )
        vacancy_info.append('\n')

    vacancy_info.append(f'Компания: {vacancy.employer}\n\n')
    if vacancy.requirements:
        vacancy_info.append(f'Требования:\n{vacancy.requirements}\n\n')

    if vacancy.responsibility:
        vacancy_info.append(f'Обязанности:\n{vacancy.responsibility}\n')

    return ''.join(vacancy_info)
