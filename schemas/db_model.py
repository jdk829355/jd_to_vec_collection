from datetime import datetime

from sqlalchemy import UUID, Column, Date, ForeignKey, String
from pgvector.sqlalchemy import Vector

from plugins.db.database import Base

class Announcement(Base):
    __tablename__ = "ANNOUNCEMENTS"

    id = Column(UUID, primary_key=True, index=True)
    title = Column(String, index=True)
    created_at = Column(Date, default=datetime.utcnow)
    url = Column(String, unique=True, index=True)
    summary = Column(String)

class Requirements(Base):
    __tablename__ = "REQUIREMENTS"

    name = Column(String, primary_key=True, unique=True)
    created_at = Column(Date, default=datetime.now())

class AnnouncementRequirement(Base):
    __tablename__ = "ANNOUNCEMENT_REQUIREMENTS"

    announcement_id = Column(
        UUID, 
        ForeignKey('ANNOUNCEMENTS.id', ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True)
    requirement_name = Column(String, ForeignKey('REQUIREMENTS.name', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

if __name__ == "__main__":
    from plugins.db.database import engine
    Base.metadata.create_all(bind=engine)