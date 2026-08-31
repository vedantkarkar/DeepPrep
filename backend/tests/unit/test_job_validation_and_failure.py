import pytest
from uuid import uuid4
from pydantic import ValidationError
from app.domains.jobs.validator import JobSemanticValidator, JobValidationError
from app.domains.jobs.schemas import (
    NormalizedCompetencyItem,
    ExtractedEligibilityItem,
)
from app.domains.jobs.parser_service import JobParserService

@pytest.mark.asyncio
async def test_empty_raw_description_rejected(db_session):
    with pytest.raises(ValueError, match="cannot be empty"):
        await JobParserService.parse_job_description(
            db=db_session,
            raw_description="   ",
        )

def test_invalid_proficiency_level_rejected():
    with pytest.raises((ValidationError, JobValidationError)):
        NormalizedCompetencyItem(
            skill_id=uuid4(),
            skill_slug="java",
            canonical_name="Java",
            category="programming",
            required_proficiency_level=6, # Invalid: must be <= 5
            importance_weight=0.8,
            is_required=True,
        )

def test_invalid_importance_weight_rejected():
    with pytest.raises((ValidationError, JobValidationError)):
        NormalizedCompetencyItem(
            skill_id=uuid4(),
            skill_slug="java",
            canonical_name="Java",
            category="programming",
            required_proficiency_level=3,
            importance_weight=1.5, # Invalid: must be <= 1.0
            is_required=True,
        )

def test_invalid_eligibility_criterion_rejected():
    invalid_elig = ExtractedEligibilityItem(
        criterion_type="favorite_color", # Invalid
        expected_value="blue",
        operator="EQUALS",
    )
    with pytest.raises(JobValidationError, match="Unsupported eligibility criterion"):
        JobSemanticValidator.validate_eligibility(invalid_elig)
