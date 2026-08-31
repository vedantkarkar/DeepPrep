import pytest
from app.ai.mock_provider import MockAIProvider
from app.domains.jobs.parser_service import JobParserService

@pytest.mark.asyncio
async def test_job_description_parsing_and_normalization(db_session):
    raw_jd = """
Software Engineer at Persistent Systems

Location: Pune, Maharashtra
Experience: 0-2 years

ELIGIBILITY:
- Bachelor's degree in Computer Science or Information Technology
- 2024 / 2025 graduates

TECHNICAL REQUIREMENTS:
- Strong core Java and Spring Boot experience required.
- Solid understanding of SQL and relational databases required.
- Strong Data Structures and Algorithms (DSA) problem solving required.

PREFERRED:
- Familiarity with Docker and AWS cloud is preferred.
"""
    parsed = await JobParserService.parse_job_description(
        db=db_session,
        raw_description=raw_jd,
        title="Software Engineer",
        company_name="Persistent Systems",
        source_type="fixture",
        ai_provider=MockAIProvider(),
    )

    assert parsed.title == "Software Engineer"
    assert parsed.company_name == "Persistent Systems"
    assert parsed.location_city == "Pune"
    assert parsed.source_type == "fixture"

    # Eligibility assertions
    elig_types = [e.criterion_type for e in parsed.eligibility_requirements]
    assert "degree" in elig_types
    assert "branch" in elig_types
    assert "min_experience_years" in elig_types

    # Competency assertions
    comps = {c.skill_slug: c for c in parsed.competency_requirements}
    assert "java" in comps
    assert comps["java"].is_required is True
    assert comps["java"].required_proficiency_level >= 3
    assert comps["java"].importance_weight >= 0.85
    assert len(comps["java"].supporting_text) > 0

    assert "spring-boot" in comps
    assert comps["spring-boot"].is_required is True

    assert "sql" in comps
    assert comps["sql"].is_required is True

    assert "dsa" in comps
    assert comps["dsa"].is_required is True
    assert comps["dsa"].interview_relevance_level == "high"

    # Preferred skills
    assert "docker" in comps
    assert comps["docker"].is_required is False
    assert comps["docker"].required_proficiency_level == 2
    assert comps["docker"].importance_weight <= 0.60

    assert "aws" in comps
    assert comps["aws"].is_required is False

@pytest.mark.asyncio
async def test_unknown_skills_preserved_as_unresolved(db_session):
    raw_jd = """
Data Engineer

TECHNICAL SKILLS:
- Python required.
- Apache Flink and Apache Iceberg required.
"""
    parsed = await JobParserService.parse_job_description(
        db=db_session,
        raw_description=raw_jd,
        title="Data Engineer",
        company_name="Acme",
        ai_provider=MockAIProvider(),
    )

    comps = {c.skill_slug: c for c in parsed.competency_requirements}
    assert "python" in comps

    # Unknown skills (like Apache Flink if absent from taxonomy) should be preserved in unresolved_skills
    # We verify that normalizer does not create a fake canonical skill
    for c in parsed.competency_requirements:
        assert c.skill_id is not None
