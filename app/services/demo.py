from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.core.errors import ApiError
from app.models import Chapter, StudentSession
from app.schemas.demo import (
    AdminDecisionSummary,
    DemoCourseResponse,
    DemoSubmissionIn,
    DemoSubmissionResponse,
    SubmittedFactors,
)
from app.schemas.interaction import InteractionIn
from app.schemas.student_flow import (
    NormalizedScoreExplanation,
    QuestionOption,
    QuestionResponse,
    ScoreBreakdownItem,
    StudentCourseDetail,
    StudentQuestionResult,
    StudentSessionResponse,
    StudentSessionSubmission,
    TeamApiSubmission,
)
from app.services.catalog import load_catalog
from app.services.merge import get_recommendation, ingest_interaction, predict_next_chapter
from app.services.recommendation import build_recommendation_parameters
from app.services.scoring import compute_performance_score, difficulty_level_from_value


def _performance_band(score: float | None) -> str:
    if score is None:
        return "insufficient_data"
    if score >= 0.8:
        return "excellent"
    if score >= 0.6:
        return "on_track"
    if score >= 0.4:
        return "needs_support"
    return "intensive_support"


def _observed_patterns(
    *,
    confidence_level: int,
    focus_level: int,
    hints_used: int,
    retry_count: int,
    completion_ratio: float,
    ended_early: bool,
    study_mode: str,
) -> list[str]:
    patterns: list[str] = []
    if hints_used >= 2:
        patterns.append("high_hint_dependency")
    if retry_count >= 2:
        patterns.append("multiple_retries")
    if confidence_level <= 2:
        patterns.append("low_confidence")
    if focus_level <= 2:
        patterns.append("low_focus")
    if completion_ratio < 1:
        patterns.append("partial_completion")
    if ended_early:
        patterns.append("self_ended_session")
    if study_mode == "revision":
        patterns.append("revision_mode")
    if not patterns:
        patterns.append("steady_progress")
    return patterns


def _coaching_tips(
    *,
    patterns: list[str],
    next_chapter_name: str | None,
) -> list[str]:
    tips: list[str] = []
    if "high_hint_dependency" in patterns:
        tips.append("Use worked examples first, then hide hints on the next attempt.")
    if "multiple_retries" in patterns:
        tips.append("Break the chapter into smaller practice bursts before retrying the full set.")
    if "low_confidence" in patterns:
        tips.append("Give the learner one easier prerequisite checkpoint before moving back to full difficulty.")
    if "low_focus" in patterns or "self_ended_session" in patterns:
        tips.append("Recommend a shorter follow-up session with fewer questions and a clear stopping point.")
    if "revision_mode" in patterns:
        tips.append("Keep the learner in revision mode and compare performance against the previous attempt.")
    if next_chapter_name:
        tips.append(f"Suggested next learning touchpoint: {next_chapter_name}.")
    return tips[:4]


def list_demo_courses() -> list[DemoCourseResponse]:
    return [
        DemoCourseResponse(
            chapter_id=chapter["chapter_id"],
            grade=chapter["grade"],
            chapter_name=chapter["chapter_name"],
            difficulty=chapter["difficulty"],
            question_count=chapter["question_count"],
            total_hints_embedded=chapter["total_hints_embedded"],
            prerequisites=chapter["prerequisites"],
            next_chapter_id=chapter.get("next_chapter_id"),
        )
        for chapter in load_catalog()
    ]


def _get_demo_course(chapter_id: str) -> dict:
    for chapter in load_catalog():
        if chapter["chapter_id"] == chapter_id:
            return chapter
    raise ApiError(404, f"Unknown chapter_id '{chapter_id}'")


def get_student_course(chapter_id: str) -> StudentCourseDetail:
    chapter = _get_demo_course(chapter_id)
    return StudentCourseDetail(
        chapter_id=chapter["chapter_id"],
        grade=chapter["grade"],
        chapter_name=chapter["chapter_name"],
        description=chapter["description"],
        learning_goal=chapter["learning_goal"],
        difficulty=chapter["difficulty"],
        expected_completion_time=chapter["expected_completion_time"],
        prerequisites=chapter["prerequisites"],
        next_chapter_id=chapter.get("next_chapter_id"),
        questions=[
            QuestionResponse(
                question_id=question["question_id"],
                subtopic_id=question["subtopic_id"],
                prompt=question["prompt"],
                hint=question["hint"],
                correct_option_index=question["correct_option_index"],
                options=[
                    QuestionOption(index=index, text=option)
                    for index, option in enumerate(question["options"])
                ],
            )
            for question in chapter["questions"]
        ],
    )


def submit_demo_progress(
    db: Session,
    payload: DemoSubmissionIn,
    scoring_profile: str,
    threshold: float,
) -> DemoSubmissionResponse:
    chapter = _get_demo_course(payload.chapter_id)
    attempted = payload.correct_answers + payload.wrong_answers

    if attempted > chapter["question_count"]:
        raise ApiError(
            422,
            "correct_answers + wrong_answers cannot exceed the configured question_count for this demo course",
        )
    if payload.hints_used > chapter["total_hints_embedded"]:
        raise ApiError(
            422,
            "hints_used cannot exceed the configured total_hints_embedded for this demo course",
        )

    timestamp = datetime.now(timezone.utc)
    interaction_payload = InteractionIn(
        schema_version=chapter["schema_version"],
        student_id=payload.student_id,
        session_id=f"demo_{payload.student_id}_{payload.chapter_id}_{uuid4().hex[:8]}",
        chapter_id=payload.chapter_id,
        timestamp=timestamp,
        session_status="completed" if payload.topic_completion_ratio >= 1.0 else "exited_midway",
        correct_answers=payload.correct_answers,
        wrong_answers=payload.wrong_answers,
        questions_attempted=attempted,
        total_questions=chapter["question_count"],
        hints_used=payload.hints_used,
        total_hints_embedded=chapter["total_hints_embedded"],
        retry_count=payload.retry_count,
        time_spent_seconds=payload.time_spent_seconds,
        topic_completion_ratio=payload.topic_completion_ratio,
        chapter_difficulty_level=difficulty_level_from_value(chapter["difficulty"]),
        expected_completion_time_seconds=chapter["expected_completion_time"],
        prerequisite_chapter_ids=chapter["prerequisites"],
        subtopic_metrics=None,
    )

    ingest_result = ingest_interaction(
        db=db,
        payload=interaction_payload,
        scoring_profile=scoring_profile,
        threshold=threshold,
    )
    recommendation = get_recommendation(
        db=db,
        student_id=payload.student_id,
        threshold=threshold,
        chapter_id=payload.chapter_id,
    )
    next_chapter = predict_next_chapter(
        db=db,
        student_id=payload.student_id,
        threshold=threshold,
    )

    return DemoSubmissionResponse(
        student_id=payload.student_id,
        submitted_chapter_id=payload.chapter_id,
        submitted_chapter_name=chapter["chapter_name"],
        submitted_factors=SubmittedFactors(
            correct_answers=payload.correct_answers,
            wrong_answers=payload.wrong_answers,
            hints_used=payload.hints_used,
            retry_count=payload.retry_count,
            time_spent_seconds=payload.time_spent_seconds,
            topic_completion_ratio=payload.topic_completion_ratio,
        ),
        admin_delivery=AdminDecisionSummary(
            session_id=ingest_result.session_id,
            delivered_at=timestamp,
            performance_score=ingest_result.performance_score,
            needs_support=recommendation.needs_support,
            prerequisite_recommendations=recommendation.recommendations,
            weak_subtopics=recommendation.weak_subtopics,
            next_chapter_id=next_chapter.predicted_next_chapter_id,
            next_chapter_name=next_chapter.predicted_next_chapter_name,
            decision_type=next_chapter.decision_type,
            rationale=next_chapter.rationale,
        ),
    )


def submit_student_session(
    db: Session,
    payload: StudentSessionSubmission,
    scoring_profile: str,
    threshold: float,
    force_ended_early: bool = False,
) -> StudentSessionResponse:
    chapter = _get_demo_course(payload.chapter_id)
    questions_by_id = {question["question_id"]: question for question in chapter["questions"]}
    subtopic_accumulator: dict[str, dict] = {}
    question_results: list[StudentQuestionResult] = []

    correct_answers = 0
    wrong_answers = 0
    questions_attempted = 0
    hints_used = 0
    retry_count = 0

    for answer in payload.answers:
        question = questions_by_id.get(answer.question_id)
        if question is None:
            raise ApiError(422, f"Unknown question_id '{answer.question_id}' for chapter '{payload.chapter_id}'")

        attempts = answer.attempts
        selected_option_index = answer.selected_option_index
        attempted = attempts > 0 and selected_option_index is not None
        is_correct = attempted and selected_option_index == question["correct_option_index"]

        if attempted:
            questions_attempted += 1
            if is_correct:
                correct_answers += 1
            else:
                wrong_answers += 1
        if answer.hint_opened:
            hints_used += 1
        if attempts > 1:
            retry_count += attempts - 1

        question_results.append(
            StudentQuestionResult(
                question_id=answer.question_id,
                selected_option_index=selected_option_index,
                is_correct=bool(is_correct),
                attempts=attempts,
                hint_opened=answer.hint_opened,
            )
        )

        subtopic_id = question["subtopic_id"]
        metric = subtopic_accumulator.setdefault(
            subtopic_id,
            {
                "subtopic_id": subtopic_id,
                "questions_attempted": 0,
                "correct_answers": 0,
                "wrong_answers": 0,
                "hints_used": 0,
                "retry_count": 0,
                "time_spent_seconds": 0,
            },
        )
        if attempted:
            metric["questions_attempted"] += 1
            if is_correct:
                metric["correct_answers"] += 1
            else:
                metric["wrong_answers"] += 1
        if answer.hint_opened:
            metric["hints_used"] += 1
        if attempts > 1:
            metric["retry_count"] += attempts - 1

    if questions_attempted == 0 and not (payload.ended_early or force_ended_early):
        raise ApiError(422, "At least one question must be attempted before ending the chapter session")

    total_questions = len(chapter["questions"])
    completion_ratio = round(questions_attempted / max(total_questions, 1), 2)
    effective_ended_early = payload.ended_early or force_ended_early
    if effective_ended_early:
        session_status = "exited_midway"
        completion_ratio = min(completion_ratio, 0.9)
    else:
        session_status = "completed" if questions_attempted == total_questions else "exited_midway"

    # Split the observed time equally across attempted questions for demo reporting.
    timestamp = datetime.now(timezone.utc)
    if payload.session_started_at is not None:
        started_at = payload.session_started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        elapsed_seconds = max(0, int((timestamp - started_at).total_seconds()))
        actual_time_spent = max(payload.time_spent_seconds, elapsed_seconds)
    else:
        actual_time_spent = payload.time_spent_seconds

    time_per_attempted = int(actual_time_spent / max(questions_attempted, 1))
    for metric in subtopic_accumulator.values():
        metric["time_spent_seconds"] = metric["questions_attempted"] * time_per_attempted

    merge_payload = {
        "schema_version": chapter["schema_version"],
        "student_id": payload.student_id,
        "session_id": payload.session_id or f"play_{payload.student_id}_{payload.chapter_id}_{uuid4().hex[:8]}",
        "chapter_id": payload.chapter_id,
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "session_status": session_status,
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "questions_attempted": questions_attempted,
        "total_questions": total_questions,
        "hints_used": hints_used,
        "total_hints_embedded": chapter["total_hints_embedded"],
        "retry_count": retry_count,
        "time_spent_seconds": actual_time_spent,
        "topic_completion_ratio": completion_ratio,
        "chapter_difficulty_level": difficulty_level_from_value(chapter["difficulty"]),
        "expected_completion_time_seconds": chapter["expected_completion_time"],
        "prerequisite_chapter_ids": chapter["prerequisites"],
        "subtopic_metrics": list(subtopic_accumulator.values()),
    }

    ingest_result = ingest_interaction(
        db=db,
        payload=InteractionIn(**merge_payload),
        scoring_profile=scoring_profile,
        threshold=threshold,
    )
    recommendation = get_recommendation(
        db=db,
        student_id=payload.student_id,
        threshold=threshold,
        chapter_id=payload.chapter_id,
    )
    next_chapter = predict_next_chapter(
        db=db,
        student_id=payload.student_id,
        threshold=threshold,
    )

    persisted_session = db.scalars(
        select(StudentSession)
        .options(
            selectinload(StudentSession.chapter).selectinload(Chapter.subtopics),
            selectinload(StudentSession.interaction),
        )
        .where(StudentSession.session_id == merge_payload["session_id"])
    ).first()
    if persisted_session is None or persisted_session.interaction is None:
        raise ApiError(500, "Processed session could not be reloaded for admin scoring view")

    score_result = compute_performance_score(
        chapter=persisted_session.chapter,
        session=persisted_session,
        interaction=persisted_session.interaction,
        profile=scoring_profile,
    )
    recommendation_parameters = build_recommendation_parameters(
        chapter=persisted_session.chapter,
        session=persisted_session,
        interaction=persisted_session.interaction,
        threshold=threshold,
    )

    admin_summary = {
        "performance_score": ingest_result.performance_score,
        "performance_band": _performance_band(ingest_result.performance_score),
        "needs_support": recommendation.needs_support,
        "decision_type": next_chapter.decision_type,
        "next_chapter_id": next_chapter.predicted_next_chapter_id,
        "next_chapter_name": next_chapter.predicted_next_chapter_name,
        "support_recommendations": recommendation.recommendations,
        "weak_subtopics": recommendation.weak_subtopics,
        "rationale": next_chapter.rationale,
        "normalization_summary": (
            "The score is normalized to 0-1. Only available components are used, and their "
            "weights are renormalized to sum to 1.0 before the final score is calculated."
        ),
    }
    observed_patterns = _observed_patterns(
        confidence_level=payload.confidence_level,
        focus_level=payload.focus_level,
        hints_used=hints_used,
        retry_count=retry_count,
        completion_ratio=completion_ratio,
        ended_early=payload.ended_early,
        study_mode=payload.study_mode,
    )
    coaching_tips = _coaching_tips(
        patterns=observed_patterns,
        next_chapter_name=next_chapter.predicted_next_chapter_name,
    )

    return StudentSessionResponse(
        student_id=payload.student_id,
        chapter_id=payload.chapter_id,
        chapter_name=chapter["chapter_name"],
        session_id=merge_payload["session_id"],
        submitted_at=timestamp,
        student_results=question_results,
        performance_score=ingest_result.performance_score,
        performance_band=_performance_band(ingest_result.performance_score),
        score_breakdown=[
            ScoreBreakdownItem(
                name=name,
                value=round(score_result.component_scores.get(name), 4) if score_result.component_scores.get(name) is not None else None,
                normalized_weight=round(score_result.component_weights.get(name), 4) if score_result.component_weights.get(name) is not None else None,
                contribution=round(score_result.component_contributions.get(name), 4) if score_result.component_contributions.get(name) is not None else None,
            )
            for name in [
                "mastery_ratio",
                "attempt_coverage",
                "hint_independence",
                "retry_resilience",
                "time_efficiency",
                "completion_ratio",
                "difficulty_progress",
                "prerequisite_readiness",
            ]
        ],
        normalized_score_explanation=NormalizedScoreExplanation(
            formula="normalized_score = sum(component_value x normalized_weight)",
            summary=(
                "We keep the standard base weights fixed whenever the official fields are present. "
                "Only if a raw field is actually missing or null do we exclude that component and "
                "renormalize the remaining weights so they still sum to 1.0."
            ),
            weights_sum=round(sum(score_result.component_weights.values()), 4),
        ),
        next_chapter_id=next_chapter.predicted_next_chapter_id,
        next_chapter_name=next_chapter.predicted_next_chapter_name,
        recommendation_reason=next_chapter.rationale,
        support_recommendations=recommendation.recommendations,
        weak_subtopics=recommendation.weak_subtopics,
        recommendation_parameters=recommendation_parameters,
        observed_patterns=observed_patterns,
        coaching_tips=coaching_tips,
        learner_signals={
            "confidence_level": payload.confidence_level,
            "focus_level": payload.focus_level,
            "study_mode": payload.study_mode,
            "ended_early": payload.ended_early,
        },
        team_api_submission=TeamApiSubmission(
            endpoint="/merge/interactions",
            method="POST",
            payload=merge_payload,
        ),
        admin_summary=admin_summary,
    )


def get_admin_view(
    db: Session,
    student_id: str,
    threshold: float,
) -> AdminDecisionSummary:
    next_chapter = predict_next_chapter(
        db=db,
        student_id=student_id,
        threshold=threshold,
    )
    if next_chapter.current_chapter_id is None:
        raise ApiError(404, f"No submitted chapter data found for student '{student_id}'")

    recommendation = get_recommendation(
        db=db,
        student_id=student_id,
        threshold=threshold,
        chapter_id=next_chapter.current_chapter_id,
    )

    return AdminDecisionSummary(
        session_id=recommendation.session_id,
        delivered_at=recommendation.based_on_timestamp,
        performance_score=recommendation.performance_score,
        needs_support=recommendation.needs_support,
        prerequisite_recommendations=recommendation.recommendations,
        weak_subtopics=recommendation.weak_subtopics,
        next_chapter_id=next_chapter.predicted_next_chapter_id,
        next_chapter_name=next_chapter.predicted_next_chapter_name,
        decision_type=next_chapter.decision_type,
        rationale=next_chapter.rationale,
    )
