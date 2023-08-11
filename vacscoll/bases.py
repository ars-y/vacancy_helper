import asyncio

from .db import VIDStorage
from .exceptions import URLValueException
from .processors import TextProcessor
from .utils import make_request


class BaseVacancyCollector:
    """Base model for vacancy collectors."""

    def __init__(
        self,
        url: str,
        endpoint: str | None = None,
        params: dict | None = None,
        filters: set | None = None
    ) -> None:
        if not TextProcessor.is_correct_url(url):
            raise URLValueException(
                'initial url \'%s\' is invalid' % url
            )

        self._url = url
        self._endpoint = endpoint
        self._params = params or {}
        self._filters = filters or set()

        self._storage = VIDStorage()

    def _sift_vacancies(self, vacancies: list) -> list:
        """Sift vacancies to leave new ones. New vacancies save in database."""
        old_vacancies: set = self._storage.load()
        new_vacancies: list = [
            vac for vac in vacancies if vac.id not in old_vacancies
        ]
        self._storage.save(vacancies)
        return new_vacancies

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

        if not endpoint and not params:
            return request_url

        if not request_url.endswith('/'):
            request_url += '/'

        request_url += endpoint

        params_string: list = [
            k + '=' + params[k]
            for k in params
        ]

        if params_string:
            request_url += '?'

        return request_url + '&'.join(params_string)

    async def get_response_data(
        self,
        urls: list,
        delay: float | int = 0
    ) -> list:
        """
        Create tasks with delay to make requests.
        Return list of decode JSON response data.
        """
        tasks: list = []
        for url in urls:
            tasks.append(
                asyncio.create_task(make_request(url))
            )
            await asyncio.sleep(delay)

        return await asyncio.gather(*tasks)
