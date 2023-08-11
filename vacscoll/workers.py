import re

from .collectors import VacancyHHCollector
from .constants import HH_REGION_RU, HH_URL
from .db import VIDStorage


async def get_vacs(
    src_name: str,
    keywords: str,
    area: str | None = None
) -> list:
    """Getting vacancies objects list from job aggregators API."""
    if src_name == 'hh':
        keywords: str = '+'.join(keywords.split())
        params: dict = {
            'text': keywords,
            'per_page': '100',
            'no_magic': 'true',
        }
        endpoint: str = 'vacancies'

        if area:
            params.update({'area': area})

        vacscoll = VacancyHHCollector(HH_URL, endpoint, params)
        return await vacscoll.run()


async def get_areas(src_name: str, city: str) -> str | None:
    """Return area ID if user has entered an existing one."""
    selector: dict = {
        'hh': recieve_hh_areas,
    }
    areas: dict = await selector[src_name]()
    return checking_area(city.lower(), areas)


async def recieve_hh_areas() -> dict:
    """Recieve areas dict from HH API."""
    endpoint: str = 'areas/' + HH_REGION_RU
    vacscoll = VacancyHHCollector(HH_URL)
    url = vacscoll.make_request_url_with_params(endpoint)
    dataset = await vacscoll.get_response_data([url])
    return unpacking(dict(*dataset).get('areas'))


def unpacking(areas: list) -> dict:
    """Get nested cities from regions."""
    def dfs(regions: list) -> None:
        for region in regions:
            _id = region.get('id')
            _name = region.get('name')
            total_regions[_id] = _name
            areas = region.get('areas')
            if areas:
                dfs(areas)

    total_regions: dict = {}
    dfs(areas)
    return total_regions


def checking_area(city: str, areas: dict) -> str | None:
    """
    Checking user entered city is exists.
    If city is exists return its ID."""
    for _id, area in areas.items():
        if re.search(city, area.lower()):
            return _id


def remove_unrecieved(vacancies: list) -> None:
    """Remove unrecieved vacancies ids from db."""
    VIDStorage().clean([vac.id for vac in vacancies])
