import asyncio
import json

from plugins.crawler.content_parser import parse_content
from schemas.announcement_schema import Announcement, AiAnnouncementResponse
from google.genai import types
import google.genai
from dotenv import load_dotenv
import os


def extract_position_and_summary(announcement: Announcement) -> AiAnnouncementResponse:
    client = google.genai.Client(
        api_key=os.getenv('GEMINI_API_KEY'),
    )

    model = "gemini-2.5-flash-lite"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""
**Role:** 
You are an expert Corporate Technical Recruiter with over 10 years of experience in crafting and analyzing IT job postings.

**Objective:** 
Analyze the following job announcement and extract three key elements: the Job Title (e.g., Frontend Developer, Data Analyst), a concise Job Summary, and the Required Skills.

**CRITICAL CONSTRAINT FOR REQUIRED SKILLS:** 
The extracted required skills MUST ABSOLUTELY be EXACTLY ONE WORD per skill. Each skill must be the exact proper noun of the technology or tech stack itself (e.g., "React", "Python", "Docker"). Do NOT include any descriptive words, phrases, or verbs (e.g., write "JavaScript", NOT "Experience with JavaScript" or "JavaScript frameworks"). 

**Input Job Announcement:**
title: {announcement.title}

{announcement.content}

**Expected Output Format:**
- Job Title: [Extracted Job Title]
- Job Summary:[4-5 sentences summarizing the core duties and COMPANY(especially the company's NAME) information!! IN KOREAN!!!!!]
- Required Skills: [Skill1, Skill2, Skill3, ...]"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=AiAnnouncementResponse.model_json_schema(),
    )
    result = ""

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        result += chunk.text if chunk.text else ""

    result = json.loads(result)

    return AiAnnouncementResponse(**result)

if __name__ == "__main__":
    load_dotenv()

    url = "https://jumpit.saramin.co.kr/position/53315032"
    last_modified = "2024-06-01"
    announcement = asyncio.run(parse_content(url, last_modified))

    ai_response = extract_position_and_summary(announcement)
    print(ai_response)