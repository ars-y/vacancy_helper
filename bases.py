import aiohttp
import asyncio
import datetime as dt
import shelve

import db
from exceptions import URLValueException
from managers import EventLimiter
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
        self._filters = filters or set()

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

    def _sift_vacancies(self, vacancies_id: list) -> list:
        """Sift vacancies to leave new ones. New vacancies save in database."""
        old_vacancies: set = self.load()
        new_vacancies: list = [
            vid for vid in vacancies_id if vid not in old_vacancies
        ]
        self.save(new_vacancies)
        return new_vacancies

    async def _async_get_response_data(
        self,
        urls: list,
        delay: float | int
    ) -> list:
        """Create tasks for requests and wait it to complete."""
        limiter: EventLimiter = EventLimiter(delay)
        tasks: list = [
            asyncio.create_task(self._try_make_request(limiter, url))
            for url in urls
        ]
        pending: set = set(tasks)
        while pending:
            done, pending = await asyncio.wait(pending)

        return [task.result() for task in done]

    async def _make_request(self, url: str) -> list:
        """
        Making async request with session and url.
        Rerutn decodes JSON response.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def _try_make_request(self, limiter: EventLimiter, url: str):
        """Waiting release for next request."""
        while True:
            await limiter.wait()
            return await self._make_request(url)

    def make_request_url_with_params(
        self,
        endpoint: str = None,
        params: dict = None
    ) -> str:
        """
        With url, endpoint and parameters making
        request url.
        """
        request_url: str = self._url
        if not endpoint:
            endpoint = self._endpoint

        if not params:
            params = self._params

        if not endpoint or not params:
            return request_url

        if not request_url.endswith('/'):
            request_url += '/'

        request_url += endpoint + '?'

        params_string: list = [
            k + '=' + params[k]
            for k in params
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
