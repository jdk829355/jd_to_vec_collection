from datetime import datetime

from sqlalchemy import UUID, Column, Date, String
from pgvector.sqlalchemy import Vector

from plugins.db.database import Base

class Announcement(Base):
    __tablename__ = "ANNOUNCEMENTS"

    id = Column(UUID, primary_key=True, index=True)
    title = Column(String, index=True)
    created_at = Column(Date, default=datetime.utcnow)
    url = Column(String, unique=True, index=True)
    summary = Column(String)
    title_embedding = Column(Vector())