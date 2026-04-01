from __future__ import annotations

from typing import Optional

from app.models.chapter import Chapter
from app.models.interaction import Interaction
from app.models.student_session import StudentSession
from app.schemas.pathway import NextChapterResponse
from app.schemas.recommendation import RecommendationResponse
from app.services.catalog import get_catalog_map, get_starting_chapter
from app.services.scoring import difficulty_level_from_value


def build_recommendation_parameters(
    chapter: Chapter,
    session: StudentSession,
    interaction: Interaction,
    threshold: float,
) -> dict[str, float]:
    attempted = interaction.questions_attempted
    if attempted is None:
        attempted = (interaction.correct_answers or 0) + (interaction.wrong_answers or 0)
    total_questions = interaction.total_questions
    attempt_coverage = None
    if attempted is not None and total_questions:
        attempt_coverage = min(attempted / max(total_questions, 1), 1.0)

    accuracy = None
    if attempted and interaction.correct_answers is not None:
        accuracy = interaction.correct_answers / max(attempted, 1)

    hint_dependency = None
    if interaction.hints_used is not None and interaction.total_hints is not None:
        if interaction.total_hints == 0:
            hint_dependency = 0.0
        else:
            hint_dependency = min(interaction.hints_used / interaction.total_hints, 1.0)

    retry_pressure = None
    if attempted and interaction.retry_count is not None:
        retry_pressure = min(interaction.retry_count / max(attempted, 1), 1.0)

    time_efficiency = None
    if chapter.expected_completion_time and interaction.time_spent is not None:
        time_efficiency = min(
            chapter.expected_completion_time / max(interaction.time_spent, 1),
            1.0,
        )
    time_pressure = None if time_efficiency is None else 1 - time_efficiency

    completion_strength = session.completion_ratio
    completion_gap = None if completion_strength is None else 1 - completion_strength
    prerequisite_count = len(chapter.prerequisites or [])
    prerequisite_factor = min(prerequisite_count / 3, 1.0)

    weak_subtopics = extract_weak_subtopics(chapter, interaction, threshold)
    weak_subtopic_ratio = 0.0
    if chapter.subtopics:
        weak_subtopic_ratio = len(weak_subtopics) / len(chapter.subtopics)

    score = session.performance_score
    score_gap = None if score is None else 1 - score

    struggle_terms = [
        (score_gap, 0.30),
        (None if accuracy is None else 1 - accuracy, 0.20),
        (hint_dependency, 0.10),
        (retry_pressure, 0.10),
        (time_pressure, 0.10),
        (completion_gap, 0.10),
        (chapter.difficulty, 0.10),
    ]
    applied_terms = [(value, weight) for value, weight in struggle_terms if value is not None]
    struggle_index = None
    if applied_terms:
        total_weight = sum(weight for _, weight in applied_terms)
        struggle_index = sum(value * weight for value, weight in applied_terms) / total_weight

    readiness_index = None if struggle_index is None else 1 - struggle_index
    prerequisite_pressure = None if struggle_index is None else struggle_index * max(chapter.difficulty, 0.4)

    return {
        "accuracy": round(accuracy, 4) if accuracy is not None else None,
        "attempt_coverage": round(attempt_coverage, 4) if attempt_coverage is not None else None,
        "hint_dependency": round(hint_dependency, 4) if hint_dependency is not None else None,
        "retry_pressure": round(retry_pressure, 4) if retry_pressure is not None else None,
        "time_efficiency": round(time_efficiency, 4) if time_efficiency is not None else None,
        "time_pressure": round(time_pressure, 4) if time_pressure is not None else None,
        "completion_strength": round(completion_strength, 4) if completion_strength is not None else None,
        "completion_gap": round(completion_gap, 4) if completion_gap is not None else None,
        "difficulty_level": difficulty_level_from_value(chapter.difficulty),
        "difficulty_factor": round(chapter.difficulty, 4),
        "expected_completion_time_seconds": chapter.expected_completion_time,
        "prerequisite_count": prerequisite_count,
        "prerequisite_factor": round(prerequisite_factor, 4),
        "prerequisite_chapter_ids": chapter.prerequisites or [],
        "weak_subtopic_ratio": round(weak_subtopic_ratio, 4),
        "score_gap": round(score_gap, 4) if score_gap is not None else None,
        "struggle_index": round(struggle_index, 4) if struggle_index is not None else None,
        "readiness_index": round(readiness_index, 4) if readiness_index is not None else None,
        "prerequisite_pressure": round(prerequisite_pressure, 4) if prerequisite_pressure is not None else None,
    }


def _subtopic_score(metric: dict) -> Optional[float]:
    attempted = metric.get("questions_attempted")
    if attempted is None:
        attempted = (metric.get("correct_answers") or 0) + (metric.get("wrong_answers") or 0)

    if not attempted:
        return None

    parts: list[float] = []
    if metric.get("correct_answers") is not None:
        parts.append(metric["correct_answers"] / max(attempted, 1))
    if metric.get("retry_count") is not None:
        parts.append(1 - min(metric["retry_count"] / max(attempted, 1), 1.0))
    if metric.get("hints_used") is not None:
        parts.append(1 - min(metric["hints_used"] / max(attempted, 1), 1.0))

    if not parts:
        return None
    return sum(parts) / len(parts)


def extract_weak_subtopics(
    chapter: Chapter,
    interaction: Interaction,
    threshold: float,
) -> list[str]:
    if not interaction.subtopic_metrics:
        return []

    subtopic_names = {subtopic.subtopic_id: subtopic.name for subtopic in chapter.subtopics}
    scored_subtopics: list[tuple[str, float]] = []

    for metric in interaction.subtopic_metrics:
        score = _subtopic_score(metric)
        if score is None:
            continue
        if score < threshold:
            label = subtopic_names.get(metric["subtopic_id"], metric["subtopic_id"])
            scored_subtopics.append((label, score))

    scored_subtopics.sort(key=lambda item: item[1])
    return [label for label, _ in scored_subtopics[:3]]


def build_recommendation_response(
    session: StudentSession,
    interaction: Interaction,
    chapter: Chapter,
    threshold: float,
) -> RecommendationResponse:
    needs_support = (
        session.performance_score is not None
        and session.performance_score < threshold
    )
    recommendations = chapter.prerequisites if needs_support else []
    weak_subtopics = extract_weak_subtopics(chapter, interaction, threshold) if needs_support else []

    return RecommendationResponse(
        student_id=session.student_id,
        chapter_id=session.chapter_id,
        session_id=session.session_id,
        performance_score=session.performance_score,
        needs_support=needs_support,
        threshold=threshold,
        based_on_timestamp=session.timestamp,
        recommendations=recommendations,
        weak_subtopics=weak_subtopics,
    )


def build_next_chapter_response(
    session: Optional[StudentSession],
    interaction: Optional[Interaction],
    chapter: Optional[Chapter],
    threshold: float,
    student_id: str,
) -> NextChapterResponse:
    catalog_map = get_catalog_map()

    if session is None or interaction is None or chapter is None:
        starting_chapter = get_starting_chapter()
        return NextChapterResponse(
            student_id=student_id,
            current_chapter_id=None,
            current_chapter_name=None,
            performance_score=None,
            decision_type="start_path",
            predicted_next_chapter_id=starting_chapter["chapter_id"],
            predicted_next_chapter_name=starting_chapter["chapter_name"],
            threshold=threshold,
            support_recommendations=[],
            weak_subtopics=[],
            rationale="No previous session found, so the learner starts from the first foundation chapter in the editable catalog.",
            based_on_timestamp=None,
        )

    weak_subtopics = extract_weak_subtopics(chapter, interaction, threshold)
    parameters = build_recommendation_parameters(chapter, session, interaction, threshold)
    score = session.performance_score
    chapter_config = catalog_map.get(chapter.chapter_id, {})
    next_chapter_id = chapter_config.get("next_chapter_id")
    next_chapter = catalog_map.get(next_chapter_id) if next_chapter_id else None

    if (
        (score is not None and score < threshold)
        or (parameters["struggle_index"] is not None and parameters["struggle_index"] >= 0.55)
        or parameters["weak_subtopic_ratio"] >= 0.5
    ):
        remediation_target = chapter.prerequisites[0] if chapter.prerequisites else chapter.chapter_id
        remediation_chapter = catalog_map.get(remediation_target)
        predicted_next_chapter_name = (
            remediation_chapter["chapter_name"]
            if remediation_chapter is not None
            else chapter.chapter_name
        )
        return NextChapterResponse(
            student_id=student_id,
            current_chapter_id=chapter.chapter_id,
            current_chapter_name=chapter.chapter_name,
            performance_score=score,
            decision_type="remediation",
            predicted_next_chapter_id=remediation_target,
            predicted_next_chapter_name=predicted_next_chapter_name,
            threshold=threshold,
            support_recommendations=chapter.prerequisites,
            weak_subtopics=weak_subtopics,
            rationale=(
                "The learner shows enough struggle signals in score, retry/hint behavior, "
                "completion, or weak subtopics that prerequisite revision is recommended "
                "before advancing."
            ),
            based_on_timestamp=session.timestamp,
        )

    if (
        session.session_status == "exited_midway"
        or (session.completion_ratio is not None and session.completion_ratio < 0.8)
        or (parameters["readiness_index"] is not None and parameters["readiness_index"] < 0.65)
    ):
        return NextChapterResponse(
            student_id=student_id,
            current_chapter_id=chapter.chapter_id,
            current_chapter_name=chapter.chapter_name,
            performance_score=score,
            decision_type="continue_current",
            predicted_next_chapter_id=chapter.chapter_id,
            predicted_next_chapter_name=chapter.chapter_name,
            threshold=threshold,
            support_recommendations=[],
            weak_subtopics=weak_subtopics,
            rationale=(
                "The learner has not yet shown enough readiness to move forward, so the "
                "system keeps them on the current chapter for another supported attempt."
            ),
            based_on_timestamp=session.timestamp,
        )

    if next_chapter is not None:
        return NextChapterResponse(
            student_id=student_id,
            current_chapter_id=chapter.chapter_id,
            current_chapter_name=chapter.chapter_name,
            performance_score=score,
            decision_type="advance",
            predicted_next_chapter_id=next_chapter["chapter_id"],
            predicted_next_chapter_name=next_chapter["chapter_name"],
            threshold=threshold,
            support_recommendations=[],
            weak_subtopics=[],
            rationale="The learner met the promotion threshold, so the system advances them to the next chapter defined in the editable catalog.",
            based_on_timestamp=session.timestamp,
        )

    return NextChapterResponse(
        student_id=student_id,
        current_chapter_id=chapter.chapter_id,
        current_chapter_name=chapter.chapter_name,
        performance_score=score,
        decision_type="complete_path",
        predicted_next_chapter_id=None,
        predicted_next_chapter_name=None,
        threshold=threshold,
        support_recommendations=[],
        weak_subtopics=[],
        rationale="This learner is already at the end of the current dummy path, so there is no next chapter configured yet.",
        based_on_timestamp=session.timestamp,
    )
