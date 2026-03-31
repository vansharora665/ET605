from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class DemoCourseResponse(BaseModel):
    chapter_id: str
    grade: int
    chapter_name: str
    difficulty: float
    question_count: int
    total_hints_embedded: int
    prerequisites: list[str]
    next_chapter_id: Optional[str]


class DemoSubmissionIn(BaseModel):
    student_id: str = Field(..., min_length=1)
    chapter_id: str = Field(..., min_length=1)
    correct_answers: int = Field(..., ge=0)
    wrong_answers: int = Field(..., ge=0)
    hints_used: int = Field(default=0, ge=0)
    retry_count: int = Field(default=0, ge=0)
    time_spent_seconds: int = Field(..., ge=0)
    topic_completion_ratio: float = Field(..., ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_answers(self) -> "DemoSubmissionIn":
        if self.correct_answers + self.wrong_answers == 0:
            raise ValueError("At least one question must be attempted in the demo flow")
        return self


class SubmittedFactors(BaseModel):
    correct_answers: int
    wrong_answers: int
    hints_used: int
    retry_count: int
    time_spent_seconds: int
    topic_completion_ratio: float


class AdminDecisionSummary(BaseModel):
    session_id: str
    delivered_at: datetime
    performance_score: Optional[float]
    needs_support: bool
    prerequisite_recommendations: list[str]
    weak_subtopics: list[str]
    next_chapter_id: Optional[str]
    next_chapter_name: Optional[str]
    decision_type: str
    rationale: str


class DemoSubmissionResponse(BaseModel):
    student_id: str
    submitted_chapter_id: str
    submitted_chapter_name: str
    submitted_factors: SubmittedFactors
    admin_delivery: AdminDecisionSummary
