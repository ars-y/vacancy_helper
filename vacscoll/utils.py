import aiohttp


async def make_request(url: str) -> list:
    """
    Making async request with session and url.
    Rerutn decodes JSON response.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
