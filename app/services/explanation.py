from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import ApiError
from app.models import Chapter, StudentSession
from app.schemas.explanation import (
    DecisionStep,
    EngineExplanationResponse,
    ScoreStep,
    ValidationCheck,
)
from app.services.merge import get_recommendation
from app.services.recommendation import build_next_chapter_response, build_recommendation_parameters
from app.services.scoring import compute_performance_score, difficulty_level_from_value


def _build_payload(session: StudentSession) -> dict:
    interaction = session.interaction
    return {
        "student_id": session.student_id,
        "session_id": session.session_id,
        "chapter_id": session.chapter_id,
        "timestamp": session.timestamp.isoformat().replace("+00:00", "Z"),
        "session_status": session.session_status,
        "correct_answers": interaction.correct_answers,
        "wrong_answers": interaction.wrong_answers,
        "questions_attempted": interaction.questions_attempted,
        "total_questions": interaction.total_questions,
        "retry_count": interaction.retry_count,
        "hints_used": interaction.hints_used,
        "total_hints_embedded": interaction.total_hints,
        "time_spent_seconds": interaction.time_spent,
        "topic_completion_ratio": session.completion_ratio,
        "chapter_difficulty_level": difficulty_level_from_value(session.chapter.difficulty),
        "expected_completion_time_seconds": session.chapter.expected_completion_time,
        "prerequisite_chapter_ids": session.chapter.prerequisites,
        "subtopic_metrics": interaction.subtopic_metrics,
    }


def _build_validation_checks(payload: dict) -> list[ValidationCheck]:
    correct = payload.get("correct_answers")
    wrong = payload.get("wrong_answers")
    attempted = payload.get("questions_attempted")
    total = payload.get("total_questions")
    hints_used = payload.get("hints_used")
    total_hints = payload.get("total_hints_embedded")
    completion_ratio = payload.get("topic_completion_ratio")

    return [
        ValidationCheck(
            name="correct_plus_wrong_lte_attempted",
            passed=(
                correct is None
                or wrong is None
                or attempted is None
                or correct + wrong <= attempted
            ),
            detail=f"{correct} + {wrong} <= {attempted}",
        ),
        ValidationCheck(
            name="attempted_lte_total",
            passed=(
                attempted is None
                or total is None
                or attempted <= total
            ),
            detail=f"{attempted} <= {total}",
        ),
        ValidationCheck(
            name="hints_used_lte_total_hints",
            passed=(
                hints_used is None
                or total_hints is None
                or hints_used <= total_hints
            ),
            detail=f"{hints_used} <= {total_hints}",
        ),
        ValidationCheck(
            name="completion_ratio_in_range",
            passed=completion_ratio is None or 0 <= completion_ratio <= 1,
            detail=f"0 <= {completion_ratio} <= 1",
        ),
    ]


def get_engine_explanation(
    db: Session,
    student_id: str,
    threshold: float,
    scoring_profile: str,
) -> EngineExplanationResponse:
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
        raise ApiError(404, f"No processed session found for student '{student_id}'")

    payload = _build_payload(session)
    validation_checks = _build_validation_checks(payload)
    score_result = compute_performance_score(
        chapter=session.chapter,
        session=session,
        interaction=session.interaction,
        profile=scoring_profile,
    )
    recommendation = get_recommendation(
        db=db,
        student_id=student_id,
        threshold=threshold,
        chapter_id=session.chapter_id,
    )
    next_chapter = build_next_chapter_response(
        session=session,
        interaction=session.interaction,
        chapter=session.chapter,
        threshold=threshold,
        student_id=student_id,
    )
    recommendation_parameters = build_recommendation_parameters(
        chapter=session.chapter,
        session=session,
        interaction=session.interaction,
        threshold=threshold,
    )

    attempted = session.interaction.questions_attempted or 0
    total_questions = session.interaction.total_questions or 0
    prerequisite_factor = min(len(session.chapter.prerequisites or []) / 3, 1.0)
    score_steps = [
        ScoreStep(
            name="mastery_ratio",
            formula=f"{session.interaction.correct_answers or 0} / max({total_questions}, 1)",
            value=score_result.component_scores.get("mastery_ratio"),
            weight=score_result.component_weights.get("mastery_ratio"),
            contribution=score_result.component_contributions.get("mastery_ratio"),
            included="mastery_ratio" in score_result.component_scores,
        ),
        ScoreStep(
            name="attempt_coverage",
            formula=f"{attempted} / max({total_questions}, 1)",
            value=score_result.component_scores.get("attempt_coverage"),
            weight=score_result.component_weights.get("attempt_coverage"),
            contribution=score_result.component_contributions.get("attempt_coverage"),
            included="attempt_coverage" in score_result.component_scores,
        ),
        ScoreStep(
            name="hint_independence",
            formula=f"1 - ({session.interaction.hints_used or 0} / max({session.interaction.total_hints or 0}, 1))",
            value=score_result.component_scores.get("hint_independence"),
            weight=score_result.component_weights.get("hint_independence"),
            contribution=score_result.component_contributions.get("hint_independence"),
            included="hint_independence" in score_result.component_scores,
        ),
        ScoreStep(
            name="retry_resilience",
            formula=f"1 - ({session.interaction.retry_count or 0} / max({attempted}, 1))",
            value=score_result.component_scores.get("retry_resilience"),
            weight=score_result.component_weights.get("retry_resilience"),
            contribution=score_result.component_contributions.get("retry_resilience"),
            included="retry_resilience" in score_result.component_scores,
        ),
        ScoreStep(
            name="time_efficiency",
            formula=f"min({session.chapter.expected_completion_time} / max({session.interaction.time_spent or 0}, 1), 1)",
            value=score_result.component_scores.get("time_efficiency"),
            weight=score_result.component_weights.get("time_efficiency"),
            contribution=score_result.component_contributions.get("time_efficiency"),
            included="time_efficiency" in score_result.component_scores,
        ),
        ScoreStep(
            name="completion_ratio",
            formula=f"{session.completion_ratio}",
            value=score_result.component_scores.get("completion_ratio"),
            weight=score_result.component_weights.get("completion_ratio"),
            contribution=score_result.component_contributions.get("completion_ratio"),
            included="completion_ratio" in score_result.component_scores,
        ),
        ScoreStep(
            name="difficulty_progress",
            formula=f"attempt_coverage x (1 - 0.5 x {session.chapter.difficulty})",
            value=score_result.component_scores.get("difficulty_progress"),
            weight=score_result.component_weights.get("difficulty_progress"),
            contribution=score_result.component_contributions.get("difficulty_progress"),
            included="difficulty_progress" in score_result.component_scores,
        ),
        ScoreStep(
            name="prerequisite_readiness",
            formula=f"{session.completion_ratio} x (1 - 0.5 x {prerequisite_factor})",
            value=score_result.component_scores.get("prerequisite_readiness"),
            weight=score_result.component_weights.get("prerequisite_readiness"),
            contribution=score_result.component_contributions.get("prerequisite_readiness"),
            included="prerequisite_readiness" in score_result.component_scores,
        ),
    ]

    decision_steps = [
        DecisionStep(
            step="validation",
            outcome="passed" if all(check.passed for check in validation_checks) else "failed",
            detail="Payload sanity checks were run before scoring.",
        ),
        DecisionStep(
            step="score_threshold",
            outcome="below_threshold" if (score_result.score or 0) < threshold else "meets_threshold",
            detail=f"Final score {score_result.score} compared with threshold {threshold}.",
        ),
        DecisionStep(
            step="session_status",
            outcome=session.session_status or "unknown",
            detail="The engine checks whether the learner completed the chapter or exited midway.",
        ),
        DecisionStep(
            step="next_chapter_decision",
            outcome=next_chapter.decision_type,
            detail=next_chapter.rationale,
        ),
    ]

    return EngineExplanationResponse(
        student_id=student_id,
        session_id=session.session_id,
        chapter_id=session.chapter_id,
        chapter_name=session.chapter.chapter_name,
        session_status=session.session_status,
        based_on_timestamp=session.timestamp,
        payload=payload,
        validation_checks=validation_checks,
        score_profile=scoring_profile,
        threshold=threshold,
        score_steps=score_steps,
        final_score=score_result.score,
        normalized_score_summary=(
            "The final score stays on a 0-1 scale by keeping standard weights fixed when the "
            "official fields are present. Only truly missing or null source fields cause a "
            "component to be excluded and the remaining weights to be renormalized to 1.0."
        ),
        recommendation_parameters=recommendation_parameters,
        decision_steps=decision_steps,
        decision_type=next_chapter.decision_type,
        next_chapter_id=next_chapter.predicted_next_chapter_id,
        next_chapter_name=next_chapter.predicted_next_chapter_name,
        rationale=next_chapter.rationale,
        prerequisite_recommendations=recommendation.recommendations,
        weak_subtopics=recommendation.weak_subtopics,
    )
