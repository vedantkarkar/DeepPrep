import pytest
from sqlalchemy.future import select
from app.models.skill import Skill
from app.models.job import Job
from app.models.candidate import Candidate
from app.seed import seed_database

@pytest.mark.asyncio
async def test_seed_idempotency_and_counts(db_session):
    # Re-run seed with current test session to test idempotency
    await seed_database(session=db_session)

    # Verify skill count
    res_skills = await db_session.execute(select(Skill))
    skills = res_skills.scalars().all()
    assert len(skills) == 40

    # Verify jobs count
    res_jobs = await db_session.execute(select(Job).where(Job.source_type.in_(["fixture", "direct_company"])))
    jobs = res_jobs.scalars().all()
    assert len(jobs) == 5

    # Verify demo candidate exists
    res_cand = await db_session.execute(select(Candidate).where(Candidate.full_name == "Aarav Deshmukh"))
    candidate = res_cand.scalar_one_or_none()
    assert candidate is not None
    assert candidate.location_city == "Pune"
