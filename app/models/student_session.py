from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class StudentSession(Base):
    __tablename__ = "student_sessions"

    session_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    student_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    chapter_id: Mapped[str] = mapped_column(
        ForeignKey("chapters.chapter_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completion_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    schema_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    session_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    performance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    needs_recommendation: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    chapter: Mapped["Chapter"] = relationship(back_populates="sessions")
    interaction: Mapped["Interaction"] = relationship(
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
