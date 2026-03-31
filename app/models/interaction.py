from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("student_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    correct_answers: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    wrong_answers: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    questions_attempted: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_questions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hints_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_hints: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    retry_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    time_spent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    subtopic_metrics: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    session: Mapped["StudentSession"] = relationship(back_populates="interaction")
