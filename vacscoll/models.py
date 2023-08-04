from .exceptions import VacancyNoneTypeException
from .processors import TextProcessor


class VacancyHH:
    """Model for summary hh vacancy info."""

    def __init__(self, item: dict) -> None:
        if not item:
            raise VacancyNoneTypeException()

        self._vacancy: dict = item
        self._vacancy_id: int | None = None
        self._name: str | None = None
        self._employer: str | None = None
        self._description: str | None = None
        self._employment: str | None = None
        self._experience: str | None = None

        self._vacancy_url: str | None = self._get_vacancy_url()

        self.__fill_vacancy()

    def _set_vacancy_id(self) -> None:
        self._vacancy_id = self._vacancy.get('id', None)

    def _set_name(self) -> None:
        self._name = self._vacancy.get('name', None)

    def _set_employer(self) -> None:
        employer_info: dict = self._vacancy.get('employer', None)

        if not employer_info:
            self._employer = None
            return

        self._employer = employer_info.get('name', None)

    def _set_description(self) -> tuple:
        text_processor: TextProcessor = TextProcessor()

        description: dict = self._vacancy.get('description', None)
        if not description:
            return

        self._description = text_processor.cleaning_data(description)

    def _set_employment(self) -> None:
        employment: dict = self._vacancy.get('employment', None)
        if not employment:
            self._employment = None
            return

        self._employment = employment.get('name', None)

    def _set_experience(self) -> None:
        experience: dict = self._vacancy.get('experience', None)
        if not experience:
            self._experience = None
            return

        self._experience = experience.get('name', None)

    def _get_vacancy_url(self) -> str:
        return self._vacancy.get('alternate_url', None)

    def __fill_vacancy(self) -> None:
        attribute_setters: tuple = (
            '_set_vacancy_id',
            '_set_name',
            '_set_employer',
            '_set_description',
            '_set_employment',
            '_set_experience',
        )

        for attr_name in attribute_setters:
            setter = getattr(self, attr_name)
            setter()

    def __str__(self) -> str:
        summary_description: str = (
            f'{self._name}\n'
            f'{self._employment}\n'
            f'Компания: {self._employer}\n\n'
            f'Описание:\n{self._description}\n\n'
            f'Вакансия: {self._vacancy_url}'
        )

        return summary_description

    def __repr__(self) -> str:
        return f'{type(self).__name__}(\'{self._vacancy_id}\')'
