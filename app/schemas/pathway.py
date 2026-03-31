from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NextChapterResponse(BaseModel):
    student_id: str
    current_chapter_id: Optional[str]
    current_chapter_name: Optional[str]
    performance_score: Optional[float]
    decision_type: str
    predicted_next_chapter_id: Optional[str]
    predicted_next_chapter_name: Optional[str]
    threshold: float
    support_recommendations: list[str]
    weak_subtopics: list[str]
    rationale: str
    based_on_timestamp: Optional[datetime]
