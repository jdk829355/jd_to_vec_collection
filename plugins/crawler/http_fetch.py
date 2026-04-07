import aiohttp
import asyncio
import logging

async def _get_using_aiohttp(session, url):
    logger = logging.getLogger(__name__)
    async with session.get(url) as response:
        res = await response.text()
        logger.info(f"Fetched data from {url}")
        return res
        

async def fetch(urls: list[str]) -> list:
    logger = logging.getLogger(__name__)
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[_get_using_aiohttp(session, url) for url in urls])
        logger.info(f"Fetched data from {len(urls)} URLs")  
        return results