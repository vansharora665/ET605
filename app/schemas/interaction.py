from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SubtopicMetricPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subtopic_id: str = Field(..., min_length=1)
    questions_attempted: Optional[int] = Field(default=None, ge=0)
    correct_answers: Optional[int] = Field(default=None, ge=0)
    wrong_answers: Optional[int] = Field(default=None, ge=0)
    hints_used: Optional[int] = Field(default=None, ge=0)
    retry_count: Optional[int] = Field(default=None, ge=0)
    time_spent_seconds: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_subtopic_counts(self) -> "SubtopicMetricPayload":
        if (
            self.questions_attempted is not None
            and self.correct_answers is not None
            and self.wrong_answers is not None
            and self.correct_answers + self.wrong_answers > self.questions_attempted
        ):
            raise ValueError(
                "correct_answers + wrong_answers cannot exceed questions_attempted"
            )
        return self


class InteractionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Optional[str] = None
    student_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    chapter_id: str = Field(..., min_length=1)
    timestamp: datetime
    session_status: Optional[Literal["completed", "exited_midway"]] = None
    correct_answers: Optional[int] = Field(default=None, ge=0)
    wrong_answers: Optional[int] = Field(default=None, ge=0)
    questions_attempted: Optional[int] = Field(default=None, ge=0)
    total_questions: Optional[int] = Field(default=None, ge=0)
    hints_used: Optional[int] = Field(default=None, ge=0)
    total_hints_embedded: Optional[int] = Field(default=None, ge=0)
    retry_count: Optional[int] = Field(default=None, ge=0)
    time_spent_seconds: Optional[int] = Field(default=None, ge=0)
    topic_completion_ratio: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    subtopic_metrics: Optional[List[SubtopicMetricPayload]] = None

    @model_validator(mode="after")
    def validate_counts(self) -> "InteractionIn":
        if (
            self.correct_answers is not None
            and self.wrong_answers is not None
            and self.questions_attempted is not None
            and self.correct_answers + self.wrong_answers > self.questions_attempted
        ):
            raise ValueError(
                "correct_answers + wrong_answers cannot exceed questions_attempted"
            )

        if (
            self.correct_answers is not None
            and self.wrong_answers is not None
            and self.total_questions is not None
            and self.correct_answers + self.wrong_answers > self.total_questions
        ):
            raise ValueError(
                "correct_answers + wrong_answers cannot exceed total_questions"
            )

        if (
            self.questions_attempted is not None
            and self.total_questions is not None
            and self.questions_attempted > self.total_questions
        ):
            raise ValueError("questions_attempted cannot exceed total_questions")

        if (
            self.hints_used is not None
            and self.total_hints_embedded is not None
            and self.hints_used > self.total_hints_embedded
        ):
            raise ValueError("hints_used cannot exceed total_hints_embedded")

        return self


class InteractionIngestResponse(BaseModel):
    session_id: str
    status: Literal["created", "updated"]
    performance_score: Optional[float]
    needs_recommendation: bool
    message: str
