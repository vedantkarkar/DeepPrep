"""Eligibility evaluation constants and operator definitions."""

from enum import Enum

class EligibilityStatus(str, Enum):
    ELIGIBLE = "eligible"
    PARTIALLY_ELIGIBLE = "partially_eligible"
    INELIGIBLE = "ineligible"

class CriterionType(str, Enum):
    DEGREE = "degree"
    BRANCH = "branch"
    MIN_GRADUATION_YEAR = "min_graduation_year"
    MAX_GRADUATION_YEAR = "max_graduation_year"
    MIN_EXPERIENCE_YEARS = "min_experience_years"
    LOCATION_CONSTRAINT = "location_constraint"

class EvaluationOperator(str, Enum):
    EQUALS = "EQUALS"
    IN = "IN"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS_EQUAL = "LESS_EQUAL"
    CONTAINS = "CONTAINS"
