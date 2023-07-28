import aiohttp
import asyncio
import datetime as dt
import requests
import shelve

import db
from exceptions import URLValueException
from processors import is_correct_url


class BaseVacancyCollector:
    """Base model for vacancy collectors."""

    def __init__(
        self,
        url: str,
        endpoint: str | None = None,
        params: dict | None = None,
        filters: set | None = None
    ) -> None:
        if not is_correct_url(url):
            raise URLValueException(url)

        self._url = url
        self._endpoint = endpoint
        self._params = params
        self._filters = filters

        self._db_file: str | None = None
        self._max_age: int | None = None
        self._prepare_collector()

    def _prepare_collector(self) -> None:
        """
        Creating database for vacancies.
        Set values for collector attribute.
        """
        if not self._db_is_exists():
            self._create_db()

        attribute_setters: tuple = (
            '_set_db_filename',
            '_set_max_age',
        )

        for attr_name in attribute_setters:
            setter = getattr(self, attr_name)
            setter()

    def _set_db_filename(self) -> None:
        """Set database file name."""
        self._db_file = db.get_db_filename()

    def _set_max_age(self) -> None:
        """Set storage time limit for vacancy id."""
        self._max_age = db.get_expired_time()

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

    def save(self, vacancies_id: list) -> None:
        """Save vacancy id in db with timestamp."""
        with shelve.open(self._db_file) as vdb:
            for vid in vacancies_id:
                if vid not in vdb:
                    current_time = dt.datetime.now()
                    vdb[vid] = dt.datetime.timestamp(current_time)

    def load(self) -> set:
        """Loading set of vacancies id. Remove id if expired."""
        vacancies_id: set = {}
        time_delta = dt.timedelta(self._max_age)
        expired_ids: list = []

        with shelve.open(self._db_file) as vdb:
            vacancies_id = set(vdb.keys())

            for vid in vdb:
                pub_date = dt.datetime.fromtimestamp(vdb[vid])
                current_date = dt.datetime.now()
                if pub_date + time_delta < current_date:
                    expired_ids.append(vid)

            if expired_ids:
                for vid in expired_ids:
                    vdb.pop(vid)

        return vacancies_id


class VacancyHHCollector(BaseVacancyCollector):
    """
    Model collecting vacancies, select by filters
    and returns a list of VacancyHH objects
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def _make_request(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> list:
        """
        Making async request with session and url.
        Rerutn decodes JSON response.
        """
        async with session.get(url) as response:
            return await response.json()

    async def _async_get_response_data(self, urls: list) -> list:
        """Creating session to make async requests and gather response data."""
        async with aiohttp.ClientSession() as session:
            coros: list = [
                self._make_request(session, url)
                for url in urls
            ]

            return await asyncio.gather(*coros)

    def get_vacancies_id_list(self, url: str) -> list:
        """
        Collecting vacancies id in list
        from all vacancies with specified parameters.
        If response contains more than one page,
        then make async requests for remaining pages.
        """
        response: requests.Response = requests.get(url)
        data = response.json()

        items: list = self._drain_response_data(data.get('items'))
        vacancies_id: list = [item.get('id') for item in items]

        current_page: int = data.get('page', 0)
        total_pages: int = data.get('pages', 0)

        if total_pages > current_page:
            urls: list = [
                url + '&page=%d' % page_num
                for page_num in range(1, total_pages)
            ]

            dataset: list = asyncio.run(self._async_get_response_data(urls))

            for data in dataset:
                if 'items' in data:
                    items: list = self._drain_response_data(data.get('items'))
                    vacancies_id += [item.get('id') for item in items]

        return vacancies_id

    def _drain_response_data(self, items: list) -> list:
        """Filtering response data items."""
        processed_items: list = []

        for item in items:
            experience: str = item.get('experience').get('id')
            employment: str = item.get('employment').get('id')

            if (
                    experience not in self._filters
                    and employment not in self._filters
            ):
                processed_items.append(item)

        return processed_items

    def run(self):
        """Start collecting vacancies."""
        request_url: str = self.make_request_url_with_params()
        vacancies_id: list = self.get_vacancies_id_list(request_url)
        pass
