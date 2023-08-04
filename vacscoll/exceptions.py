class URLValueException(ValueError):
    """Exception for URl is not correct."""

    def __init__(self, *args: tuple) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        if not self.args:
            return 'initial url is invalid'

        return super().__str__()


class VacancyNoneTypeException(ValueError):
    """Exception for Vacancy object is None."""

    def __init__(self, *args: tuple) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        if not self.args:
            return 'Vacancy instance didn\'t reach source'

        return super().__str__()
