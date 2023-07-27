import requests
import shelve

import db


class BaseVacancyCollector:
    """Base model for vacancy collectors."""

    def __init__(
        self,
        url: str,
        endpoint: str | None = None,
        params: dict | None = None,
        filters: list | None = None
    ) -> None:
        self._url = url
        self._endpoint = endpoint
        self._params = params
        self._filters = filters

        self._db_file: str | None = None
        self._prepare_collector()

    def _prepare_collector(self) -> None:
        if not self._db_is_exists():
            self._create_db()

    def _set_db_filename(self) -> None:
        self._db_file = db.get_db_filename()

    def _create_db(self) -> None:
        """Creating DB."""
        db.create_db()

    def _db_is_exists(self) -> bool:
        """Check for db is already exist."""
        if not self._db_file:
            self._set_db_filename()

        return db.file_is_exists(self._db_file)

    def make_request_url_with_params(self) -> str:
        """
        With url, endpoint and parameters making
        request url.
        """
        request_url: str = self._url
        if not self._params or not self._endpoint:
            return request_url

        if not request_url.endswith('/'):
            request_url += '/'

        request_url += self._endpoint + '?'

        params_string: list = [
            k + '=' + self._params[k]
            for k in self._params
        ]

        return request_url + '&'.join(params_string)


class VacancyHHCollector(BaseVacancyCollector):
    """
    Model collecting vacancies, select by filters
    and returns a list of VacancyHH objects
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def get_vacancies_id_list(self, url: str) -> list:
        """
        Collecting vacancies id in list
        from all vacancies with specified parameters.
        """
        response: requests.Response = requests.get(url)
        data = response.json()

        vacancies_id: list = []

        current_page: int = data.get('page', 0)
        total_pages: int = data.get('pages', 0)

        while current_page <= total_pages:
            items: list = data.get('items')
            for item in items:
                vacancy_id: str = item.get('id')
                vacancies_id.append(vacancy_id)
            
            current_page += 1
            url += '&page=%d' % current_page
            response = requests.get(url)
            data = response.json()

        return vacancies_id

    def run(self):
        """Start collecting vacancies."""
        request_url: str = self.make_request_url_with_params()
        vacancies_id: list = self.get_vacancies_id_list(request_url)
