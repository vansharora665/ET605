from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import get_session, get_settings
from app.core.config import Settings
from app.schemas.chapter import ChapterResponse
from app.schemas.interaction import InteractionIn, InteractionIngestResponse
from app.schemas.pathway import NextChapterResponse
from app.schemas.recommendation import RecommendationResponse
from app.services.merge import (
    get_recommendation,
    ingest_interaction,
    list_chapters,
    predict_next_chapter,
)

router = APIRouter(prefix="/merge", tags=["merge"])


@router.get(
    "/chapters",
    response_model=list[ChapterResponse],
    summary="Fetch all chapter metadata",
)
def get_chapters(db: Session = Depends(get_session)) -> list[ChapterResponse]:
    return list_chapters(db)


@router.post(
    "/interactions",
    response_model=InteractionIngestResponse,
    status_code=201,
    summary="Accept session-end interaction data from chapter modules",
)
def post_interactions(
    payload: InteractionIn,
    response: Response,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> InteractionIngestResponse:
    result = ingest_interaction(
        db=db,
        payload=payload,
        scoring_profile=settings.scoring_profile,
        threshold=settings.recommendation_threshold,
    )
    if result.status == "updated":
        response.status_code = 200
    return result


@router.get(
    "/recommendations/{student_id}",
    response_model=RecommendationResponse,
    summary="Fetch prerequisite chapter recommendations for a student",
)
def get_student_recommendations(
    student_id: str,
    chapter_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> RecommendationResponse:
    return get_recommendation(
        db=db,
        student_id=student_id,
        chapter_id=chapter_id,
        threshold=settings.recommendation_threshold,
    )


@router.get(
    "/next-chapter/{student_id}",
    response_model=NextChapterResponse,
    summary="Predict the next chapter for a student from the latest processed session",
)
def get_next_chapter(
    student_id: str,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> NextChapterResponse:
    return predict_next_chapter(
        db=db,
        student_id=student_id,
        threshold=settings.recommendation_threshold,
    )
