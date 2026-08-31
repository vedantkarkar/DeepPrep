"""
Service layer for generating and retrieving Preparation Plans.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.session import PreparationSession
from app.models.readiness import ReadinessReport, ReadinessItemBreakdown
from app.models.plan import PreparationPlan
from app.models.job import Job
from app.domains.planning.optimizer import PreparationOptimizer
from app.domains.planning.models import PreparationPlanResponse, PriorityArea, WeeklySchedule, PreparationMilestone

class PreparationPlanService:
    @staticmethod
    async def generate_plan(
        db: AsyncSession,
        session_id: UUID,
    ) -> PreparationPlanResponse:
        """
        Generate and persist a deterministic preparation plan for an evaluated session.
        """
        # 1. Fetch PreparationSession with Job
        res_sess = await db.execute(
            select(PreparationSession)
            .options(
                selectinload(PreparationSession.job).selectinload(Job.competency_requirements),
            )
            .where(PreparationSession.id == session_id)
        )
        session = res_sess.scalar_one_or_none()
        if not session:
            raise ValueError("Preparation session not found.")

        # 2. Fetch Latest ReadinessReport for session
        res_rep = await db.execute(
            select(ReadinessReport)
            .options(
                selectinload(ReadinessReport.item_breakdowns).selectinload(ReadinessItemBreakdown.skill),
            )
            .where(ReadinessReport.session_id == session_id)
            .order_by(ReadinessReport.generated_at.desc())
        )
        report = res_rep.scalars().first()
        if not report:
            raise ValueError("Readiness report not found. You must evaluate readiness before generating a plan.")

        # 3. Optimize & Generate Plan Payload
        plan_dict = PreparationOptimizer.optimize(session=session, report=report)

        # 4. Persist PreparationPlan into PostgreSQL
        plan_model = PreparationPlan(
            report_id=report.id,
            session_id=session.id,
            total_hours_allocated=plan_dict["total_hours_allocated"],
            schedule=plan_dict["schedule"],
            milestones=plan_dict["milestones"],
        )
        db.add(plan_model)
        await db.commit()
        await db.refresh(plan_model)

        return PreparationPlanResponse(
            id=plan_model.id,
            session_id=plan_model.session_id,
            report_id=plan_model.report_id,
            total_hours_allocated=plan_model.total_hours_allocated,
            available_hours_per_week=session.available_hours_per_week,
            weeks_until_target=session.weeks_until_target,
            capacity_note=plan_dict["capacity_note"],
            priority_areas=[PriorityArea(**p) for p in plan_dict["priority_areas"]],
            schedule=[WeeklySchedule(**s) for s in plan_dict["schedule"]],
            milestones=[PreparationMilestone(**m) for m in plan_dict["milestones"]],
            created_at=plan_model.created_at,
        )

    @staticmethod
    async def get_plan(
        db: AsyncSession,
        session_id: UUID,
    ) -> PreparationPlanResponse:
        """
        Retrieve existing preparation plan for a session.
        """
        res_sess = await db.execute(
            select(PreparationSession)
            .options(
                selectinload(PreparationSession.job).selectinload(Job.competency_requirements),
            )
            .where(PreparationSession.id == session_id)
        )
        session = res_sess.scalar_one_or_none()
        if not session:
            raise ValueError("Preparation session not found.")

        res_plan = await db.execute(
            select(PreparationPlan)
            .where(PreparationPlan.session_id == session_id)
            .order_by(PreparationPlan.created_at.desc())
        )
        plan_model = res_plan.scalars().first()
        if not plan_model:
            raise ValueError("Preparation plan not found for this session.")

        res_rep = await db.execute(
            select(ReadinessReport)
            .options(
                selectinload(ReadinessReport.item_breakdowns).selectinload(ReadinessItemBreakdown.skill),
            )
            .where(ReadinessReport.id == plan_model.report_id)
        )
        report = res_rep.scalars().first()
        plan_dict = PreparationOptimizer.optimize(session=session, report=report) if report else {}

        priority_areas = [PriorityArea(**p) for p in plan_dict.get("priority_areas", [])]
        capacity_note = plan_dict.get("capacity_note", "Optimized preparation schedule.")

        return PreparationPlanResponse(
            id=plan_model.id,
            session_id=plan_model.session_id,
            report_id=plan_model.report_id,
            total_hours_allocated=plan_model.total_hours_allocated,
            available_hours_per_week=session.available_hours_per_week,
            weeks_until_target=session.weeks_until_target,
            capacity_note=capacity_note,
            priority_areas=priority_areas,
            schedule=[WeeklySchedule(**s) for s in (plan_model.schedule or [])],
            milestones=[PreparationMilestone(**m) for m in (plan_model.milestones or [])],
            created_at=plan_model.created_at,
        )
