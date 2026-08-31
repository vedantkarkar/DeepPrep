from datetime import date
from typing import Dict, Any, Tuple
from app.models.evidence import CandidateEvidence
from app.domains.evidence import rules

def calculate_recency_factor(date_obtained: date | None, reference_date: date | None = None) -> float:
    """Calculates deterministic recency factor based on age of evidence.
    
    If date_obtained is omitted, returns neutral default factor (0.85).
    """
    if date_obtained is None:
        return rules.RECENCY_FACTOR_DEFAULT

    if reference_date is None:
        reference_date = date.today()

    age_days = (reference_date - date_obtained).days
    if age_days < 0:
        age_days = 0 # Future dates treated as fresh/current

    if age_days <= rules.RECENCY_DAYS_TIER_1:
        return rules.RECENCY_FACTOR_TIER_1
    elif age_days <= rules.RECENCY_DAYS_TIER_2:
        return rules.RECENCY_FACTOR_TIER_2
    elif age_days <= rules.RECENCY_DAYS_TIER_3:
        return rules.RECENCY_FACTOR_TIER_3
    else:
        return rules.RECENCY_FACTOR_OLD

def extract_metadata_depth_bonus(evidence_type: str, metadata: Dict[str, Any]) -> float:
    """Calculates deterministic practical depth bonus from structured evidence metadata."""
    bonus = 0.0
    if not metadata:
        return bonus

    if evidence_type == "assessment":
        total_solved = metadata.get("total_solved", 0)
        contest_rating = metadata.get("contest_rating", 0)
        if total_solved >= 150 or contest_rating >= 1600:
            bonus += 0.15
        elif total_solved >= 50 or contest_rating >= 1400:
            bonus += 0.08
    elif evidence_type in ("project", "github"):
        commits = metadata.get("commits", 0)
        stars = metadata.get("stars", 0)
        if commits >= 25 or stars >= 5:
            bonus += 0.10
        elif commits >= 10:
            bonus += 0.05
    elif evidence_type == "course":
        hours = metadata.get("hours", 0)
        if hours >= 20:
            bonus += 0.05

    return min(bonus, 0.20) # Cap individual depth bonus at +0.20

def evaluate_evidence_item(evidence: CandidateEvidence, reference_date: date | None = None) -> Tuple[float, float]:
    """Evaluates a single CandidateEvidence record.
    
    Returns:
        (effective_strength, effective_confidence)
    """
    ev_type = evidence.evidence_type.lower()
    base_strength = rules.BASE_EVIDENCE_STRENGTHS.get(ev_type, rules.BASE_EVIDENCE_STRENGTHS["other"])
    depth_bonus = extract_metadata_depth_bonus(ev_type, evidence.raw_metadata or {})
    
    v_status = (evidence.verification_status or "unverified").lower()
    v_mult = rules.VERIFICATION_MULTIPLIERS.get(v_status, rules.VERIFICATION_MULTIPLIERS["unverified"])
    
    recency_factor = calculate_recency_factor(evidence.date_obtained, reference_date)
    
    # Effective strength formula
    effective_strength = (base_strength + depth_bonus) * v_mult * recency_factor
    
    # Effective confidence formula
    base_conf = evidence.confidence_score if evidence.confidence_score is not None else 0.50
    effective_confidence = base_conf * v_mult * recency_factor
    
    return effective_strength, effective_confidence
