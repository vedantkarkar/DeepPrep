import pytest
from app.models.candidate import Candidate
from app.models.job import JobEligibilityRequirement
from app.domains.eligibility.evaluator import EligibilityEvaluator
from app.domains.eligibility.rules import EligibilityStatus

def test_matching_degree_and_graduation_year_passes():
    cand = Candidate(
        full_name="Eligible Candidate",
        degree="B.Tech",
        branch="Computer Science and Engineering",
        graduation_year=2025,
        education_confirmed_by_user=True,
    )
    reqs = [
        JobEligibilityRequirement(
            criterion_type="degree",
            operator="IN",
            expected_value=["B.Tech", "B.E.", "MCA"],
            is_mandatory=True,
        ),
        JobEligibilityRequirement(
            criterion_type="branch",
            operator="IN",
            expected_value=["Computer Science", "Information Technology"],
            is_mandatory=True,
        ),
        JobEligibilityRequirement(
            criterion_type="min_graduation_year",
            operator="GREATER_EQUAL",
            expected_value=2024,
            is_mandatory=True,
        ),
    ]
    res = EligibilityEvaluator.evaluate(cand, reqs)
    assert res.status == EligibilityStatus.ELIGIBLE
    assert res.is_eligible is True
    assert len(res.criteria_evaluations) == 3
    assert all(ce.passed for ce in res.criteria_evaluations)

def test_degree_mismatch_fails_with_ineligible():
    cand = Candidate(
        full_name="Mismatch Candidate",
        degree="B.Com",
        branch="Commerce",
        graduation_year=2025,
        education_confirmed_by_user=True,
    )
    reqs = [
        JobEligibilityRequirement(
            criterion_type="degree",
            operator="IN",
            expected_value=["B.Tech", "B.E."],
            is_mandatory=True,
        ),
    ]
    res = EligibilityEvaluator.evaluate(cand, reqs)
    assert res.status == EligibilityStatus.INELIGIBLE
    assert res.is_eligible is False
    assert not res.criteria_evaluations[0].passed
    assert "does not match" in res.criteria_evaluations[0].explanation

def test_unconfirmed_education_returns_partially_eligible():
    cand = Candidate(
        full_name="Unconfirmed Candidate",
        degree="B.Tech",
        branch="Computer Science",
        graduation_year=2025,
        education_confirmed_by_user=False, # Candidate hasn't confirmed
    )
    reqs = [
        JobEligibilityRequirement(
            criterion_type="degree",
            operator="EQUALS",
            expected_value="B.Tech",
            is_mandatory=True,
        ),
    ]
    res = EligibilityEvaluator.evaluate(cand, reqs)
    assert res.status == EligibilityStatus.PARTIALLY_ELIGIBLE
    assert res.is_eligible is True
    assert "unconfirmed by candidate" in res.summary_reasons[0]
