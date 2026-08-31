from typing import List
from app.domains.jobs.schemas import (
    ParsedJobDescriptionResponse,
    NormalizedCompetencyItem,
    ExtractedEligibilityItem,
)
from app.domains.jobs import rules

class JobValidationError(Exception):
    """Raised when job description fails semantic or structural validation."""
    pass

class JobSemanticValidator:
    """Validates structured job requirements against product constraints."""

    @classmethod
    def validate_parsed_job(cls, parsed: ParsedJobDescriptionResponse) -> None:
        if not parsed.title or not parsed.title.strip():
            raise JobValidationError("Job title cannot be empty.")

        if not parsed.company_name or not parsed.company_name.strip():
            raise JobValidationError("Company name cannot be empty.")

        if not parsed.raw_description or not parsed.raw_description.strip():
            raise JobValidationError("Raw job description cannot be empty.")

        # Validate competencies
        for comp in parsed.competency_requirements:
            cls.validate_competency(comp)

        # Validate eligibility
        for elig in parsed.eligibility_requirements:
            cls.validate_eligibility(elig)

    @classmethod
    def validate_competency(cls, comp: NormalizedCompetencyItem) -> None:
        if not (rules.MIN_PROFICIENCY_LEVEL <= comp.required_proficiency_level <= rules.MAX_PROFICIENCY_LEVEL):
            raise JobValidationError(
                f"Proficiency level {comp.required_proficiency_level} for '{comp.canonical_name}' "
                f"must be within [{rules.MIN_PROFICIENCY_LEVEL}, {rules.MAX_PROFICIENCY_LEVEL}]."
            )

        if not (rules.MIN_IMPORTANCE_WEIGHT <= comp.importance_weight <= rules.MAX_IMPORTANCE_WEIGHT):
            raise JobValidationError(
                f"Importance weight {comp.importance_weight} for '{comp.canonical_name}' "
                f"must be within [{rules.MIN_IMPORTANCE_WEIGHT}, {rules.MAX_IMPORTANCE_WEIGHT}]."
            )

    @classmethod
    def validate_eligibility(cls, elig: ExtractedEligibilityItem) -> None:
        valid_criteria = [
            "degree", "branch", "min_experience_years", "max_experience_years",
            "min_graduation_year", "max_graduation_year", "location_constraint"
        ]
        if elig.criterion_type.lower() not in valid_criteria:
            raise JobValidationError(
                f"Unsupported eligibility criterion '{elig.criterion_type}'. Valid: {valid_criteria}"
            )

        valid_ops = ["EQUALS", "IN", "GREATER_EQUAL", "LESS_EQUAL", "CONTAINS"]
        if (elig.operator or "").upper() not in valid_ops:
            raise JobValidationError(
                f"Unsupported eligibility operator '{elig.operator}'. Valid: {valid_ops}"
            )
