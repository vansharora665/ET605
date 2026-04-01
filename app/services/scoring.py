from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.models.chapter import Chapter
from app.models.interaction import Interaction
from app.models.student_session import StudentSession


SCORING_PROFILES = {
    "assignment_core": {
        "accuracy": 0.50,
        "hint_independence": 0.20,
        "retry_resilience": 0.20,
        "time_efficiency": 0.10,
    },
    "revised_spec": {
        "mastery_ratio": 0.30,
        "attempt_coverage": 0.20,
        "hint_independence": 0.10,
        "retry_resilience": 0.10,
        "time_efficiency": 0.10,
        "completion_ratio": 0.10,
        "difficulty_progress": 0.05,
        "prerequisite_readiness": 0.05,
    },
}


@dataclass
class ScoreResult:
    score: Optional[float]
    component_scores: dict[str, float]
    component_weights: dict[str, float]
    component_contributions: dict[str, float]
    profile: str


def _resolve_questions_attempted(interaction: Interaction) -> Optional[int]:
    if interaction.questions_attempted is not None:
        return interaction.questions_attempted
    if interaction.correct_answers is None and interaction.wrong_answers is None:
        return None
    return (interaction.correct_answers or 0) + (interaction.wrong_answers or 0)


def difficulty_level_from_value(difficulty: float | None) -> str:
    if difficulty is None:
        return "mid"
    if difficulty < 0.45:
        return "easy"
    if difficulty < 0.7:
        return "mid"
    return "hard"


def compute_performance_score(
    chapter: Chapter,
    session: StudentSession,
    interaction: Interaction,
    profile: str = "revised_spec",
) -> ScoreResult:
    weights = SCORING_PROFILES.get(profile, SCORING_PROFILES["revised_spec"])
    attempted = _resolve_questions_attempted(interaction)
    components: dict[str, float] = {}
    applied_weights: dict[str, float] = {}
    total_questions = interaction.total_questions
    completion_ratio = session.completion_ratio
    prerequisite_factor = min(len(chapter.prerequisites or []) / 3, 1.0)
    inactive_exit_session = session.session_status == "exited_midway" and (attempted or 0) == 0

    if "accuracy" in weights and attempted and interaction.correct_answers is not None:
        components["accuracy"] = interaction.correct_answers / max(attempted, 1)
        applied_weights["accuracy"] = weights["accuracy"]

    if "mastery_ratio" in weights and total_questions and interaction.correct_answers is not None:
        components["mastery_ratio"] = interaction.correct_answers / max(total_questions, 1)
        applied_weights["mastery_ratio"] = weights["mastery_ratio"]

    if "attempt_coverage" in weights and attempted is not None and total_questions:
        components["attempt_coverage"] = min(attempted / max(total_questions, 1), 1.0)
        applied_weights["attempt_coverage"] = weights["attempt_coverage"]

    if (
        "hint_independence" in weights
        and interaction.hints_used is not None
        and interaction.total_hints is not None
    ):
        if inactive_exit_session:
            components["hint_independence"] = 0.0
        elif interaction.total_hints == 0:
            components["hint_independence"] = 1.0
        else:
            components["hint_independence"] = 1 - min(
                interaction.hints_used / interaction.total_hints,
                1.0,
            )
        applied_weights["hint_independence"] = weights["hint_independence"]

    if "retry_resilience" in weights and interaction.retry_count is not None:
        if inactive_exit_session:
            components["retry_resilience"] = 0.0
            applied_weights["retry_resilience"] = weights["retry_resilience"]
        elif attempted:
            components["retry_resilience"] = 1 - min(
                interaction.retry_count / max(attempted, 1),
                1.0,
            )
            applied_weights["retry_resilience"] = weights["retry_resilience"]

    if (
        "time_efficiency" in weights
        and
        chapter.expected_completion_time
        and interaction.time_spent is not None
    ):
        components["time_efficiency"] = min(
            chapter.expected_completion_time / max(interaction.time_spent, 1),
            1.0,
        )
        applied_weights["time_efficiency"] = weights["time_efficiency"]

    if (
        "completion_ratio" in weights
        and completion_ratio is not None
    ):
        components["completion_ratio"] = completion_ratio
        applied_weights["completion_ratio"] = weights["completion_ratio"]

    if (
        "difficulty_progress" in weights
        and total_questions
        and attempted is not None
    ):
        attempt_coverage = min(attempted / max(total_questions, 1), 1.0)
        components["difficulty_progress"] = attempt_coverage * (1 - 0.5 * chapter.difficulty)
        applied_weights["difficulty_progress"] = weights["difficulty_progress"]

    if (
        "prerequisite_readiness" in weights
        and completion_ratio is not None
    ):
        components["prerequisite_readiness"] = completion_ratio * (1 - 0.5 * prerequisite_factor)
        applied_weights["prerequisite_readiness"] = weights["prerequisite_readiness"]

    if not applied_weights:
        return ScoreResult(
            score=None,
            component_scores=components,
            component_weights={},
            component_contributions={},
            profile=profile,
        )

    total_applied_weight = sum(applied_weights.values())
    fixed_weights = {
        name: weight / total_applied_weight
        for name, weight in applied_weights.items()
    }
    contributions = {
        name: components.get(name, 0.0) * fixed_weights[name]
        for name in fixed_weights
    }

    score = sum(contributions.values())

    return ScoreResult(
        score=round(max(0.0, min(score, 1.0)), 4),
        component_scores=components,
        component_weights=fixed_weights,
        component_contributions=contributions,
        profile=profile,
    )
