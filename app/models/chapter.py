from __future__ import annotations

from typing import Optional

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base


class Chapter(Base):
    __tablename__ = "chapters"

    chapter_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    schema_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    chapter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    chapter_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    difficulty: Mapped[float] = mapped_column(Float, nullable=False)
    expected_completion_time: Mapped[int] = mapped_column(Integer, nullable=False)
    prerequisites: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    subtopics: Mapped[list["Subtopic"]] = relationship(
        back_populates="chapter",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list["StudentSession"]] = relationship(back_populates="chapter")
