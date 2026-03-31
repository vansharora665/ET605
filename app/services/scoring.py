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
        "accuracy": 0.45,
        "hint_independence": 0.15,
        "retry_resilience": 0.15,
        "time_efficiency": 0.15,
        "completion_ratio": 0.10,
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

    if attempted and interaction.correct_answers is not None:
        components["accuracy"] = interaction.correct_answers / max(attempted, 1)
        applied_weights["accuracy"] = weights["accuracy"]

    if (
        interaction.hints_used is not None
        and interaction.total_hints is not None
        and attempted
    ):
        if interaction.total_hints == 0:
            components["hint_independence"] = 1.0
        else:
            components["hint_independence"] = 1 - min(
                interaction.hints_used / interaction.total_hints,
                1.0,
            )
        applied_weights["hint_independence"] = weights["hint_independence"]

    if attempted and interaction.retry_count is not None:
        components["retry_resilience"] = 1 - min(
            interaction.retry_count / max(attempted, 1),
            1.0,
        )
        applied_weights["retry_resilience"] = weights["retry_resilience"]

    if (
        chapter.expected_completion_time
        and interaction.time_spent is not None
        and attempted
    ):
        components["time_efficiency"] = min(
            chapter.expected_completion_time / max(interaction.time_spent, 1),
            1.0,
        )
        applied_weights["time_efficiency"] = weights["time_efficiency"]

    if (
        "completion_ratio" in weights
        and session.completion_ratio is not None
    ):
        components["completion_ratio"] = session.completion_ratio
        applied_weights["completion_ratio"] = weights["completion_ratio"]

    total_weight = sum(applied_weights.values())
    if total_weight == 0:
        return ScoreResult(
            score=None,
            component_scores=components,
            component_weights={},
            component_contributions={},
            profile=profile,
        )

    normalized_weights = {
        name: applied_weights[name] / total_weight
        for name in components
    }
    contributions = {
        name: components[name] * normalized_weights[name]
        for name in components
    }

    score = sum(contributions.values())

    return ScoreResult(
        score=round(max(0.0, min(score, 1.0)), 4),
        component_scores=components,
        component_weights=normalized_weights,
        component_contributions=contributions,
        profile=profile,
    )
