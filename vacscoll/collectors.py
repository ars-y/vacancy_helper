import asyncio

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

    async def _extract_rest_vacancies(
        self,
        url: str,
        total_pages: int
    ) -> list:
        """Extract vacancies from rest pages."""
        urls: list = [
            url + '&page=%d' % page_num
            for page_num in range(1, total_pages)
        ]

        dataset = await self._get_response_data(urls, self._delay)

        return [
            item for data in dataset
            for item in data.get('items')
        ]

    async def _recieve_vacancies(self, url: str) -> list:
        """
        Collecting vacancy objects in list
        from all vacancies with specified parameters.
        If response contains more than one page,
        then make async requests for remaining pages.
        """

        dataset: list = await asyncio.gather(
            asyncio.create_task(self._make_request(url))
        )

        data: dict = dict(*dataset)

        vacancies_items: list = data.get('items')

        current_page: int = data.get('page', 0)
        total_pages: int = data.get('pages', 0)

        if current_page < total_pages:
            items: list = await asyncio.gather(
                asyncio.create_task(
                    self._extract_rest_vacancies(url, total_pages)
                )
            )
            vacancies_items.extend(*items)

        if self._filters:
            vacancies_items: list = self._apply_filters(vacancies_items)

        return [VacancyHH(item) for item in vacancies_items]

    async def run(self) -> list:
        """Collecting vacancies and return sift vacancy objects."""
        request_url: str = self.make_request_url_with_params()
        vacancies: list = await self._recieve_vacancies(request_url)
        return self._sift_vacancies(vacancies)
