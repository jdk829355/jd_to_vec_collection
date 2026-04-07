import asyncio
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta, timezone
from http_fetch import fetch




async def get_urls(last_mod_standard: datetime|None=None) -> list[str]:
    if last_mod_standard is not None:
        last_mod_standard = last_mod_standard.replace(tzinfo=timezone(timedelta(hours=9))) # 한국 시간대에 맞게 설정

    sitemap_url = "https://jumpit.saramin.co.kr/sitemap/sitemap_position_view_1.xml"
    sitemap_data = await fetch([sitemap_url])
    sitemap_data = sitemap_data[0]
    NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'

    root = ET.fromstring(sitemap_data)
    url_dates = root.findall(f"{NS}url")
    urls = []
    for url_date in url_dates:
        url = url_date.find(f"{NS}loc") if url_date.find(f"{NS}loc") is not None else None
        lastmod = url_date.find(f"{NS}lastmod") if url_date.find(f"{NS}lastmod") is not None else None

        if url is not None and lastmod is not None:
            url, lastmod = url.text, lastmod.text # type: ignore
            lastmod = datetime.strptime(lastmod, "%Y-%m-%dT%H:%M:%S%z")
            if last_mod_standard is None or lastmod > last_mod_standard:
                urls.append(url)
    return urls


if __name__ == "__main__":
    last_mod = datetime(2026, 4, 6)
    print(asyncio.run(get_urls(last_mod), ))
