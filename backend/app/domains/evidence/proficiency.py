from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID
from app.models.evidence import CandidateEvidence
from app.domains.evidence import rules
from app.domains.evidence.evaluator import evaluate_evidence_item

@dataclass
class ProficiencyEstimate:
    skill_slug: str
    estimated_level: int # 0 to 5
    confidence_score: float # 0.0 to 1.0
    confidence_label: str # low, medium, high
    supporting_evidence_ids: List[UUID] = field(default_factory=list)
    explanation: str = ""
    aggregate_strength: float = 0.0

class ProficiencyEstimator:
    """Pure deterministic proficiency estimator.
    
    Transforms evaluated evidence records for a given skill into a bounded
    evidence-backed proficiency level (0-5) and confidence classification.
    """

    @classmethod
    def estimate(
        cls,
        skill_slug: str,
        evidence_items: List[CandidateEvidence],
    ) -> ProficiencyEstimate:
        # Invariant 1: No evidence -> Level 0 (Unknown)
        if not evidence_items:
            return ProficiencyEstimate(
                skill_slug=skill_slug,
                estimated_level=0,
                confidence_score=0.0,
                confidence_label="low",
                supporting_evidence_ids=[],
                explanation="No supporting evidence found. Estimated proficiency is Level 0 (Unknown).",
                aggregate_strength=0.0,
            )

        # Evaluate individual items
        evaluated_items = []
        for ev in evidence_items:
            strength, conf = evaluate_evidence_item(ev)
            evaluated_items.append({
                "id": ev.id,
                "evidence_type": ev.evidence_type.lower(),
                "title": ev.title,
                "strength": strength,
                "confidence": conf,
            })

        # Sort descending by individual strength
        evaluated_items.sort(key=lambda x: x["strength"], reverse=True)

        # Invariant 12: Bounded diminishing returns aggregation
        weights = [
            rules.AGGREGATION_WEIGHT_PRIMARY,
            rules.AGGREGATION_WEIGHT_SECONDARY,
            rules.AGGREGATION_WEIGHT_TERTIARY,
        ]
        
        aggregate_strength = 0.0
        for i, item in enumerate(evaluated_items):
            w = weights[i] if i < len(weights) else rules.AGGREGATION_WEIGHT_SUBSEQUENT
            aggregate_strength += item["strength"] * w

        # Invariant 16: Category ceiling cap based on strongest evidence type present
        max_allowed_cap = max(
            rules.MAX_LEVEL_CAP_BY_TYPE.get(item["evidence_type"], 2)
            for item in evaluated_items
        )

        # Map aggregate strength to level
        if aggregate_strength >= rules.LEVEL_5_MIN_STRENGTH:
            uncapped_level = 5
        elif aggregate_strength >= rules.LEVEL_4_MIN_STRENGTH:
            uncapped_level = 4
        elif aggregate_strength >= rules.LEVEL_3_MIN_STRENGTH:
            uncapped_level = 3
        elif aggregate_strength >= rules.LEVEL_2_MIN_STRENGTH:
            uncapped_level = 2
        elif aggregate_strength >= rules.LEVEL_1_MIN_STRENGTH:
            uncapped_level = 1
        else:
            uncapped_level = 0

        estimated_level = min(uncapped_level, max_allowed_cap)

        # Invariant 15: Separate Confidence calculation
        avg_item_conf = sum(item["confidence"] for item in evaluated_items) / len(evaluated_items)
        unique_types = len(set(item["evidence_type"] for item in evaluated_items))
        
        # Diversity and quantity multiplier
        if len(evaluated_items) == 1:
            diversity_mult = 0.75
        elif unique_types >= 2:
            diversity_mult = 1.00 # Multi-source diversity bonus
        else:
            diversity_mult = 0.85 # Multiple items of same type

        aggregate_confidence = min(1.0, avg_item_conf * diversity_mult)
        
        if aggregate_confidence >= rules.CONFIDENCE_THRESHOLD_HIGH:
            confidence_label = "high"
        elif aggregate_confidence >= rules.CONFIDENCE_THRESHOLD_MEDIUM:
            confidence_label = "medium"
        else:
            confidence_label = "low"

        # Construct deterministic explanation
        supporting_ids = [item["id"] for item in evaluated_items]
        types_summary = ", ".join(sorted(set(item["evidence_type"] for item in evaluated_items)))
        
        if uncapped_level > max_allowed_cap:
            explanation = (
                f"Derived from {len(evaluated_items)} evidence item(s) ({types_summary}). "
                f"Capped at Level {max_allowed_cap} due to evidence type constraints (Requires practical/professional evidence to exceed)."
            )
        else:
            explanation = (
                f"Derived from {len(evaluated_items)} evidence item(s) ({types_summary}) "
                f"with aggregate strength score of {aggregate_strength:.2f}."
            )

        return ProficiencyEstimate(
            skill_slug=skill_slug,
            estimated_level=estimated_level,
            confidence_score=round(aggregate_confidence, 2),
            confidence_label=confidence_label,
            supporting_evidence_ids=supporting_ids,
            explanation=explanation,
            aggregate_strength=round(aggregate_strength, 2),
        )
