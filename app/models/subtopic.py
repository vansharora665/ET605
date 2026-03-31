from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Subtopic(Base):
    __tablename__ = "subtopics"

    subtopic_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    chapter_id: Mapped[str] = mapped_column(
        ForeignKey("chapters.chapter_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, nullable=False)

    chapter: Mapped["Chapter"] = relationship(back_populates="subtopics")
