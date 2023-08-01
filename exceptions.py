class URLValueException(ValueError):
    """Exception for URl is not correct."""

    def __init__(self, url: str, *args: object) -> None:
        super().__init__(*args)
        self._url = url

    def __str__(self) -> str:
        if not self.args:
            return 'Initial url \'%s\' is invalid' % self._url

        return super().__str__()


class VacancyNoneTypeException(ValueError):
    """Exception for Vacancy object is None."""
