from app.domains.readiness import rules

def classify_skill_gap(
    required_level: int,
    estimated_level: int,
    is_required: bool,
    effective_weight: float,
    interview_relevance: str,
) -> str:
    """Classifies a skill outcome into strength, aligned, moderate_gap, or critical_gap."""
    raw_gap = max(0, required_level - estimated_level)

    if raw_gap == 0:
        if estimated_level >= rules.MIN_STRENGTH_LEVEL and estimated_level >= required_level:
            return "strength"
        return "aligned"

    # Critical gap criteria
    if is_required:
        if raw_gap >= rules.CRITICAL_GAP_RAW_DEFICIT_THRESHOLD:
            return "critical_gap"
        if interview_relevance.lower() == "high":
            return "critical_gap"
        if effective_weight >= rules.CRITICAL_GAP_WEIGHT_THRESHOLD:
            return "critical_gap"
        if estimated_level == 0 and effective_weight >= 0.70:
            return "critical_gap"

    return "moderate_gap"
