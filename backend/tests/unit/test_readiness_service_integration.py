import pytest
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.session import PreparationSession
from app.domains.readiness.service import ReadinessService

@pytest.mark.asyncio
async def test_readiness_service_with_seeded_data(db_session):
    # 1. Fetch demo candidate
    res_cand = await db_session.execute(
        select(Candidate).where(Candidate.full_name == "Aarav Deshmukh")
    )
    candidate = res_cand.scalar_one()

    # 2. Fetch Persistent Systems SDE-1 job
    res_job = await db_session.execute(
        select(Job).where(Job.company_name == "Persistent Systems")
    )
    job = res_job.scalar_one()

    # 3. Create preparation session
    session = PreparationSession(
        candidate_id=candidate.id,
        job_id=job.id,
        available_hours_per_week=15,
        weeks_until_target=6,
    )
    db_session.add(session)
    await db_session.commit()

    # 4. Evaluate session via ReadinessService
    report = await ReadinessService.evaluate_session(db_session, session.id)

    assert report.id is not None
    assert report.session_id == session.id
    assert report.candidate_id == candidate.id
    assert report.job_id == job.id
    assert 0 <= report.overall_readiness_score <= 100
    assert report.eligibility_status in ["eligible", "partially_eligible", "ineligible"]
    assert len(report.item_breakdowns) >= 5

    # Check that breakdowns have complete traceability fields
    for b in report.item_breakdowns:
        assert b.required_level >= 1
        assert 0 <= b.estimated_level <= 5
        assert b.importance_weight > 0
        assert b.classification in ["strength", "aligned", "moderate_gap", "critical_gap"]
        assert len(b.explanation) > 0

    # Cleanup
    await db_session.delete(session)
    await db_session.commit()
