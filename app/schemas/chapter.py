from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class SubtopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subtopic_id: str
    chapter_id: str
    name: str
    difficulty: float


class ChapterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chapter_id: str
    schema_version: Optional[str] = None
    grade: int
    chapter_name: str
    chapter_url: Optional[str] = None
    difficulty: float
    expected_completion_time: int
    prerequisites: list[str]
    subtopics: list[SubtopicResponse]
