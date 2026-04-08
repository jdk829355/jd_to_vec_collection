from datetime import datetime
import time
from typing import List

from dotenv import load_dotenv
from prefect import task, flow, unmapped, get_run_logger
from prefect.task_runners import ThreadPoolTaskRunner

from schemas.announcement_schema import (
    AiAnnouncementResponse,
    AnnouncementSchema,
    LLMAnnouncementResponse,
)
from more_itertools import chunked
import asyncio


@task(name="get last modified standard")
def get_last_modified_standard() -> datetime | None:
    logger = get_run_logger()
    from plugins.db.db_service import get_last_modified_standard

    last_mod_standard = get_last_modified_standard()
    logger.info(f"Last modified standard: {last_mod_standard}")
    return last_mod_standard


@task(name="collect urls from sitemap")
async def collect_urls_from_sitemap(last_mod_standard: datetime | None = None):
    logger = get_run_logger()
    from plugins.crawler.sitemap_parser import get_urls

    urls = await get_urls(last_mod_standard)
    logger.info(f"Collected {len(urls)} URLs from sitemap")  # type: ignore
    return urls


@task(name="filter existing urls")
def filter_existing_urls(
    url_and_last_mods: list[tuple[str, datetime]],
) -> list[tuple[str, datetime]]:
    logger = get_run_logger()
    from plugins.db.db_service import remove_existing_url

    filtered_urls = remove_existing_url(url_and_last_mods)
    logger.info(f"Filtered URLs. {len(filtered_urls)} URLs remain after filtering")  # type: ignore
    return filtered_urls


@task(name="parse content from url", retries=2, retry_delay_seconds=5)
async def parse_content_from_url(
    url_and_last_mod: tuple[str, datetime],
) -> AnnouncementSchema:
    url, last_modified = url_and_last_mod
    logger = get_run_logger()
    from plugins.crawler.content_parser import parse_content

    announcement = await parse_content(url, last_modified.isoformat())
    logger.info(f"Parsed content from {url}")
    return announcement


@task(name="get ai response", retries=2, retry_delay_seconds=5)
def get_ai_response(
    announcement: AnnouncementSchema,
) -> tuple[AnnouncementSchema, AiAnnouncementResponse]:
    logger = get_run_logger()
    from plugins.position_extractor.extractor import extract_position_and_summary
    from plugins.position_extractor.skill_embedder import embed_skill

    ai_announcement_response: LLMAnnouncementResponse = extract_position_and_summary(
        announcement
    )
    title_embedding: List[float] = embed_skill(announcement.title)

    logger.info(f"Got AI response for announcement: {announcement.title}")
    return announcement, AiAnnouncementResponse(
        position_name=ai_announcement_response.position_name,
        summary=ai_announcement_response.summary,
        requirements=ai_announcement_response.requirements,
        title_embedding=title_embedding,
    )


@task(name="insert to db")
def insert_to_db(
    announcement_and_ai_response: list[
        tuple[AnnouncementSchema, AiAnnouncementResponse]
    ],
):
    logger = get_run_logger()
    from plugins.db.db_service import insert_announcements

    insert_announcements(announcement_and_ai_response)
    logger.info("Data inserted into database!")


@flow(
    name="data collection pipeline",
    task_runner=ThreadPoolTaskRunner(max_workers=10), # type: ignore
    log_prints=True,
)  # type: ignore
async def data_collection_pipeline():
    logger = get_run_logger()
    last_mod_standard = get_last_modified_standard()
    url_and_last_mods = await collect_urls_from_sitemap(last_mod_standard)
    filtered_urls = filter_existing_urls(url_and_last_mods)

    for batch in chunked(filtered_urls, 10):
        content_results = parse_content_from_url.map(batch)
        ai_response_results = get_ai_response.map(content_results)
        list_to_insert = []
        for announcement_and_ai_response in ai_response_results:
            try:
                res = announcement_and_ai_response.result()
                if res:
                    list_to_insert.append(res)
            except Exception as e:
                logger.error(f"Error processing announcement: {e}")
        insert_to_db(list_to_insert)
        await asyncio.sleep(1)  # API rate limit 방지 위해 1초 대기


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(data_collection_pipeline())
