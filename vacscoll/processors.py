import re

from constants import TAG_PATTERN, URL_PATTERN


TAG_PATTERN: re.Pattern = re.compile(TAG_PATTERN)
URL_PATTERN: re.Pattern = re.compile(URL_PATTERN)


class TextProcessor:
    """Set of text processing methods."""

    def __init__(self) -> None:
        pass

    def cleaning_data(self, strings: str) -> str:
        """
        Cleaning html tags from input strings if exists.
        Additing bullet and carry characters.
        """
        if not strings:
            return

        strings: list = strings.split()

        for i in range(len(strings)):
            _match: re.Match | None = re.search(TAG_PATTERN, strings[i])
            if _match:
                strings[i] = self._remove_tags(strings[i])

        strings: list = self._remove_empty_elements(strings)
        self._add_carry(strings)

        return ' '.join(strings)

    def _add_carry(self, strings: list) -> None:
        """
        Replace ':' and ';' with hypen bullet.
        Add extra carry after dot.
        """
        for i in range(len(strings) - 1):
            if ':' in strings[i] or ';' in strings[i]:
                strings[i] += '\n-'
            elif '.' in strings[i]:
                strings[i] += '\n\n'

    def _remove_tags(self, string: str) -> list:
        """Remove html tags from string."""
        return re.sub(TAG_PATTERN, '', string)

    def _remove_empty_elements(self, strings: list) -> list:
        return [string for string in strings if string != '']

    @staticmethod
    def is_correct_url(url: str) -> bool:
        """Check url is correct."""
        return re.match(URL_PATTERN, url) is not None
