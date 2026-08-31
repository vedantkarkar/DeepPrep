import pytest
from uuid import uuid4
from datetime import date
from app.models.candidate import Candidate
from app.models.skill import Skill
from app.models.job import Job, JobEligibilityRequirement, JobCompetencyRequirement
from app.models.evidence import CandidateEvidence
from app.domains.readiness.engine import ReadinessEngine

def make_skill(name: str, slug: str) -> Skill:
    return Skill(id=uuid4(), canonical_name=name, slug=slug, category="programming")

def test_exact_match_on_all_requirements_scores_100():
    cand = Candidate(
        id=uuid4(),
        full_name="Perfect Match",
        degree="B.Tech",
        branch="Computer Science",
        graduation_year=2025,
        education_confirmed_by_user=True,
    )
    skill_java = make_skill("Java", "java")
    skill_sql = make_skill("SQL", "sql")

    job = Job(
        id=uuid4(),
        title="Backend Engineer",
        target_role="Backend Engineer",
        company_name="Acme Corp",
        raw_description="JD text",
        eligibility_requirements=[],
        competency_requirements=[
            JobCompetencyRequirement(
                id=uuid4(),
                skill_id=skill_java.id,
                skill=skill_java,
                is_required=True,
                importance_weight=1.0,
                required_proficiency_level=3,
            ),
            JobCompetencyRequirement(
                id=uuid4(),
                skill_id=skill_sql.id,
                skill=skill_sql,
                is_required=True,
                importance_weight=0.8,
                required_proficiency_level=3,
            ),
        ],
    )

    # Provide practical project evidence for both to reach Level 3
    ev_java = CandidateEvidence(
        id=uuid4(), candidate_id=cand.id, skill_id=skill_java.id,
        evidence_type="project", title="Java Service", url="https://github.com/test",
        verification_status="verified", confidence_score=0.8, date_obtained=date.today(),
    )
    ev_sql = CandidateEvidence(
        id=uuid4(), candidate_id=cand.id, skill_id=skill_sql.id,
        evidence_type="project", title="SQL Schema", url="https://github.com/test",
        verification_status="verified", confidence_score=0.8, date_obtained=date.today(),
    )

    res = ReadinessEngine.evaluate(cand, job, [ev_java, ev_sql])
    assert res.overall_readiness_score == 100
    assert len(res.critical_gaps_summary) == 0

def test_exceeding_requirements_does_not_give_bonus_points():
    cand = Candidate(
        id=uuid4(), full_name="Super Candidate",
        degree="B.Tech", branch="Computer Science", graduation_year=2025, education_confirmed_by_user=True
    )
    skill_dsa = make_skill("Data Structures", "dsa")

    # Job requires Level 2
    job = Job(
        id=uuid4(), title="Junior Dev", target_role="Software Engineer", company_name="Acme", raw_description="JD",
        competency_requirements=[
            JobCompetencyRequirement(
                id=uuid4(), skill_id=skill_dsa.id, skill=skill_dsa,
                is_required=True, importance_weight=1.0, required_proficiency_level=2,
            )
        ]
    )

    # Candidate has Level 4 evidence
    ev_dsa = CandidateEvidence(
        id=uuid4(), candidate_id=cand.id, skill_id=skill_dsa.id,
        evidence_type="assessment", title="LeetCode 200+",
        raw_metadata={"total_solved": 200, "contest_rating": 1700},
        verification_status="verified", confidence_score=0.9, date_obtained=date.today(),
    )

    res = ReadinessEngine.evaluate(cand, job, [ev_dsa])
    # Contribution is capped at required level (2 / 2 * 100 = 100, not 4 / 2 * 100)
    assert res.overall_readiness_score == 100
    assert res.item_breakdowns[0]["classification"] == "strength"
    assert res.item_breakdowns[0]["estimated_level"] >= 3

def test_section_37_exact_conceptual_test_case():
    """Exact test case from Section 37:
    Job:
      Java      Req Level 3, Weight 1.0, High Relevance
      SQL       Req Level 3, Weight 0.8, Medium Relevance
      Docker    Req Level 2, Weight 0.6, Low Relevance
      DSA       Req Level 3, Weight 1.0, High Relevance
    Candidate:
      Java: Level 3 evidence
      SQL: Level 2 evidence
      Docker: No evidence
      DSA: Level 4 evidence
    """
    cand = Candidate(
        id=uuid4(), full_name="Section 37 Candidate",
        degree="B.Tech", branch="CSE", graduation_year=2025, education_confirmed_by_user=True
    )
    s_java = make_skill("Java", "java")
    s_sql = make_skill("SQL", "sql")
    s_docker = make_skill("Docker", "docker")
    s_dsa = make_skill("DSA", "dsa")

    job = Job(
        id=uuid4(), title="Target Job", target_role="Software Engineer", company_name="TestCorp", raw_description="JD",
        competency_requirements=[
            JobCompetencyRequirement(
                id=uuid4(), skill_id=s_java.id, skill=s_java, is_required=True,
                importance_weight=1.0, required_proficiency_level=3, interview_relevance_level="high"
            ),
            JobCompetencyRequirement(
                id=uuid4(), skill_id=s_sql.id, skill=s_sql, is_required=True,
                importance_weight=0.8, required_proficiency_level=3, interview_relevance_level="medium"
            ),
            JobCompetencyRequirement(
                id=uuid4(), skill_id=s_docker.id, skill=s_docker, is_required=False,
                importance_weight=0.6, required_proficiency_level=2, interview_relevance_level="low"
            ),
            JobCompetencyRequirement(
                id=uuid4(), skill_id=s_dsa.id, skill=s_dsa, is_required=True,
                importance_weight=1.0, required_proficiency_level=3, interview_relevance_level="high"
            ),
        ]
    )

    ev_java = CandidateEvidence(
        id=uuid4(), candidate_id=cand.id, skill_id=s_java.id,
        evidence_type="project", title="Java API", verification_status="verified", confidence_score=0.8, date_obtained=date.today()
    )
    ev_sql = CandidateEvidence(
        id=uuid4(), candidate_id=cand.id, skill_id=s_sql.id,
        evidence_type="academic_coursework", title="DBMS Course", verification_status="self_attested", confidence_score=0.7, date_obtained=date.today()
    )
    ev_dsa = CandidateEvidence(
        id=uuid4(), candidate_id=cand.id, skill_id=s_dsa.id,
        evidence_type="assessment", title="LeetCode 200", raw_metadata={"total_solved": 200, "contest_rating": 1650},
        verification_status="verified", confidence_score=0.85, date_obtained=date.today()
    )

    res = ReadinessEngine.evaluate(cand, job, [ev_java, ev_sql, ev_dsa])
    breakdowns = {item["skill_slug"]: item for item in res.item_breakdowns}

    # Java: Aligned / Strength
    assert breakdowns["java"]["classification"] in ["aligned", "strength"]
    assert breakdowns["java"]["estimated_level"] == 3

    # SQL: Moderate gap (Req 3, Est 2)
    assert breakdowns["sql"]["classification"] == "moderate_gap"
    assert breakdowns["sql"]["gap_score"] > 0

    # Docker: Gap (No evidence)
    assert breakdowns["docker"]["estimated_level"] == 0
    assert breakdowns["docker"]["classification"] in ["moderate_gap", "critical_gap"]

    # DSA: Strength (Req 3, Est >= 3)
    assert breakdowns["dsa"]["classification"] == "strength"
    assert breakdowns["dsa"]["estimated_level"] >= 3

    # Score calculation: 
    # Total max = 1.0*3 + 0.8*3 + (0.6*0.7)*2 + 1.0*3 = 3.0 + 2.4 + 0.84 + 3.0 = 9.24
    # Achieved = 1.0*3 + 0.8*2 + 0 + 1.0*3 = 3.0 + 1.6 + 0 + 3.0 = 7.6
    # Readiness = (7.6 / 9.24) * 100 ~= 82
    assert 78 <= res.overall_readiness_score <= 86
    assert 0 <= res.overall_readiness_score <= 100

def test_determinism_identical_runs():
    cand = Candidate(id=uuid4(), full_name="Deterministic Test", degree="B.Tech", branch="CSE", graduation_year=2025, education_confirmed_by_user=True)
    s1 = make_skill("Python", "python")
    job = Job(id=uuid4(), title="Python Dev", target_role="Backend", company_name="Co", raw_description="JD",
              competency_requirements=[JobCompetencyRequirement(id=uuid4(), skill_id=s1.id, skill=s1, is_required=True, importance_weight=1.0, required_proficiency_level=3)])
    ev = CandidateEvidence(id=uuid4(), candidate_id=cand.id, skill_id=s1.id, evidence_type="project", title="Py App", verification_status="verified", confidence_score=0.8, date_obtained=date.today())

    res1 = ReadinessEngine.evaluate(cand, job, [ev])
    res2 = ReadinessEngine.evaluate(cand, job, [ev])

    assert res1.overall_readiness_score == res2.overall_readiness_score
    assert res1.evidence_confidence_score == res2.evidence_confidence_score
    assert res1.item_breakdowns == res2.item_breakdowns
