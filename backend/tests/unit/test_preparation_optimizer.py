import pytest
from uuid import uuid4
from datetime import date
from sqlalchemy.future import select

from app.models.candidate import Candidate
from app.models.job import Job
from app.models.session import PreparationSession
from app.domains.planning.prioritizer import CandidateSkillGap, GapPrioritizer
from app.domains.planning.allocator import TimeAllocator
from app.domains.planning.scheduler import WeeklyScheduler
from app.domains.planning.optimizer import PreparationOptimizer
from app.domains.planning.service import PreparationPlanService
from app.domains.readiness.service import ReadinessService

def test_prioritizer_deterministic_rules():
    """Verify gap severity, required vs preferred, importance, and interview relevance ranking."""
    # Gap 3 required with high relevance (System Design)
    g1 = CandidateSkillGap("system-design", "System Design", "arch", 3, 0, 1.0, True, "high", "med", "critical_gap")
    # Gap 2 required with medium relevance (Spring Boot)
    g2 = CandidateSkillGap("spring-boot", "Spring Boot", "framework", 3, 1, 0.85, True, "medium", "med", "moderate_gap")
    # Gap 2 preferred with low relevance (Docker)
    g3 = CandidateSkillGap("docker", "Docker", "devops", 2, 0, 0.60, False, "low", "med", "moderate_gap")
    # Gap 0 required with low confidence (triggers validation priority)
    g4 = CandidateSkillGap("java", "Java", "prog", 3, 3, 1.0, True, "high", "low", "strength")
    # Gap 0 required with high confidence (maintenance)
    g5 = CandidateSkillGap("sql", "SQL", "db", 3, 3, 0.85, True, "medium", "high", "strength")

    prioritized = GapPrioritizer.prioritize_gaps([g5, g3, g4, g2, g1])
    # Order must be g1 > g2 > g3 > g4 > g5
    assert prioritized[0].skill_slug == "system-design"
    assert prioritized[1].skill_slug == "spring-boot"
    assert prioritized[2].skill_slug == "docker"
    assert prioritized[3].skill_slug == "java"
    assert prioritized[4].skill_slug == "sql"

    assert prioritized[0].priority_tier == "high"
    assert prioritized[3].priority_tier == "maintenance"

def test_allocator_capacity_and_diminishing_returns():
    """Verify time allocator respects total capacity and prevents monopoly."""
    g1 = CandidateSkillGap("system-design", "System Design", "arch", 3, 0, 1.0, True, "high", "med", "critical_gap")
    g2 = CandidateSkillGap("docker", "Docker", "devops", 2, 0, 0.85, True, "medium", "med", "moderate_gap")
    g3 = CandidateSkillGap("sql", "SQL", "db", 3, 1, 0.85, True, "medium", "med", "moderate_gap")
    g4 = CandidateSkillGap("java", "Java", "prog", 3, 3, 1.0, True, "high", "high", "strength")

    total_hours = 60 # 10 hrs/wk * 6 wks
    allocations = TimeAllocator.allocate_hours([g1, g2, g3, g4], total_hours)

    total_allocated = sum(allocations.values())
    assert total_allocated == 60.0

    # System Design has highest priority, but cannot consume > 40% (24 hrs)
    assert allocations["system-design"] <= 24.0
    assert allocations["system-design"] >= allocations["docker"]
    assert allocations["docker"] >= allocations["java"]
    # Maintenance cap <= 15% (9 hrs)
    assert allocations["java"] <= 9.0

def test_weekly_scheduler_structure_and_final_week_review():
    """Verify weekly scheduler creates exact weeks, respects weekly capacity, and reserves review in final week."""
    g1 = CandidateSkillGap("system-design", "System Design", "arch", 3, 0, 1.0, True, "high", "med", "critical_gap")
    g2 = CandidateSkillGap("docker", "Docker", "devops", 2, 0, 0.85, True, "medium", "med", "moderate_gap")

    allocations = {"system-design": 30.0, "docker": 18.0}
    schedule = WeeklyScheduler.generate_schedule([g1, g2], allocations, weeks_until_target=6, hours_per_week=8)

    assert len(schedule) == 6
    for idx, week in enumerate(schedule, 1):
        assert week.week_number == idx
        assert week.total_hours <= 8.0

    # Final week should have mock technical interview activity
    final_week = schedule[-1]
    final_types = [a.activity_type for a in final_week.activities]
    assert "ASSESS" in final_types

def test_edge_case_minimal_time():
    """1 week, 2 hours/week must generate a tiny but valid plan."""
    g1 = CandidateSkillGap("system-design", "System Design", "arch", 3, 0, 1.0, True, "high", "med", "critical_gap")
    allocations = TimeAllocator.allocate_hours([g1], total_available_hours=2)
    schedule = WeeklyScheduler.generate_schedule([g1], allocations, weeks_until_target=1, hours_per_week=2)

    assert len(schedule) == 1
    assert schedule[0].total_hours <= 2.0
    assert sum(allocations.values()) == 2.0

def test_edge_case_candidate_with_no_gaps():
    """If candidate meets all requirements, plan generates maintenance & assessment."""
    g1 = CandidateSkillGap("java", "Java", "prog", 3, 4, 1.0, True, "high", "high", "strength")
    g2 = CandidateSkillGap("sql", "SQL", "db", 3, 3, 0.85, True, "medium", "high", "strength")

    allocations = TimeAllocator.allocate_hours([g1, g2], total_available_hours=10)
    schedule = WeeklyScheduler.generate_schedule([g1, g2], allocations, weeks_until_target=2, hours_per_week=5)

    assert len(schedule) == 2
    assert sum(allocations.values()) <= 10.0
    for week in schedule:
        for act in week.activities:
            assert act.activity_type in ["MAINTAIN", "ASSESS"]

@pytest.mark.asyncio
async def test_end_to_end_preparation_plan_service(db_session):
    """Verify complete Readiness -> Plan generation -> Database persistence -> Determinism."""
    res_cand = await db_session.execute(select(Candidate).where(Candidate.full_name == "Aarav Deshmukh"))
    candidate = res_cand.scalar_one()

    res_job = await db_session.execute(select(Job).where(Job.company_name == "Persistent Systems"))
    job = res_job.scalar_one()

    session = None
    try:
        session = PreparationSession(
            candidate_id=candidate.id,
            job_id=job.id,
            available_hours_per_week=12,
            weeks_until_target=4,
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        # 1. Attempting to generate plan BEFORE readiness evaluation must raise ValueError
        with pytest.raises(ValueError, match="Readiness report not found"):
            await PreparationPlanService.generate_plan(db=db_session, session_id=session.id)

        # 2. Evaluate Readiness
        await ReadinessService.evaluate_session(db=db_session, session_id=session.id)

        # 3. Generate Preparation Plan
        plan1 = await PreparationPlanService.generate_plan(db=db_session, session_id=session.id)

        assert plan1.id is not None
        assert plan1.session_id == session.id
        assert plan1.weeks_until_target == 4
        assert plan1.available_hours_per_week == 12
        assert len(plan1.schedule) == 4
        assert len(plan1.milestones) >= 2
        assert len(plan1.priority_areas) > 0

        # 4. Retrieve Plan
        retrieved = await PreparationPlanService.get_plan(db=db_session, session_id=session.id)
        assert retrieved.id == plan1.id
        assert retrieved.total_hours_allocated == plan1.total_hours_allocated

        # 5. Determinism Check: Re-generating plan yields identical total hours and schedules
        plan2 = await PreparationPlanService.generate_plan(db=db_session, session_id=session.id)
        assert plan2.total_hours_allocated == plan1.total_hours_allocated
        assert len(plan2.schedule) == len(plan1.schedule)
        assert [s.total_hours for s in plan2.schedule] == [s.total_hours for s in plan1.schedule]

    finally:
        if session:
            await db_session.delete(session)
            await db_session.commit()
