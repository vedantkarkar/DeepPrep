"""
Deterministic Gap Prioritizer for Candidate Skills.
"""

from typing import List, Dict, Any
from app.domains.planning.rules import (
    compute_gap_effort,
    IS_REQUIRED_FACTOR,
    IS_PREFERRED_FACTOR,
    INTERVIEW_RELEVANCE_MULTIPLIERS,
)

class CandidateSkillGap:
    def __init__(
        self,
        skill_slug: str,
        canonical_name: str,
        category: str,
        required_level: int,
        estimated_level: int,
        importance_weight: float,
        is_required: bool,
        interview_relevance: str,
        confidence_score: str,
        classification: str,
    ):
        self.skill_slug = skill_slug
        self.canonical_name = canonical_name
        self.category = category
        self.required_level = required_level
        self.estimated_level = estimated_level
        self.importance_weight = importance_weight
        self.is_required = is_required
        self.interview_relevance = interview_relevance.lower() if interview_relevance else "medium"
        self.confidence_score = confidence_score.lower() if confidence_score else "medium"
        self.classification = classification

        self.gap_levels = max(0, required_level - estimated_level)
        self.effort_units = compute_gap_effort(estimated_level, required_level)
        self.base_priority = self._calculate_base_priority()
        self.priority_tier = self._assign_tier()
        self.rationale = self._generate_rationale()

    def _calculate_base_priority(self) -> float:
        req_mult = IS_REQUIRED_FACTOR if self.is_required else IS_PREFERRED_FACTOR
        rel_mult = INTERVIEW_RELEVANCE_MULTIPLIERS.get(self.interview_relevance, 1.0)

        if self.gap_levels > 0:
            # Formula: (Gap * Weight * ReqFactor * Relevance) / sqrt(Effort)
            numerator = float(self.gap_levels) * self.importance_weight * req_mult * rel_mult
            denominator = max(0.5, self.effort_units) ** 0.5
            return round(numerator / denominator, 4)
        else:
            # Skills meeting target: lower baseline for revision/maintenance
            # Low confidence triggers validation priority, but remains lower than real gaps
            if self.confidence_score == "low":
                return round(0.18 * self.importance_weight * rel_mult, 4)
            return round(0.08 * self.importance_weight * rel_mult, 4)

    def _assign_tier(self) -> str:
        if self.gap_levels >= 2 or (self.gap_levels >= 1 and self.importance_weight >= 0.85):
            return "high"
        elif self.gap_levels == 1:
            return "medium"
        else:
            return "maintenance"

    def _generate_rationale(self) -> str:
        if self.gap_levels > 0:
            urgency = "Critical gap" if self.priority_tier == "high" else "Moderate gap"
            req_label = "required" if self.is_required else "preferred"
            return (
                f"{urgency}: Modeled {req_label} requirement is Level {self.required_level}, "
                f"while evidence supports Level {self.estimated_level} ({self.interview_relevance} interview relevance)."
            )
        elif self.confidence_score == "low":
            return (
                f"Meets modeled Level {self.required_level}, but evidence confidence is low. "
                f"Recommended quick validation/assessment task."
            )
        else:
            return (
                f"Current capability meets modeled requirement (Level {self.estimated_level} / {self.required_level}). "
                f"Recommended periodic revision and maintenance."
            )

class GapPrioritizer:
    @staticmethod
    def prioritize_gaps(items: List[CandidateSkillGap]) -> List[CandidateSkillGap]:
        """Return skills sorted deterministically by base priority descending."""
        return sorted(items, key=lambda x: (x.base_priority, x.gap_levels, x.importance_weight), reverse=True)
