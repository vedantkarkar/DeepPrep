from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.job import Job, JobEligibilityRequirement, JobCompetencyRequirement
from app.domains.jobs.schemas import JobCreateFromParsedRequest

class JobPersistenceService:
    """Handles persisting validated structured jobs into PostgreSQL."""

    @classmethod
    async def persist_job(
        cls,
        db: AsyncSession,
        req: JobCreateFromParsedRequest,
    ) -> Job:
        loc = f"{req.location_city or ''}, {req.location_state or ''}".strip(", ") or None

        job = Job(
            title=req.title,
            company_name=req.company_name,
            target_role=req.target_role,
            location=loc,
            source_url=req.source_url,
            source_type=req.source_type,
            posted_date=req.posted_date,
            raw_description=req.raw_description,
            is_active=True,
        )
        db.add(job)
        await db.flush()

        # Add eligibility requirements
        for elig in req.eligibility_requirements:
            elig_rec = JobEligibilityRequirement(
                job_id=job.id,
                criterion_type=elig.criterion_type,
                expected_value=elig.expected_value,
                operator=elig.operator,
                is_mandatory=elig.is_mandatory,
            )
            db.add(elig_rec)

        # Add competency requirements
        for comp in req.competency_requirements:
            comp_rec = JobCompetencyRequirement(
                job_id=job.id,
                skill_id=comp.skill_id,
                required_proficiency_level=comp.required_proficiency_level,
                importance_weight=comp.importance_weight,
                is_required=comp.is_required,
                interview_relevance_level=comp.interview_relevance_level,
                importance_provenance=comp.importance_provenance or "extracted_from_jd",
            )
            db.add(comp_rec)

        await db.commit()

        # Reload with relationships
        stmt = (
            select(Job)
            .options(
                selectinload(Job.eligibility_requirements),
                selectinload(Job.competency_requirements).selectinload(JobCompetencyRequirement.skill),
            )
            .where(Job.id == job.id)
        )
        res = await db.execute(stmt)
        return res.scalar_one()
