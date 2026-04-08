from typing import List

from pydantic import BaseModel, Field

class AnnouncementSchema(BaseModel):
    title: str = Field(..., description="The title of the announcement")
    content: str = Field(..., description="The content of the announcement")
    date: str = Field(..., description="The date of the announcement in YYYY-MM-DD format")
    url: str = Field(..., description="The URL of the announcement")
    company_name: str = Field(..., description="The name of the company posting the announcement")


class LLMAnnouncementResponse(BaseModel):
    position_name: str = Field(..., description="The name of the position")
    summary: str = Field(..., description="A summary of the announcement")
    requirements: List[str] = Field(..., description="The requirements for the position")

class AiAnnouncementResponse(BaseModel):
    position_name: str = Field(..., description="The name of the position")
    summary: str = Field(..., description="A summary of the announcement")
    requirements: List[str] = Field(..., description="The requirements for the position")
    title_embedding: List[float] = Field(..., description="The embedding vector for the announcement title")