import requests
import shelve

from db import create_db
from settings.globconf import DB_NAME


class BaseVacancyCollector:
    """Base model for vacancy collectors."""
    
    def __init__(self, url: str, params: dict) -> None:
        self._url = url
        self._params = params
        self._db_file = DB_NAME
    
    def _create_db(self):
        """Create DB."""
        create_db()

    def _db_is_exists(self) -> bool:
        """Check for db is already exist."""
    
    def run(self):
        ...


class VacancyHHCollector(BaseVacancyCollector):
    """
    Model collecting vacancies, select by filters
    and returns a list of VacancyHH objects
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def run(self):
        """Start collecting vacancies."""
        if not self._db_is_exists():
            self._create_db()