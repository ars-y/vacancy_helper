import re


TAG_PATTERN: re.Pattern = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def remove_tags_from_text(string: str) -> list:
    """Принимает список строк, в которых убирает html теги."""
    return re.sub(TAG_PATTERN, '', string)


def add_marks(strings: list) -> None:
    """
    Добавляет символы '-' перед каждой строкой,
    ';' в конце каждой строки, кроме последней.
    Последняя строка получает '.'
    
    Input: ['s0', 's1', 's2']
    Output: ['-s0;', '-s1;', '-s2.']    
    """
    n: int = len(strings)

    for i in range(n):
        strings[i] = '- ' + strings[i]
        strings[i] += ';' if i < n - 1 else '.'


def process_text(strings: str) -> str:
    """
    Текст разбивается на строки с добавочными списковыми символами,
    убираются все html теги, если они присутствуют.
    """
    if not strings:
        return

    strings: list = strings.split('. ')
    add_marks(strings)

    for i in range(len(strings)):
        _match = re.search(TAG_PATTERN, strings[i])
        if _match:
            strings[i] = remove_tags_from_text(strings[i])
    
    return '\n'.join(strings)
