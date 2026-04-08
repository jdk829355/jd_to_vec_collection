import asyncio

from plugins.crawler.http_fetch import fetch
from bs4 import BeautifulSoup
import logging

from schemas.announcement_schema import AnnouncementSchema

logger = logging.getLogger(__name__)

def get_section_content(soup, section_name):
    # 원하는 섹션명(예: "주요업무")을 가진 <dt> 태그 찾기
    dt_tag = soup.find('dt', string=section_name)
    
    if dt_tag:
        # <dt> 태그 바로 다음에 오는 <dd> 태그 찾기
        dd_tag = dt_tag.find_next_sibling('dd')
        if dd_tag:
            # <dd> 태그 내부에 있는 <pre> 태그의 텍스트 추출 (줄바꿈 원형 유지)
            pre_tag = dd_tag.find('pre')
            if pre_tag:
                return pre_tag.get_text(strip=True)
            else:
                # pre 태그가 없을 경우를 대비하여 <dd> 텍스트 전체 추출
                return dd_tag.get_text(separator='\n', strip=True)
                
    return "해당 내용을 찾을 수 없습니다."

async def parse_content(url: str, last_modified: str) -> AnnouncementSchema:
    html_data = await fetch([url])
    html_data = html_data[0]
    soup = BeautifulSoup(html_data, 'html.parser')
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    content = "주요업무: " + get_section_content(soup, "주요업무")
    content += "\n\n" + "자격요건: " + get_section_content(soup, "자격요건")
    content += "\n\n" + "우대사항: " + get_section_content(soup, "우대사항")

    company_tag = soup.select_one('a.name span')
    company_name = company_tag.get_text(strip=True) if company_tag else "회사명 없음"

    announcement = AnnouncementSchema(
        title=title,
        content=content,
        date=last_modified,
        url=url,
        company_name=company_name,
    )
    logger.info(f"Parsed content from {url}")
    return announcement


if __name__ == "__main__":
    url = "https://jumpit.saramin.co.kr/position/53315032"
    last_modified = "2024-06-01"
    announcement = asyncio.run(parse_content(url, last_modified))
    print(announcement)