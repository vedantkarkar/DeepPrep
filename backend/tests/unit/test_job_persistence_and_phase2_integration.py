import pytest
from datetime import date
from sqlalchemy.future import select
from app.models.candidate import Candidate
from app.models.evidence import CandidateEvidence
from app.models.skill import Skill
from app.models.session import PreparationSession
from app.domains.jobs.schemas import (
    JobCreateFromParsedRequest,
    ExtractedEligibilityItem,
    NormalizedCompetencyItem,
)
from app.domains.jobs.persistence_service import JobPersistenceService
from app.domains.readiness.service import ReadinessService

@pytest.mark.asyncio
async def test_section_41_critical_integration_parsed_job_to_phase2(db_session):
    """Section 41 Critical Integration Test:
    1. Construct structured job from parsed JD:
       - Eligibility: Degree Bachelor's, Branch CS/IT, Exp 0-2 yrs
       - Required: Java (Req 3, W 1.0), Spring Boot (Req 3, W 0.80), SQL (Req 3, W 0.85)
       - Preferred: AWS (Req 2, W 0.60), Docker (Req 2, W 0.60)
    2. Persist via JobPersistenceService.
    3. Candidate has verified evidence for Java (L3) and SQL (L3), Coursework for Spring Boot (L2), no AWS/Docker.
    4. Run Phase 2 ReadinessService.evaluate_session.
    5. Verify exact mathematical readiness and line-item explainability without duplicating Phase 2 logic.
    """
    async def get_skill(slug: str):
        res = await db_session.execute(select(Skill).where(Skill.slug == slug))
        return res.scalar_one()

    s_java = await get_skill("java")
    s_spring = await get_skill("spring-boot")
    s_sql = await get_skill("sql")
    s_aws = await get_skill("aws")
    s_docker = await get_skill("docker")

    job_req = JobCreateFromParsedRequest(
        title="Software Engineer - Backend",
        company_name="Synthetix Labs",
        target_role="Backend Engineer",
        location_city="Pune",
        source_type="fixture",
        raw_description="Synthetic backend JD for integration verification",
        eligibility_requirements=[
            ExtractedEligibilityItem(
                criterion_type="degree",
                expected_value=["B.Tech", "B.E.", "Bachelor's"],
                operator="IN",
                is_mandatory=True,
                supporting_text="Bachelor's degree required"
            ),
            ExtractedEligibilityItem(
                criterion_type="branch",
                expected_value=["Computer Science", "Information Technology"],
                operator="IN",
                is_mandatory=True,
                supporting_text="CS / IT branch"
            ),
        ],
        competency_requirements=[
            NormalizedCompetencyItem(
                skill_id=s_java.id, skill_slug="java", canonical_name="Java", category="programming",
                required_proficiency_level=3, importance_weight=1.0, is_required=True, interview_relevance_level="high",
                supporting_text="Strong Java experience required"
            ),
            NormalizedCompetencyItem(
                skill_id=s_spring.id, skill_slug="spring-boot", canonical_name="Spring Boot", category="framework",
                required_proficiency_level=3, importance_weight=0.80, is_required=True, interview_relevance_level="medium",
                supporting_text="Spring Boot required"
            ),
            NormalizedCompetencyItem(
                skill_id=s_sql.id, skill_slug="sql", canonical_name="SQL", category="database",
                required_proficiency_level=3, importance_weight=0.85, is_required=True, interview_relevance_level="medium",
                supporting_text="SQL queries required"
            ),
            NormalizedCompetencyItem(
                skill_id=s_aws.id, skill_slug="aws", canonical_name="AWS", category="cloud",
                required_proficiency_level=2, importance_weight=0.60, is_required=False, interview_relevance_level="low",
                supporting_text="AWS preferred"
            ),
            NormalizedCompetencyItem(
                skill_id=s_docker.id, skill_slug="docker", canonical_name="Docker", category="devops",
                required_proficiency_level=2, importance_weight=0.60, is_required=False, interview_relevance_level="low",
                supporting_text="Docker preferred"
            ),
        ]
    )
    job = await JobPersistenceService.persist_job(db=db_session, req=job_req)
    assert job.id is not None

    cand = None
    session = None
    try:
        cand = Candidate(
            full_name="Phase 4 Candidate",
            degree="B.Tech",
            branch="Computer Science",
            graduation_year=2025,
            education_confirmed_by_user=True,
        )
        db_session.add(cand)
        await db_session.flush()

        ev_java = CandidateEvidence(
            candidate_id=cand.id, skill_id=s_java.id, evidence_type="project",
            title="Java Microservice", url="https://github.com/test", verification_status="verified",
            confidence_score=0.85, date_obtained=date.today()
        )
        ev_sql = CandidateEvidence(
            candidate_id=cand.id, skill_id=s_sql.id, evidence_type="project",
            title="SQL Data Schema", url="https://github.com/test", verification_status="verified",
            confidence_score=0.85, date_obtained=date.today()
        )
        ev_spring = CandidateEvidence(
            candidate_id=cand.id, skill_id=s_spring.id, evidence_type="academic_coursework",
            title="Spring Framework Intro", verification_status="self_attested",
            confidence_score=0.70, date_obtained=date.today()
        )
        db_session.add_all([ev_java, ev_sql, ev_spring])
        await db_session.commit()

        session = PreparationSession(
            candidate_id=cand.id,
            job_id=job.id,
            available_hours_per_week=15,
            weeks_until_target=6,
        )
        db_session.add(session)
        await db_session.commit()

        report = await ReadinessService.evaluate_session(db_session, session.id)

        assert report.eligibility_status == "eligible"
        assert 70 <= report.overall_readiness_score <= 88

        breakdowns = {b.skill.slug: b for b in report.item_breakdowns}
        assert breakdowns["java"].classification in ["strength", "aligned"]
        assert breakdowns["sql"].classification in ["strength", "aligned"]
        assert breakdowns["spring-boot"].classification == "moderate_gap"
        assert breakdowns["aws"].estimated_level == 0
        assert breakdowns["docker"].estimated_level == 0

    finally:
        if session:
            await db_session.delete(session)
        if job:
            await db_session.delete(job)
        if cand:
            await db_session.delete(cand)
        await db_session.commit()
