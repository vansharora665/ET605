from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ValidationCheck(BaseModel):
    name: str
    passed: bool
    detail: str


class ScoreStep(BaseModel):
    name: str
    formula: str
    value: Optional[float]
    weight: Optional[float]
    contribution: Optional[float]
    included: bool


class DecisionStep(BaseModel):
    step: str
    outcome: str
    detail: str


class EngineExplanationResponse(BaseModel):
    student_id: str
    session_id: str
    chapter_id: str
    chapter_name: str
    session_status: Optional[str]
    based_on_timestamp: datetime
    payload: dict
    validation_checks: list[ValidationCheck]
    score_profile: str
    threshold: float
    score_steps: list[ScoreStep]
    final_score: Optional[float]
    normalized_score_summary: str
    recommendation_parameters: dict
    decision_steps: list[DecisionStep]
    decision_type: str
    next_chapter_id: Optional[str]
    next_chapter_name: Optional[str]
    rationale: str
    prerequisite_recommendations: list[str]
    weak_subtopics: list[str]
