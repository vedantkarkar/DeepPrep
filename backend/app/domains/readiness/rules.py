"""Centralized rules and constants for the Deterministic Readiness Engine."""

# Weight factor applied to preferred (non-mandatory) competencies
PREFERRED_SKILL_WEIGHT_FACTOR: float = 0.70

# Minimum level to qualify as a demonstrable strength
MIN_STRENGTH_LEVEL: int = 2

# Thresholds for Critical Gap classification
CRITICAL_GAP_WEIGHT_THRESHOLD: float = 0.85
CRITICAL_GAP_RAW_DEFICIT_THRESHOLD: int = 2

# Overall Evidence Confidence Classification Thresholds
OVERALL_CONFIDENCE_MEDIUM_THRESHOLD: float = 0.45
OVERALL_CONFIDENCE_HIGH_THRESHOLD: float = 0.75
