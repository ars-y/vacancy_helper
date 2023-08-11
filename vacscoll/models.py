from .exceptions import VacancyNoneTypeException
from .processors import TextProcessor


class VacancyHH:
    """Model for summary hh vacancy info."""

    def __init__(self, item: dict) -> None:
        if not item:
            raise VacancyNoneTypeException()

        self._vacancy: dict = item

    @property
    def id(self) -> int | None:
        return self._vacancy.get('id')

    @property
    def name(self) -> str | None:
        return self._vacancy.get('name')

    @property
    def employment(self) -> str:
        employment_info: dict = self._vacancy.get('employment')
        if not employment_info:
            return

        return employment_info.get('name')

    @property
    def employer(self) -> str:
        employer_info: dict = self._vacancy.get('employer')

        if not employer_info:
            return

        return employer_info.get('name')

    @property
    def location(self) -> str | None:
        area: dict = self._vacancy.get('area')
        if not area:
            return

        return area.get('name')

    @property
    def requirements(self) -> str | None:
        text_processor: TextProcessor = TextProcessor()

        snippet: dict = self._vacancy.get('snippet')
        if not snippet:
            return

        requirement = snippet.get('requirement')
        if not requirement:
            return

        return text_processor.cleaning_data(requirement)

    @property
    def responsibility(self) -> str | None:
        text_processor: TextProcessor = TextProcessor()

        snippet: dict = self._vacancy.get('snippet')
        if not snippet:
            return

        responsibilities = snippet.get('responsibility')
        if not responsibilities:
            return

        return text_processor.cleaning_data(responsibilities)

    @property
    def salary(self) -> tuple | None:
        salary_info: dict = self._vacancy.get('salary')
        if not salary_info:
            return

        min_bound = salary_info.get('from')
        max_bound = salary_info.get('to')
        currency = salary_info.get('currency')

        return min_bound, max_bound, currency

    @property
    def url(self) -> str | None:
        return self._vacancy.get('alternate_url')

    def __str__(self) -> str:
        summary_info: str = (
            f'{self.name}\n'
            f'{self.employment}\n'
            f'Компания: {self.employer}\n\n'
            f'Требования:\n{self.requirements}\n\n'
            f'Обязанности:\n{self.responsibility}\n'
        )

        return summary_info

    def __repr__(self) -> str:
        return f'{type(self).__name__}(\'{self.id}\')'
