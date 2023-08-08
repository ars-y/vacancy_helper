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
        return self._vacancy.get('id', None)

    @property
    def name(self) -> str | None:
        return self._vacancy.get('name', None)

    @property
    def employment(self) -> str | None:
        employment_info: dict = self._vacancy.get('employment', None)
        if not employment_info:
            return

        return employment_info.get('name', None)

    @property
    def employer(self) -> str | None:
        employer_info: dict = self._vacancy.get('employer', None)

        if not employer_info:
            return

        return employer_info.get('name', None)

    @property
    def description(self) -> str | None:
        text_processor: TextProcessor = TextProcessor()

        description: dict = self._vacancy.get('description', None)
        if not description:
            return

        return text_processor.cleaning_data(description)

    @property
    def url(self) -> str | None:
        return self._vacancy.get('alternate_url', None)

    def __str__(self) -> str:
        summary_info: str = (
            f'{self.name}\n'
            f'{self.employment}\n'
            f'Компания: {self.employer}\n\n'
            f'Описание:\n{self.description}\n\n'
            f'Вакансия: {self.url}'
        )

        return summary_info

    def __repr__(self) -> str:
        return f'{type(self).__name__}(\'{self.id}\')'
