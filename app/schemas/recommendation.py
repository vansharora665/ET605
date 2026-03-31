from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    student_id: str
    chapter_id: str
    session_id: str
    performance_score: Optional[float]
    needs_support: bool
    threshold: float
    based_on_timestamp: datetime
    recommendations: list[str]
    weak_subtopics: list[str]
