from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_session, get_settings
from app.core.config import Settings
from app.schemas.demo import AdminDecisionSummary, DemoCourseResponse, DemoSubmissionIn, DemoSubmissionResponse
from app.schemas.explanation import EngineExplanationResponse
from app.schemas.student_flow import StudentCourseDetail, StudentSessionResponse, StudentSessionSubmission
from app.services.explanation import get_engine_explanation
from app.services.demo import (
    get_admin_view,
    get_student_course,
    list_demo_courses,
    submit_demo_progress,
    submit_student_session,
)

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get(
    "/courses",
    response_model=list[DemoCourseResponse],
    summary="List the 4 dummy math courses used for the simple demo",
)
def get_demo_courses() -> list[DemoCourseResponse]:
    return list_demo_courses()


@router.get(
    "/courses/{chapter_id}",
    response_model=StudentCourseDetail,
    summary="Fetch a student-ready chapter with dummy questions and hints",
)
def get_demo_course_detail(chapter_id: str) -> StudentCourseDetail:
    return get_student_course(chapter_id)


@router.post(
    "/submit",
    response_model=DemoSubmissionResponse,
    summary="Submit one simple chapter result and deliver the processed output to the admin view",
)
def post_demo_submission(
    payload: DemoSubmissionIn,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> DemoSubmissionResponse:
    return submit_demo_progress(
        db=db,
        payload=payload,
        scoring_profile=settings.scoring_profile,
        threshold=settings.recommendation_threshold,
    )


@router.post(
    "/student-session",
    response_model=StudentSessionResponse,
    summary="Submit a full student chapter session and see the module API payload plus merge recommendations",
)
def post_student_session(
    payload: StudentSessionSubmission,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> StudentSessionResponse:
    return submit_student_session(
        db=db,
        payload=payload,
        scoring_profile=settings.scoring_profile,
        threshold=settings.recommendation_threshold,
    )


@router.post(
    "/session/complete",
    response_model=StudentSessionResponse,
    summary="Submit a completed or manually ended student session using the refined session lifecycle endpoint",
)
def post_complete_student_session(
    payload: StudentSessionSubmission,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> StudentSessionResponse:
    return submit_student_session(
        db=db,
        payload=payload,
        scoring_profile=settings.scoring_profile,
        threshold=settings.recommendation_threshold,
    )


@router.post(
    "/session/exit",
    response_model=StudentSessionResponse,
    summary="Submit an exited-midway session for tab close, navigation away, or network recovery",
)
def post_exited_student_session(
    payload: StudentSessionSubmission,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> StudentSessionResponse:
    return submit_student_session(
        db=db,
        payload=payload,
        scoring_profile=settings.scoring_profile,
        threshold=settings.recommendation_threshold,
        force_ended_early=True,
    )


@router.get(
    "/admin/{student_id}",
    response_model=AdminDecisionSummary,
    summary="Fetch the latest admin-side decision summary for a student",
)
def get_demo_admin_view(
    student_id: str,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AdminDecisionSummary:
    return get_admin_view(
        db=db,
        student_id=student_id,
        threshold=settings.recommendation_threshold,
    )


@router.get(
    "/engine-explanation/{student_id}",
    response_model=EngineExplanationResponse,
    summary="Explain step by step how the recommendation engine processed the latest session",
)
def get_demo_engine_explanation(
    student_id: str,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> EngineExplanationResponse:
    return get_engine_explanation(
        db=db,
        student_id=student_id,
        threshold=settings.recommendation_threshold,
        scoring_profile=settings.scoring_profile,
    )
