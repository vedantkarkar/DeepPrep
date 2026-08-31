import pytest
import uuid
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models import (
    Candidate,
    Skill,
    SkillAlias,
    Job,
    JobEligibilityRequirement,
    JobCompetencyRequirement,
    CandidateEvidence,
    CandidateSkill,
    PreparationSession,
    ReadinessReport,
    ReadinessItemBreakdown,
    PreparationPlan,
)

@pytest.mark.asyncio
async def test_candidate_creation_with_optional_email(db_session):
    cand = Candidate(
        full_name="Test Candidate No Email",
        email=None,
        phone="+91 99999 88888",
        location_city="Pune",
        degree="B.Tech",
        branch="IT",
        institution="Pune University",
        graduation_year=2025,
        education_confirmed_by_user=False,
    )
    db_session.add(cand)
    await db_session.commit()

    assert cand.id is not None
    assert cand.email is None
    assert cand.education_confirmed_by_user is False

    # Cleanup
    await db_session.delete(cand)
    await db_session.commit()

@pytest.mark.asyncio
async def test_unique_candidate_skill_constraint(db_session):
    # Fetch skill
    res = await db_session.execute(select(Skill).where(Skill.slug == "python"))
    py_skill = res.scalar_one()

    cand = Candidate(full_name="Duplicate Skill Test User")
    db_session.add(cand)
    await db_session.flush()

    claim1 = CandidateSkill(
        candidate_id=cand.id,
        skill_id=py_skill.id,
        claim_source="resume",
        confirmed_by_user=False,
    )
    db_session.add(claim1)
    await db_session.commit()

    claim2 = CandidateSkill(
        candidate_id=cand.id,
        skill_id=py_skill.id,
        claim_source="manual_entry",
        confirmed_by_user=True,
    )
    db_session.add(claim2)
    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()
    # Delete test candidate
    await db_session.delete(cand)
    await db_session.commit()

@pytest.mark.asyncio
async def test_candidate_cascade_deletion(db_session):
    res = await db_session.execute(select(Skill).where(Skill.slug == "java"))
    java_skill = res.scalar_one()

    cand = Candidate(full_name="Cascade Test Candidate")
    db_session.add(cand)
    await db_session.flush()

    claim = CandidateSkill(candidate_id=cand.id, skill_id=java_skill.id, claim_source="resume")
    ev = CandidateEvidence(candidate_id=cand.id, skill_id=java_skill.id, evidence_type="project", title="Test Java Project")
    db_session.add_all([claim, ev])
    await db_session.commit()

    claim_id = claim.id
    ev_id = ev.id

    # Delete candidate
    await db_session.delete(cand)
    await db_session.commit()

    # Verify claim and evidence are deleted via cascade
    res_claim = await db_session.execute(select(CandidateSkill).where(CandidateSkill.id == claim_id))
    assert res_claim.scalar_one_or_none() is None

    res_ev = await db_session.execute(select(CandidateEvidence).where(CandidateEvidence.id == ev_id))
    assert res_ev.scalar_one_or_none() is None
