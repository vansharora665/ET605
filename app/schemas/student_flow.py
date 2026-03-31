from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class QuestionOption(BaseModel):
    index: int
    text: str


class QuestionResponse(BaseModel):
    question_id: str
    subtopic_id: str
    prompt: str
    hint: str
    correct_option_index: int
    options: list[QuestionOption]


class StudentCourseDetail(BaseModel):
    chapter_id: str
    grade: int
    chapter_name: str
    description: str
    learning_goal: str
    difficulty: float
    expected_completion_time: int
    prerequisites: list[str]
    next_chapter_id: Optional[str]
    questions: list[QuestionResponse]


class StudentAnswerSubmission(BaseModel):
    question_id: str
    selected_option_index: Optional[int] = None
    attempts: int = Field(..., ge=0)
    hint_opened: bool = False


class StudentSessionSubmission(BaseModel):
    student_id: str = Field(..., min_length=1)
    chapter_id: str = Field(..., min_length=1)
    time_spent_seconds: int = Field(..., ge=0)
    confidence_level: int = Field(default=3, ge=1, le=5)
    focus_level: int = Field(default=3, ge=1, le=5)
    study_mode: Literal["guided", "independent", "revision"] = "guided"
    ended_early: bool = False
    answers: list[StudentAnswerSubmission]


class StudentQuestionResult(BaseModel):
    question_id: str
    selected_option_index: Optional[int]
    is_correct: bool
    attempts: int
    hint_opened: bool


class TeamApiSubmission(BaseModel):
    endpoint: str
    method: str
    payload: dict


class ScoreBreakdownItem(BaseModel):
    name: str
    value: Optional[float]
    normalized_weight: Optional[float]
    contribution: Optional[float]


class NormalizedScoreExplanation(BaseModel):
    formula: str
    summary: str
    weights_sum: float


class StudentSessionResponse(BaseModel):
    student_id: str
    chapter_id: str
    chapter_name: str
    session_id: str
    submitted_at: datetime
    student_results: list[StudentQuestionResult]
    performance_score: Optional[float]
    performance_band: str
    score_breakdown: list[ScoreBreakdownItem]
    normalized_score_explanation: NormalizedScoreExplanation
    next_chapter_id: Optional[str]
    next_chapter_name: Optional[str]
    recommendation_reason: str
    support_recommendations: list[str]
    weak_subtopics: list[str]
    recommendation_parameters: dict
    observed_patterns: list[str]
    coaching_tips: list[str]
    learner_signals: dict
    team_api_submission: TeamApiSubmission
    admin_summary: dict
