import aiohttp
import asyncio
from prefect import get_run_logger


async def _get_using_aiohttp(session, url):
    logger = get_run_logger()
    async with session.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://jumpit.saramin.co.kr/",
        },
    ) as response:
        res = await response.text()
        logger.info(f"Fetched data from {url}")
        return res


async def fetch(urls: list[str]) -> list:
    logger = get_run_logger()
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            *[_get_using_aiohttp(session, url) for url in urls]
        )
        logger.info(f"Fetched data from {len(urls)} URLs")
        return results
