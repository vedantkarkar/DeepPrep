"""Centralized evidence evaluation rules, base constants, and proficiency thresholds.

Every numeric parameter is named and documented. No magic numbers are permitted.
"""

from typing import Dict

# ---------------------------------------------------------------------------
# 1. Base Evidence Strengths (0.0 to 1.0 scale)
# Represents intrinsic evidentiary value of the evidence category.
# ---------------------------------------------------------------------------
BASE_EVIDENCE_STRENGTHS: Dict[str, float] = {
    "self_report": 0.15,            # Unsubstantiated personal claim
    "other": 0.20,                  # Miscellaneous/unspecified evidence
    "course": 0.35,                 # Completed online/offline video course
    "academic_coursework": 0.40,    # University classroom coursework & exams
    "certification": 0.50,          # Externally proctored certification
    "project": 0.65,                # Concrete software build / implementation
    "github": 0.65,                 # Version-controlled code repository
    "assessment": 0.70,             # Algorithmic/technical platform testing (e.g. LeetCode)
    "internship": 0.85,             # Real-world industry workplace experience
    "professional_experience": 0.95 # Full-time professional software engineering
}

# ---------------------------------------------------------------------------
# 2. Maximum Proficiency Level Caps by Evidence Type
# Prevents low-rigor evidence from deriving high proficiency levels.
# ---------------------------------------------------------------------------
MAX_LEVEL_CAP_BY_TYPE: Dict[str, int] = {
    "self_report": 1,            # Self-reports can NEVER exceed Level 1 (Basic Awareness)
    "other": 2,                  # Unclassified items capped at Level 2
    "academic_coursework": 2,    # Academic courses without projects capped at Level 2 (Elementary)
    "course": 2,                 # Video courses without practical code capped at Level 2
    "certification": 3,          # Certifications capped at Level 3 (Competent)
    "project": 4,                # Practical projects can support up to Level 4 (Proficient)
    "github": 4,                 # GitHub repositories can support up to Level 4
    "assessment": 4,             # Standard platform assessments support up to Level 4
    "internship": 5,             # Workplace internships can reach Level 5 with sufficient breadth
    "professional_experience": 5 # Professional roles can reach Level 5
}

# ---------------------------------------------------------------------------
# 3. Verification Multipliers
# Scaled by credibility/verification state of the evidence item.
# ---------------------------------------------------------------------------
VERIFICATION_MULTIPLIERS: Dict[str, float] = {
    "unverified": 0.80,    # Candidate entered without verification link or external validation
    "self_attested": 0.90, # Candidate provided institutional context (e.g. course code/grade)
    "verified": 1.00       # Verifiable URL, repository, platform profile, or certificate ID
}

# ---------------------------------------------------------------------------
# 4. Recency Decay Factors
# Evidence ages over time; older evidence carries slightly diminished weight.
# ---------------------------------------------------------------------------
RECENCY_DAYS_TIER_1: int = 365      # <= 1 year old: 100% relevance
RECENCY_FACTOR_TIER_1: float = 1.00

RECENCY_DAYS_TIER_2: int = 730      # 1 to 2 years old: 90% relevance
RECENCY_FACTOR_TIER_2: float = 0.90

RECENCY_DAYS_TIER_3: int = 1095     # 2 to 3 years old: 75% relevance
RECENCY_FACTOR_TIER_3: float = 0.75

RECENCY_FACTOR_OLD: float = 0.60    # > 3 years old: 60% relevance
RECENCY_FACTOR_DEFAULT: float = 0.85 # When date_obtained is omitted (neutral default, no hallucination)

# ---------------------------------------------------------------------------
# 5. Diminishing Returns Aggregation Multipliers
# Prevents gaming the system by submitting many duplicate/similar weak items.
# Items for a single skill are ordered by individual strength descending.
# ---------------------------------------------------------------------------
AGGREGATION_WEIGHT_PRIMARY: float = 1.00   # 1st (strongest) evidence item
AGGREGATION_WEIGHT_SECONDARY: float = 0.50 # 2nd evidence item
AGGREGATION_WEIGHT_TERTIARY: float = 0.25  # 3rd evidence item
AGGREGATION_WEIGHT_SUBSEQUENT: float = 0.10 # 4th and subsequent evidence items

# ---------------------------------------------------------------------------
# 6. Aggregate Strength Thresholds for Proficiency Level (0 to 5)
# ---------------------------------------------------------------------------
LEVEL_0_MAX_STRENGTH: float = 0.10 # Below this is Level 0 (Unknown / No Evidence)
LEVEL_1_MIN_STRENGTH: float = 0.10 # Level 1: Basic Awareness (0.10 <= S < 0.35)
LEVEL_2_MIN_STRENGTH: float = 0.35 # Level 2: Elementary / Academic (0.35 <= S < 0.60)
LEVEL_3_MIN_STRENGTH: float = 0.60 # Level 3: Competent / Project-Ready (0.60 <= S < 0.85)
LEVEL_4_MIN_STRENGTH: float = 0.85 # Level 4: Proficient / Production-Capable (0.85 <= S < 1.10)
LEVEL_5_MIN_STRENGTH: float = 1.10 # Level 5: Advanced Depth / Multi-Source (S >= 1.10)

# ---------------------------------------------------------------------------
# 7. Confidence Thresholds (Low, Medium, High)
# Confidence is computed separately from proficiency level.
# ---------------------------------------------------------------------------
CONFIDENCE_THRESHOLD_MEDIUM: float = 0.45
CONFIDENCE_THRESHOLD_HIGH: float = 0.75
