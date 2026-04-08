from datetime import datetime

from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
import logging
from plugins.db.database import DbSession
from schemas.announcement_schema import AnnouncementSchema, AiAnnouncementResponse
from uuid import uuid4
from schemas.db_model import Announcement, AnnouncementRequirement, Requirements

load_dotenv()

def get_last_modified_standard() -> datetime|None:
    session = DbSession()
    last_modified = session.query(Announcement.created_at).order_by(Announcement.created_at.desc()).first()
    session.close()
    if last_modified:
        res = datetime.combine(last_modified[0], datetime.min.time())
        return res
    else:
        return None

def remove_existing_url(url_and_last_mods: list[tuple[str, datetime]]) -> list[tuple[str, datetime]]:
    session = DbSession()
    existing_urls = session.query(Announcement.url).filter(Announcement.url.in_( [url for url, _ in url_and_last_mods] )).all()
    existing_urls = {url for (url,) in existing_urls}
    session.close()
    return [url_and_last_mod for url_and_last_mod in url_and_last_mods if url_and_last_mod[0] not in existing_urls]

def insert_announcements(data: list[tuple[AnnouncementSchema, AiAnnouncementResponse]]):
    logger = logging.getLogger(__name__)
    db = DbSession()

    data_to_insert = []
    requirement_to_insert = []
    announcement_requirement_to_insert = []
    for announcement_schema, ai_response in data:
        announcement_id = uuid4()
        data_to_insert.append(
            {
                "id": announcement_id,
                "title": announcement_schema.title,
                "created_at": announcement_schema.date,
                "url": announcement_schema.url,
                "summary": ai_response.summary,
                "title_embedding": ai_response.title_embedding,
            }
        )
        for requirement in ai_response.requirements:
            announcement_requirement_to_insert.append(
                {
                    "announcement_id": announcement_id,
                    "requirement_name": requirement
                }
            )

            requirement_to_insert.append(
                {
                    "name": requirement
                }
            )
    try:
        stmt = insert(Announcement).values(data_to_insert)
        stmt = stmt.on_conflict_do_nothing(index_elements=['id'])
        db.execute(stmt)

        stmt = insert(Requirements).values(requirement_to_insert)
        stmt = stmt.on_conflict_do_nothing(index_elements=['name'])
        db.execute(stmt)

        stmt = insert(AnnouncementRequirement).values(announcement_requirement_to_insert)
        stmt = stmt.on_conflict_do_nothing(index_elements=['announcement_id', 'requirement_name'])
        db.execute(stmt)

        logger.info(f"PostgreSQL 삽입 성공: {len(data_to_insert)} 개의 포스트 삽입 시도")


        db.commit()
    except Exception as e:
        logger.error(f"PostgreSQL 삽입 실패: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_dotenv()
    announcement_schema = AnnouncementSchema(
        title="백엔드 개발자 모집",
        content="주요업무: 웹 서비스 개발 및 유지보수\n자격요건: Python, Django 경험자\n우대사항: AWS 경험자",
        date="2024-06-01",
        url="https://example.com/job/12345",
        company_name="예시회사",
    )
    ai_announcement_response = AiAnnouncementResponse(
        position_name="백엔드 개발자",
        summary="예시회사는 혁신적인 IT 솔루션을 제공하는 선도적인 기업입니다. 백엔드 개발자로서 웹 서비스 개발 및 유지보수를 담당하게 됩니다. 주요 업무는 Python과 Django를 활용한 웹 서비스 개발이며, AWS 경험이 있는 지원자는 우대됩니다. 예시회사는 직원들의 성장과 발전을 지원하는 환경을 제공하며, 함께 혁신을 이끌어갈 인재를 찾고 있습니다.",
        requirements=["Python", "Django", "AWS"],
        title_embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
    )
    insert_announcements([(announcement_schema, ai_announcement_response)])