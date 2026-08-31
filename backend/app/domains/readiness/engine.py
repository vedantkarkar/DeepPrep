from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.models.candidate import Candidate, CandidateSkill
from app.models.evidence import CandidateEvidence
from app.models.job import Job, JobEligibilityRequirement, JobCompetencyRequirement
from app.models.readiness import ReadinessReport, ReadinessItemBreakdown
from app.models.session import PreparationSession

from app.domains.evidence.proficiency import ProficiencyEstimator, ProficiencyEstimate
from app.domains.eligibility.evaluator import EligibilityEvaluator, EligibilityResult
from app.domains.readiness import rules
from app.domains.readiness.classification import classify_skill_gap

@dataclass
class ReadinessEvaluationResult:
    overall_readiness_score: int # 0 to 100
    technical_readiness_score: int # 0 to 100
    evidence_confidence_score: str # low, medium, high
    eligibility_status: str # eligible, partially_eligible, ineligible
    eligibility_details: Dict[str, Any]
    strengths_summary: List[str]
    critical_gaps_summary: List[Dict[str, Any]]
    item_breakdowns: List[Dict[str, Any]]

class ReadinessEngine:
    """Pure deterministic Readiness Engine.
    
    Evaluates candidate claims, evidence, and eligibility against structured
    job requirements without any probabilistic or non-deterministic components.
    """

    @classmethod
    def evaluate(
        cls,
        candidate: Candidate,
        job: Job,
        candidate_evidence: List[CandidateEvidence],
        candidate_skills: Optional[List[CandidateSkill]] = None,
    ) -> ReadinessEvaluationResult:
        # 1. Evaluate Eligibility
        eligibility_res: EligibilityResult = EligibilityEvaluator.evaluate(
            candidate=candidate,
            requirements=job.eligibility_requirements or [],
        )

        # 2. Group candidate evidence by skill_id
        evidence_by_skill: Dict[UUID, List[CandidateEvidence]] = {}
        for ev in candidate_evidence:
            evidence_by_skill.setdefault(ev.skill_id, []).append(ev)

        # 3. Evaluate Competencies
        total_contribution = 0.0
        total_maximum = 0.0
        total_weighted_confidence = 0.0
        total_weight_sum = 0.0

        item_breakdowns: List[Dict[str, Any]] = []
        strengths_summary: List[str] = []
        critical_gaps_summary: List[Dict[str, Any]] = []

        competencies = job.competency_requirements or []
        for comp in competencies:
            skill = comp.skill
            skill_slug = skill.slug if skill else "unknown"
            canonical_name = skill.canonical_name if skill else "Unknown Skill"
            category = skill.category if skill else "other"

            # Estimate proficiency from evidence
            ev_list = evidence_by_skill.get(comp.skill_id, [])
            estimate: ProficiencyEstimate = ProficiencyEstimator.estimate(
                skill_slug=skill_slug,
                evidence_items=ev_list,
            )

            # Effective weight based on required vs preferred status
            base_weight = comp.importance_weight if comp.importance_weight is not None else 1.0
            if comp.is_required:
                effective_weight = base_weight
            else:
                effective_weight = base_weight * rules.PREFERRED_SKILL_WEIGHT_FACTOR

            required_level = comp.required_proficiency_level
            estimated_level = estimate.estimated_level

            # Bounded contribution formula (Section 23)
            capped_achieved_level = min(estimated_level, required_level)
            item_contribution = effective_weight * capped_achieved_level
            item_maximum = effective_weight * required_level

            total_contribution += item_contribution
            total_maximum += item_maximum

            # Weighted confidence accumulation
            total_weighted_confidence += effective_weight * estimate.confidence_score
            total_weight_sum += effective_weight

            # Gap calculation (Section 26)
            raw_gap = max(0, required_level - estimated_level)
            weighted_gap = raw_gap * effective_weight

            # Gap classification (Section 27)
            relevance = comp.interview_relevance_level or "medium"
            classification = classify_skill_gap(
                required_level=required_level,
                estimated_level=estimated_level,
                is_required=comp.is_required,
                effective_weight=effective_weight,
                interview_relevance=relevance,
            )

            # Construct explainable deterministic breakdown text (Section 31)
            if classification == "strength":
                explanation = (
                    f"Candidate demonstrates Level {estimated_level} proficiency "
                    f"(Target: Level {required_level}). Strong capability with verified evidence."
                )
                strengths_summary.append(
                    f"{canonical_name} (Level {estimated_level} / Required {required_level})"
                )
            elif classification == "aligned":
                explanation = (
                    f"Candidate meets role expectation at Level {estimated_level} "
                    f"(Required: Level {required_level})."
                )
            elif classification == "critical_gap":
                explanation = (
                    f"Critical Gap: Required Level {required_level}, Estimated Level {estimated_level}. "
                    f"Deficit of {raw_gap} level(s) on a high-priority requirement (Weight: {effective_weight:.2f}, Interview: {relevance})."
                )
                critical_gaps_summary.append({
                    "skill_slug": skill_slug,
                    "canonical_name": canonical_name,
                    "required_level": required_level,
                    "estimated_level": estimated_level,
                    "raw_gap": raw_gap,
                    "weighted_gap": round(weighted_gap, 2),
                    "importance_weight": round(effective_weight, 2),
                    "interview_relevance": relevance,
                    "reason": explanation,
                })
            else: # moderate_gap
                explanation = (
                    f"Moderate Gap: Required Level {required_level}, Estimated Level {estimated_level}. "
                    f"Deficit of {raw_gap} level(s) with weighted gap score of {weighted_gap:.2f}."
                )

            item_breakdowns.append({
                "skill_id": comp.skill_id,
                "skill_slug": skill_slug,
                "canonical_name": canonical_name,
                "category": category,
                "competency_requirement_id": comp.id,
                "required_level": required_level,
                "estimated_level": estimated_level,
                "importance_weight": round(effective_weight, 2),
                "gap_score": round(weighted_gap, 2),
                "classification": classification,
                "supporting_evidence_ids": estimate.supporting_evidence_ids,
                "confidence_score": estimate.confidence_score,
                "confidence_label": estimate.confidence_label,
                "explanation": explanation,
            })

        # Calculate Overall Competency Readiness Score (0 to 100)
        if total_maximum > 0:
            readiness_score = int(round((total_contribution / total_maximum) * 100))
        else:
            readiness_score = 100 # Edge case: no competencies requested

        # Bound score between 0 and 100
        readiness_score = max(0, min(100, readiness_score))

        # Overall Evidence Confidence Score
        if total_weight_sum > 0:
            avg_conf = total_weighted_confidence / total_weight_sum
        else:
            avg_conf = 0.0

        if avg_conf >= rules.OVERALL_CONFIDENCE_HIGH_THRESHOLD:
            overall_confidence_label = "high"
        elif avg_conf >= rules.OVERALL_CONFIDENCE_MEDIUM_THRESHOLD:
            overall_confidence_label = "medium"
        else:
            overall_confidence_label = "low"

        eligibility_details = {
            "status": eligibility_res.status.value,
            "is_eligible": eligibility_res.is_eligible,
            "reasons": eligibility_res.summary_reasons,
            "criteria": [
                {
                    "criterion_type": ce.criterion_type,
                    "expected_value": ce.expected_value,
                    "candidate_value": ce.candidate_value,
                    "operator": ce.operator,
                    "is_mandatory": ce.is_mandatory,
                    "passed": ce.passed,
                    "explanation": ce.explanation,
                }
                for ce in eligibility_res.criteria_evaluations
            ],
        }

        return ReadinessEvaluationResult(
            overall_readiness_score=readiness_score,
            technical_readiness_score=readiness_score,
            evidence_confidence_score=overall_confidence_label,
            eligibility_status=eligibility_res.status.value,
            eligibility_details=eligibility_details,
            strengths_summary=strengths_summary,
            critical_gaps_summary=critical_gaps_summary,
            item_breakdowns=item_breakdowns,
        )
