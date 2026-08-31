import pytest
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.job import Job, JobEligibilityRequirement, JobCompetencyRequirement
from app.models.candidate import Candidate
from app.models.session import PreparationSession

@pytest.mark.asyncio
async def test_job_eligibility_vs_competency_separation(db_session):
    stmt = select(Job).options(
        selectinload(Job.eligibility_requirements),
        selectinload(Job.competency_requirements).selectinload(JobCompetencyRequirement.skill),
    ).where(Job.company_name == "Razorpay")
    res = await db_session.execute(stmt)
    job = res.scalar_one()

    # Verify eligibility requirements exist and are purely gating (degree, branch, exp)
    assert len(job.eligibility_requirements) >= 2
    for elig in job.eligibility_requirements:
        assert elig.criterion_type in ["degree", "branch", "min_experience_years", "max_experience_years", "min_graduation_year"]
        assert elig.operator in ["EQUALS", "IN", "GREATER_EQUAL", "LESS_EQUAL"]

    # Verify competency requirements exist and have required proficiency levels
    assert len(job.competency_requirements) >= 5
    for comp in job.competency_requirements:
        assert 1 <= comp.required_proficiency_level <= 5
        assert 0.1 <= comp.importance_weight <= 1.0
        assert comp.skill is not None

@pytest.mark.asyncio
async def test_preparation_session_decoupling(db_session):
    # Candidate profile is stable; PreparationSession is transient per target job
    res_cand = await db_session.execute(select(Candidate).where(Candidate.full_name == "Aarav Deshmukh"))
    candidate = res_cand.scalar_one()

    res_job = await db_session.execute(select(Job).where(Job.company_name == "Persistent Systems"))
    job = res_job.scalar_one()

    session = PreparationSession(
        candidate_id=candidate.id,
        job_id=job.id,
        available_hours_per_week=12,
        weeks_until_target=4,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    assert session.id is not None
    assert session.available_hours_per_week == 12
    assert session.weeks_until_target == 4

    # Cleanup session
    await db_session.delete(session)
    await db_session.commit()
