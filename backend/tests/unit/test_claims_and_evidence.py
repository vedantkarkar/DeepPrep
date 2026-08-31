import pytest
from datetime import date
from uuid import uuid4
from app.models.evidence import CandidateEvidence
from app.domains.evidence.proficiency import ProficiencyEstimator
from app.domains.evidence.evaluator import calculate_recency_factor, evaluate_evidence_item
from app.domains.evidence import rules

def test_resume_skill_alone_produces_level_0():
    # Invariant: No evidence items passed
    est = ProficiencyEstimator.estimate(skill_slug="python", evidence_items=[])
    assert est.estimated_level == 0
    assert est.confidence_label == "low"
    assert len(est.supporting_evidence_ids) == 0
    assert "No supporting evidence" in est.explanation

def test_self_report_alone_capped_at_level_1():
    # Invariant: Self report is weak and capped at Level 1
    ev = CandidateEvidence(
        id=uuid4(),
        candidate_id=uuid4(),
        skill_id=uuid4(),
        evidence_type="self_report",
        title="I know Python basics",
        description="Read docs online",
        verification_status="unverified",
        confidence_score=0.3,
        date_obtained=date.today(),
    )
    est = ProficiencyEstimator.estimate(skill_slug="python", evidence_items=[ev])
    assert est.estimated_level <= 1
    assert est.estimated_level == 1
    assert len(est.supporting_evidence_ids) == 1

def test_academic_coursework_capped_at_level_2():
    ev = CandidateEvidence(
        id=uuid4(),
        candidate_id=uuid4(),
        skill_id=uuid4(),
        evidence_type="academic_coursework",
        title="CS101 Intro to Programming",
        description="Classroom course",
        verification_status="self_attested",
        confidence_score=0.7,
        date_obtained=date.today(),
    )
    est = ProficiencyEstimator.estimate(skill_slug="python", evidence_items=[ev])
    assert est.estimated_level <= 2
    assert est.estimated_level == 2

def test_strong_practical_evidence_produces_level_3_or_4():
    ev_project = CandidateEvidence(
        id=uuid4(),
        candidate_id=uuid4(),
        skill_id=uuid4(),
        evidence_type="project",
        title="Async REST API",
        description="Production grade FastAPI service",
        url="https://github.com/test/repo",
        raw_metadata={"commits": 35, "stars": 6},
        verification_status="verified",
        confidence_score=0.85,
        date_obtained=date.today(),
    )
    est = ProficiencyEstimator.estimate(skill_slug="fastapi", evidence_items=[ev_project])
    assert est.estimated_level >= 3
    assert est.confidence_label in ["medium", "high"]

def test_diminishing_returns_and_cap_on_multiple_weak_items():
    # 5 self reports should NEVER exceed Level 1
    items = []
    for i in range(5):
        items.append(CandidateEvidence(
            id=uuid4(),
            candidate_id=uuid4(),
            skill_id=uuid4(),
            evidence_type="self_report",
            title=f"Claim {i}",
            verification_status="unverified",
            confidence_score=0.2,
            date_obtained=date.today(),
        ))
    est = ProficiencyEstimator.estimate(skill_slug="python", evidence_items=items)
    # Hard ceiling cap for self_report is Level 1
    assert est.estimated_level <= 1

def test_missing_date_uses_neutral_default_factor():
    factor_missing = calculate_recency_factor(None)
    assert factor_missing == rules.RECENCY_FACTOR_DEFAULT
    assert factor_missing == 0.85

def test_unverified_vs_verified_multiplier():
    ev_unverified = CandidateEvidence(
        id=uuid4(),
        candidate_id=uuid4(),
        skill_id=uuid4(),
        evidence_type="project",
        title="Project Unverified",
        verification_status="unverified",
        confidence_score=0.6,
        date_obtained=date.today(),
    )
    ev_verified = CandidateEvidence(
        id=uuid4(),
        candidate_id=uuid4(),
        skill_id=uuid4(),
        evidence_type="project",
        title="Project Verified",
        verification_status="verified",
        confidence_score=0.6,
        date_obtained=date.today(),
    )
    strength_unv, _ = evaluate_evidence_item(ev_unverified)
    strength_ver, _ = evaluate_evidence_item(ev_verified)
    assert strength_ver > strength_unv
