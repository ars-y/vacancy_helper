import re


TAG_PATTERN: re.Pattern = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def remove_tags_from_text(string: str) -> list:
    """Remove html tags from string."""
    return re.sub(TAG_PATTERN, '', string)


def add_carry(strings: list) -> None:
    """
    Replace ':' and ';' with hypen bullet.
    Add extra carry after dot.
    """
    for i in range(len(strings) - 1):
        if ':' in strings[i] or ';' in strings[i]:
            strings[i] += '\n-'
        elif '.' in strings[i]:
            strings[i] += '\n\n'


def remove_empty_elements(strings: list) -> list:
    return [string for string in strings if string != '']


def process_text(strings: str) -> str:
    """
    Cleaning html tags from input strings if exists.
    Additing bullet and carry characters.
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


def is_correct_url(url: str) -> bool:
    """Check url is correct."""
    url_patter = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    return re.match(url_patter, url) is not None
