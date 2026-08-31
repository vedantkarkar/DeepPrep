import pytest
from app.ai.mock_provider import MockAIProvider
from app.domains.candidate.resume_service import ResumeExtractionService
from app.domains.candidate.schemas import RawResumeExtraction

@pytest.mark.asyncio
async def test_resume_extraction_and_normalization(db_session):
    with open("data/resumes/demo_resume.txt", "rb") as f:
        content = f.read()

    res = await ResumeExtractionService.extract_and_normalize(
        db=db_session,
        file_bytes=content,
        filename="demo_resume.txt",
        ai_provider=MockAIProvider(),
    )

    assert res.status == "needs_confirmation"
    assert res.candidate_name == "AARAV DESHMUKH"
    assert res.email == "aarav.deshmukh@example.com"
    assert res.education_status in ["extracted", "ambiguous"]
    assert len(res.education_claims) >= 1
    assert res.education_claims[0].degree == "B.Tech"

    # Verify normalized skills
    slugs = [s.skill_slug for s in res.normalized_skill_claims]
    assert "cpp" in slugs
    assert "java" in slugs
    assert "python" in slugs
    assert "postgresql" in slugs
    assert "spring-boot" in slugs
    assert "dsa" in slugs

    # Verify all claims are unconfirmed initially
    for sc in res.normalized_skill_claims:
        assert sc.confirmed is False

@pytest.mark.asyncio
async def test_missing_education_not_hallucinated(db_session):
    text_without_edu = """
JOHN DOE
john.doe@example.com | +91 99999 11111

TECHNICAL SKILLS:
Python, SQL, FastApi

PROJECTS:
Inventory Service in FastAPI
"""
    res = await ResumeExtractionService.extract_and_normalize(
        db=db_session,
        file_bytes=text_without_edu.encode("utf-8"),
        filename="no_edu.txt",
        ai_provider=MockAIProvider(),
    )

    assert res.education_status == "missing"
    assert len(res.education_claims) == 0
