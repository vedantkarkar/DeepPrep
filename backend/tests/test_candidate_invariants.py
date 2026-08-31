import pytest
from pydantic import ValidationError
from app.models import CandidateSkill
from app.schemas.candidate import (
    CandidateCreateRequest,
    CandidateSkillClaimCreate,
    EducationConfirmRequest,
)

def test_candidate_skill_claim_does_not_have_proficiency_field():
    # Invariant check: The model must NOT store a proficiency attribute on claim
    assert not hasattr(CandidateSkill, "proficiency")
    assert hasattr(CandidateSkill, "self_assessment_level")

def test_self_assessment_pydantic_validation():
    # Valid self-assessment 1-5
    valid_claim = CandidateSkillClaimCreate(
        skill_slug="python",
        self_assessment_level=4,
        claim_source="resume"
    )
    assert valid_claim.self_assessment_level == 4

    # Invalid self-assessment > 5
    with pytest.raises(ValidationError):
        CandidateSkillClaimCreate(
            skill_slug="python",
            self_assessment_level=6
        )

    # Invalid self-assessment < 1
    with pytest.raises(ValidationError):
        CandidateSkillClaimCreate(
            skill_slug="python",
            self_assessment_level=0
        )

def test_candidate_create_optional_email():
    req = CandidateCreateRequest(full_name="Aarav Test")
    assert req.email is None
    assert req.location_city == "Pune"

def test_education_confirmation_schema():
    edu = EducationConfirmRequest(
        degree="B.Tech",
        branch="Computer Science",
        institution="COEP Pune",
        graduation_year=2025,
        student_status="final_year",
        confirmed=True
    )
    assert edu.confirmed is True
    assert edu.graduation_year == 2025
