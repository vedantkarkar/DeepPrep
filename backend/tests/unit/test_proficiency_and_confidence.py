import pytest
from datetime import date
from uuid import uuid4
from app.models.evidence import CandidateEvidence
from app.domains.evidence.proficiency import ProficiencyEstimator

def test_estimated_proficiency_strictly_bounded_0_to_5():
    # Test with massive collection of strong evidence
    items = []
    for i in range(10):
        items.append(CandidateEvidence(
            id=uuid4(),
            candidate_id=uuid4(),
            skill_id=uuid4(),
            evidence_type="professional_experience",
            title=f"Role {i}",
            verification_status="verified",
            confidence_score=0.95,
            date_obtained=date.today(),
        ))
    est = ProficiencyEstimator.estimate(skill_slug="java", evidence_items=items)
    assert 0 <= est.estimated_level <= 5
    assert est.estimated_level == 5
    assert 0.0 <= est.confidence_score <= 1.0

def test_confidence_separated_from_proficiency():
    # Single high-strength item unverified -> High proficiency (Level 3), but Low/Medium confidence
    ev1 = CandidateEvidence(
        id=uuid4(),
        candidate_id=uuid4(),
        skill_id=uuid4(),
        evidence_type="project",
        title="Solo project",
        verification_status="unverified",
        confidence_score=0.4,
        date_obtained=date.today(),
    )
    est1 = ProficiencyEstimator.estimate(skill_slug="python", evidence_items=[ev1])

    # Multiple verified coursework and certifications -> Level 2, but High confidence
    ev2_a = CandidateEvidence(
        id=uuid4(),
        candidate_id=uuid4(),
        skill_id=uuid4(),
        evidence_type="academic_coursework",
        title="Course A",
        verification_status="verified",
        confidence_score=0.9,
        date_obtained=date.today(),
    )
    ev2_b = CandidateEvidence(
        id=uuid4(),
        candidate_id=uuid4(),
        skill_id=uuid4(),
        evidence_type="course",
        title="Course B",
        verification_status="verified",
        confidence_score=0.9,
        date_obtained=date.today(),
    )
    est2 = ProficiencyEstimator.estimate(skill_slug="python", evidence_items=[ev2_a, ev2_b])

    assert est2.estimated_level <= 2
    assert est2.confidence_label in ["medium", "high"]
    assert est1.confidence_label in ["low", "medium"]
