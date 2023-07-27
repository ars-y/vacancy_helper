import re


TAG_PATTERN: re.Pattern = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def remove_tags_from_text(string: str) -> list:
    """Принимает список строк, в которых убирает html теги."""
    return re.sub(TAG_PATTERN, '', string)


def add_carry(strings: list) -> None:
    for i in range(len(strings) - 1):
        if ':' in strings[i] or ';' in strings[i]:
            strings[i] += '\n-'
        elif '.' in strings[i]:
            strings[i] += '\n\n'


def remove_empty_elements(strings: list) -> list:
    return [string for string in strings if string != '']


def process_text(strings: str) -> str:
    """
    Текст разбивается на строки с добавочными списковыми символами,
    убираются все html теги, если они присутствуют.
    """
    if not strings:
        return

    strings: list = strings.split()

    for i in range(len(strings)):
        _match = re.search(TAG_PATTERN, strings[i])
        if _match:
            strings[i] = remove_tags_from_text(strings[i])

    strings: list = remove_empty_elements(strings)
    add_carry(strings)

    return ' '.join(strings)
