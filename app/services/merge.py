from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import ApiError
from app.models import Chapter, Interaction, StudentSession
from app.schemas.interaction import InteractionIn, InteractionIngestResponse
from app.schemas.pathway import NextChapterResponse
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation import (
    build_next_chapter_response,
    build_recommendation_response,
)
from app.services.scoring import compute_performance_score, difficulty_level_from_value

logger = logging.getLogger(__name__)


def list_chapters(db: Session) -> list[Chapter]:
    statement = select(Chapter).options(selectinload(Chapter.subtopics)).order_by(Chapter.grade, Chapter.chapter_name)
    return list(db.scalars(statement).all())


def ingest_interaction(
    db: Session,
    payload: InteractionIn,
    scoring_profile: str,
    threshold: float,
) -> InteractionIngestResponse:
    chapter = db.get(Chapter, payload.chapter_id)
    if chapter is None:
        raise ApiError(404, f"Unknown chapter_id '{payload.chapter_id}'")

    expected_level = difficulty_level_from_value(chapter.difficulty)
    if payload.chapter_difficulty_level is not None and payload.chapter_difficulty_level != expected_level:
        raise ApiError(
            422,
            f"chapter_difficulty_level '{payload.chapter_difficulty_level}' does not match configured chapter difficulty '{expected_level}'",
        )
    if (
        payload.expected_completion_time_seconds is not None
        and payload.expected_completion_time_seconds != chapter.expected_completion_time
    ):
        raise ApiError(
            422,
            "expected_completion_time_seconds does not match the configured chapter metadata",
        )
    if payload.prerequisite_chapter_ids is not None and payload.prerequisite_chapter_ids != (chapter.prerequisites or []):
        raise ApiError(
            422,
            "prerequisite_chapter_ids does not match the configured chapter metadata",
        )

    session = db.get(StudentSession, payload.session_id)
    created = False

    if session is None:
        session = StudentSession(
            session_id=payload.session_id,
            student_id=payload.student_id,
            chapter_id=payload.chapter_id,
            timestamp=payload.timestamp,
            completion_ratio=payload.topic_completion_ratio,
            schema_version=payload.schema_version,
            session_status=payload.session_status,
        )
        db.add(session)
        created = True
    else:
        if session.student_id != payload.student_id or session.chapter_id != payload.chapter_id:
            raise ApiError(
                409,
                "Duplicate session_id belongs to a different student or chapter",
            )
        session.timestamp = payload.timestamp
        session.completion_ratio = payload.topic_completion_ratio
        session.schema_version = payload.schema_version
        session.session_status = payload.session_status

    interaction = db.scalar(
        select(Interaction).where(Interaction.session_id == payload.session_id)
    )
    if interaction is None:
        interaction = Interaction(session_id=payload.session_id)
        db.add(interaction)

    interaction.correct_answers = payload.correct_answers
    interaction.wrong_answers = payload.wrong_answers
    interaction.questions_attempted = payload.questions_attempted
    interaction.total_questions = payload.total_questions
    interaction.hints_used = payload.hints_used
    interaction.total_hints = payload.total_hints_embedded
    interaction.retry_count = payload.retry_count
    interaction.time_spent = payload.time_spent_seconds
    interaction.subtopic_metrics = (
        [item.model_dump() for item in payload.subtopic_metrics]
        if payload.subtopic_metrics is not None
        else None
    )

    score_result = compute_performance_score(
        chapter=chapter,
        session=session,
        interaction=interaction,
        profile=scoring_profile,
    )
    session.performance_score = score_result.score
    session.needs_recommendation = (
        score_result.score is not None and score_result.score < threshold
    )

    db.commit()
    db.refresh(session)

    action = "created" if created else "updated"
    logger.info(
        "Processed interaction session_id=%s status=%s score=%s",
        session.session_id,
        action,
        session.performance_score,
    )

    return InteractionIngestResponse(
        session_id=session.session_id,
        status=action,
        performance_score=session.performance_score,
        needs_recommendation=session.needs_recommendation,
        message=(
            "Interaction ingested successfully"
            if created
            else "Interaction updated idempotently"
        ),
    )


def get_recommendation(
    db: Session,
    student_id: str,
    threshold: float,
    chapter_id: Optional[str] = None,
) -> RecommendationResponse:
    statement = (
        select(StudentSession)
        .join(StudentSession.chapter)
        .options(
            selectinload(StudentSession.chapter).selectinload(Chapter.subtopics),
            selectinload(StudentSession.interaction),
        )
        .where(StudentSession.student_id == student_id)
        .order_by(StudentSession.timestamp.desc())
    )
    if chapter_id is not None:
        statement = statement.where(StudentSession.chapter_id == chapter_id)

    session = db.scalars(statement).first()
    if session is None or session.interaction is None:
        raise ApiError(404, f"No processed sessions found for student '{student_id}'")

    return build_recommendation_response(
        session=session,
        interaction=session.interaction,
        chapter=session.chapter,
        threshold=threshold,
    )


def predict_next_chapter(
    db: Session,
    student_id: str,
    threshold: float,
) -> NextChapterResponse:
    statement = (
        select(StudentSession)
        .join(StudentSession.chapter)
        .options(
            selectinload(StudentSession.chapter).selectinload(Chapter.subtopics),
            selectinload(StudentSession.interaction),
        )
        .where(StudentSession.student_id == student_id)
        .order_by(StudentSession.timestamp.desc())
    )
    session = db.scalars(statement).first()

    if session is None or session.interaction is None:
        return build_next_chapter_response(
            session=None,
            interaction=None,
            chapter=None,
            threshold=threshold,
            student_id=student_id,
        )

    return build_next_chapter_response(
        session=session,
        interaction=session.interaction,
        chapter=session.chapter,
        threshold=threshold,
        student_id=student_id,
    )
