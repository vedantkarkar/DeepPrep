from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete

from app.models.candidate import Candidate, CandidateSkill
from app.models.evidence import CandidateEvidence
from app.models.job import Job, JobEligibilityRequirement, JobCompetencyRequirement
from app.models.session import PreparationSession
from app.models.readiness import ReadinessReport, ReadinessItemBreakdown
from app.domains.readiness.engine import ReadinessEngine, ReadinessEvaluationResult

class ReadinessService:
    @classmethod
    async def evaluate_session(
        cls,
        db: AsyncSession,
        session_id: UUID,
    ) -> ReadinessReport:
        # 1. Fetch preparation session
        stmt_session = select(PreparationSession).where(PreparationSession.id == session_id)
        res_session = await db.execute(stmt_session)
        prep_session = res_session.scalar_one_or_none()
        if not prep_session:
            raise ValueError(f"Preparation session {session_id} not found.")

        # 2. Fetch candidate with claims and evidence
        stmt_candidate = (
            select(Candidate)
            .options(
                selectinload(Candidate.skills),
                selectinload(Candidate.evidence),
            )
            .where(Candidate.id == prep_session.candidate_id)
        )
        res_candidate = await db.execute(stmt_candidate)
        candidate = res_candidate.scalar_one_or_none()
        if not candidate:
            raise ValueError(f"Candidate {prep_session.candidate_id} not found.")

        # 3. Fetch job with eligibility and competency requirements
        stmt_job = (
            select(Job)
            .options(
                selectinload(Job.eligibility_requirements),
                selectinload(Job.competency_requirements).selectinload(JobCompetencyRequirement.skill),
            )
            .where(Job.id == prep_session.job_id)
        )
        res_job = await db.execute(stmt_job)
        job = res_job.scalar_one_or_none()
        if not job:
            raise ValueError(f"Job {prep_session.job_id} not found.")

        # 4. Pure Deterministic Evaluation
        eval_result: ReadinessEvaluationResult = ReadinessEngine.evaluate(
            candidate=candidate,
            job=job,
            candidate_evidence=candidate.evidence,
            candidate_skills=candidate.skills,
        )

        # 5. Clear previous reports for this session if re-evaluated
        await db.execute(delete(ReadinessReport).where(ReadinessReport.session_id == session_id))

        # 6. Persist ReadinessReport
        report = ReadinessReport(
            session_id=session_id,
            candidate_id=candidate.id,
            job_id=job.id,
            overall_readiness_score=eval_result.overall_readiness_score,
            technical_readiness_score=eval_result.technical_readiness_score,
            evidence_confidence_score=eval_result.evidence_confidence_score,
            eligibility_status=eval_result.eligibility_status,
            eligibility_summary=eval_result.eligibility_details,
            strengths_summary=eval_result.strengths_summary,
            critical_gaps_summary=eval_result.critical_gaps_summary,
        )
        db.add(report)
        await db.flush()

        # 7. Persist ReadinessItemBreakdown records for full line-level traceability
        for item in eval_result.item_breakdowns:
            breakdown = ReadinessItemBreakdown(
                report_id=report.id,
                skill_id=item["skill_id"],
                competency_requirement_id=item.get("competency_requirement_id"),
                required_level=item["required_level"],
                estimated_level=item["estimated_level"],
                importance_weight=item["importance_weight"],
                gap_score=item["gap_score"],
                classification=item["classification"],
                supporting_evidence_ids=[str(eid) for eid in item["supporting_evidence_ids"]],
                explanation=item["explanation"],
            )
            db.add(breakdown)

        await db.commit()
        
        # Reload with item breakdowns and skills
        stmt_reload = (
            select(ReadinessReport)
            .options(
                selectinload(ReadinessReport.item_breakdowns).selectinload(ReadinessItemBreakdown.skill),
            )
            .where(ReadinessReport.id == report.id)
        )
        res_reload = await db.execute(stmt_reload)
        return res_reload.scalar_one()
