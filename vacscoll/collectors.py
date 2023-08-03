import asyncio
import requests

from .bases import BaseVacancyCollector
from .constants import HH_REQUEST_DELAY
from .models import VacancyHH


class VacancyHHCollector(BaseVacancyCollector):
    """
    Model collecting vacancies, select by filters
    and returns a list of VacancyHH objects
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._delay: float | int = HH_REQUEST_DELAY

    def _apply_filters(self, items: list) -> list:
        """Filtering vacancies."""
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

    def _extract_rest_vacancies(self, url: str, total_pages: int) -> list:
        """Extract vacancies id from rest pages."""
        urls: list = [
            url + '&page=%d' % page_num
            for page_num in range(1, total_pages)
        ]

        dataset: list = []

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            dataset = self._sync_get_response_data(urls)
        else:
            dataset = asyncio.run(
                self._get_response_data(urls, self._delay)
            )

        return [
            item for data in dataset
            for item in data.get('items')
        ]

    def _get_vacancies_id(self, url: str) -> list:
        """
        Collecting vacancies id in list
        from all vacancies with specified parameters.
        If response contains more than one page,
        then make async requests for remaining pages.
        """
        response: requests.Response = requests.get(url)
        data = response.json()

        vacancies_items: list = data.get('items')

        current_page: int = data.get('page', 0)
        total_pages: int = data.get('pages', 0)

        if current_page < total_pages:
            vacancies_items.extend(
                self._extract_rest_vacancies(url, total_pages)
            )

        if self._filters:
            vacancies_items: list = self._apply_filters(vacancies_items)

        vacancies_id: list = [item.get('id') for item in vacancies_items]

        return vacancies_id

    def recieve_vacancies(self, vacancies_id: list) -> list:
        """
        Recieve Vacancy ojects.
        Method consruct requests for async get response data
        to initial Vacancy object and append it in list.
        """
        endpoint: str = 'vacancies/'
        params: dict = {'host': 'hh.ru'}
        request_urls: list = [
            self.make_request_url_with_params(endpoint + vid, params)
            for vid in vacancies_id
        ]

        dataset: list = asyncio.run(
            self._get_response_data(request_urls, self._delay)
        )

        return [VacancyHH(item) for item in dataset]

    def run(self) -> list:
        """Collecting vacancies and return sift vacancies id."""
        request_url: str = self.make_request_url_with_params()
        vacancies_id: list = self._get_vacancies_id(request_url)
        return self._sift_vacancies(vacancies_id)
