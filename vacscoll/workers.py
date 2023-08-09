from .collectors import VacancyHHCollector


async def get_vacs(src_name: str, keywords: str) -> list:
    """Getting vacancies objects list from job aggregators API."""
    if src_name == 'hh':
        text_param: str = '+'.join(keywords.split())
        params: dict = {
            'text': text_param,
            'per_page': '100',
            'no_magic': 'true',
        }
        url: str = 'https://api.hh.ru'
        endpoint: str = 'vacancies'

        vacscoll = VacancyHHCollector(url, endpoint, params)
        return await vacscoll.run()
