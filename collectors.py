import requests
import shelve

import db


class BaseVacancyCollector:
    """Base model for vacancy collectors."""

    def __init__(self, url: str, params: dict) -> None:
        self._url = url
        self._params = params

        self._db_file: str | None = None

    def _set_db_filename(self) -> None:
        self._db_file = db.get_db_filename()

    def _create_db(self):
        """Create DB."""
        db.create_db()

    def _db_is_exists(self) -> bool:
        """Check for db is already exist."""
        if not self._db_file:
            self._set_db_filename()

        return db.file_is_exists(self._db_file)
    
    def run(self):
        if not self._db_is_exists():
            self._create_db()
        

class VacancyHHCollector(BaseVacancyCollector):
    """
    Model collecting vacancies, select by filters
    and returns a list of VacancyHH objects
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self):
        """Start collecting vacancies."""
