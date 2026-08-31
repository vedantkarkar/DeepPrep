"""Centralized job parsing rules, baseline requirement levels, weights, and provenance definitions.

All numeric constants are named and documented. No magic numbers allowed.
"""

from typing import Dict, List

# Target role families recognized by DeepPrep
SUPPORTED_TARGET_ROLES: List[str] = [
    "Software Engineer",
    "Backend Engineer",
    "Full Stack Engineer",
    "AI/ML Engineer",
    "Data Engineer",
]

# ---------------------------------------------------------------------------
# 1. Baseline Required Proficiency Levels (1 to 5)
# Represents the expected proficiency standard modeled by DeepPrep.
# ---------------------------------------------------------------------------
DEFAULT_REQUIRED_COMPETENCY_LEVEL: int = 3   # Competent / Project-Ready
DEFAULT_ADVANCED_COMPETENCY_LEVEL: int = 4   # Deep / Production-Capable
DEFAULT_PREFERRED_COMPETENCY_LEVEL: int = 2  # Elementary / Familiarity

# Keywords triggering advanced level (Level 4)
ADVANCED_LEVEL_KEYWORDS: List[str] = [
    "expert", "deep expertise", "advanced", "in-depth", "mastery", "extensive experience"
]

# ---------------------------------------------------------------------------
# 2. Baseline Importance Weights (0.1 to 1.0)
# ---------------------------------------------------------------------------
WEIGHT_CORE_INTERVIEW_SKILL: float = 1.00   # DSA, Core Primary Language, System Design
WEIGHT_STANDARD_REQUIRED_SKILL: float = 0.85 # Frameworks, Databases (Spring Boot, PostgreSQL, SQL)
WEIGHT_SECONDARY_REQUIRED_SKILL: float = 0.70 # Testing, OS, Networking, Git
WEIGHT_PREFERRED_SKILL: float = 0.60         # Docker, AWS, Redis, Kafka (when preferred)

# Core interview skill slugs receiving 1.0 weight and high interview relevance by default
CORE_INTERVIEW_SKILL_SLUGS: List[str] = [
    "dsa", "java", "cpp", "python", "system-design", "oop"
]

# ---------------------------------------------------------------------------
# 3. Provenance and Source Types
# ---------------------------------------------------------------------------
SOURCE_TYPES: List[str] = [
    "fixture",
    "direct_company",
    "job_board",
    "manual_entry",
]

PROVENANCE_EXTRACTED: str = "extracted_from_jd"
PROVENANCE_CURATED: str = "curated"
PROVENANCE_DERIVED: str = "derived"

# ---------------------------------------------------------------------------
# 4. Validation Bounds
# ---------------------------------------------------------------------------
MIN_PROFICIENCY_LEVEL: int = 1
MAX_PROFICIENCY_LEVEL: int = 5
MIN_IMPORTANCE_WEIGHT: float = 0.10
MAX_IMPORTANCE_WEIGHT: float = 1.00
