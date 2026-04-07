import logging

from prefect import task, flow

@task(name="collect urls from sitemap")
def collect_data(last_mod_standard=None):
    logger = logging.getLogger(__name__)
    from plugins.crawler.sitemap_parser import get_urls
    urls = get_urls(last_mod_standard)
    logger.info(f"Collected {len(urls)} URLs from sitemap") # type: ignore
    return urls

@task(name="insert to db")
def insert_to_db(announcements):
    print("data collected!")

@flow(name="data collection pipeline", )
def data_collection_pipeline():
    pass

if __name__ == "__main__":
    data_collection_pipeline()