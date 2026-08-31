"""
Centralized Configuration and Planning Rules for the DeepPrep Preparation Optimizer.

All heuristics, multipliers, diminishing return parameters, and capacity constraints
are explicitly defined here without hidden magic numbers.

IMPORTANT:
These are MVP planning heuristics intended to prioritize preparation based on evidence,
not predict guaranteed learning outcomes or hiring probabilities.
"""

from typing import Dict

# ---------------------------------------------------------------------------
# 1. LEARNING EFFORT MODEL (Proficiency Transition Effort Units)
# ---------------------------------------------------------------------------
# Defines the estimated difficulty/effort units required to advance between levels.
# Advancing from Level 0 to 1 is foundational; advancing from Level 3 to 4 requires deep mastery.
EFFORT_TRANSITION_UNITS: Dict[int, float] = {
    0: 1.0,  # Level 0 -> Level 1 (Foundational syntax, concepts)
    1: 1.5,  # Level 1 -> Level 2 (Elementary application, basic coursework)
    2: 2.0,  # Level 2 -> Level 3 (Competent implementation, project-ready)
    3: 3.0,  # Level 3 -> Level 4 (Production-capable, advanced nuances)
    4: 4.0,  # Level 4 -> Level 5 (Deep expert / architect mastery)
}

# ---------------------------------------------------------------------------
# 2. REQUIREMENT IMPORTANCE & RELEVANCE MULTIPLIERS
# ---------------------------------------------------------------------------
# Multiplier based on whether a skill is mandatory for the role or preferred
IS_REQUIRED_FACTOR = 1.00
IS_PREFERRED_FACTOR = 0.65

# Multipliers based on live interview evaluation focus
INTERVIEW_RELEVANCE_MULTIPLIERS: Dict[str, float] = {
    "high": 1.25,    # Core interview focus (DSA, System Design, Primary Language)
    "medium": 1.00,  # Standard technical domain (Frameworks, Databases)
    "low": 0.80,     # Secondary / auxiliary competencies (Tools, DevOps)
}

# Evidence confidence modifier for validation tasks
# If candidate has estimated capability but confidence is low, assign assessment tasks
LOW_CONFIDENCE_VALIDATION_FACTOR = 0.85

# ---------------------------------------------------------------------------
# 3. DIMINISHING RETURNS PARAMETERS
# ---------------------------------------------------------------------------
# Prevents over-allocating preparation hours to a single skill at the expense of other gaps.
# Marginal utility formula: Priority / (1.0 + DIMINISHING_RETURN_DECAY_RATE * (Allocated Hours / Effort Units))
DIMINISHING_RETURN_DECAY_RATE = 0.35

# ---------------------------------------------------------------------------
# 4. CAPACITY & GRANULARITY CONSTRAINTS
# ---------------------------------------------------------------------------
# Planning granularity in hours (minimum practical preparation chunk)
MINIMUM_ALLOCATION_UNIT_HOURS = 1.0

# Maximum fraction of total time that can be dedicated to maintenance of already-strong skills
MAX_MAINTENANCE_TIME_RATIO = 0.15

# Maximum fraction of total time that any single skill can consume
MAX_SINGLE_SKILL_TIME_RATIO = 0.40

# Fraction of final week reserved for mock assessment, review, and consolidation
FINAL_WEEK_REVIEW_RATIO = 0.25

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def compute_gap_effort(estimated_level: int, required_level: int) -> float:
    """Compute total heuristic effort units required to bridge proficiency gap."""
    if estimated_level >= required_level:
        return 0.5  # Minimal effort for maintenance
    total_effort = 0.0
    for level in range(estimated_level, required_level):
        total_effort += EFFORT_TRANSITION_UNITS.get(level, 2.0)
    return max(0.5, total_effort)
