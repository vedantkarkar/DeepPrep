from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.job import Job, JobEligibilityRequirement, JobCompetencyRequirement
from app.schemas.job import JobResponse, JobDetailResponse, JobEligibilityItem, JobCompetencyItem
from app.domains.jobs.schemas import (
    ParsedJobDescriptionResponse,
    JobCreateFromParsedRequest,
)
from app.domains.jobs.parser_service import JobParserService
from app.domains.jobs.persistence_service import JobPersistenceService
from app.domains.jobs.validator import JobValidationError

router = APIRouter(prefix="/jobs", tags=["Jobs"])

class JobParseRequest(BaseModel):
    raw_description: str
    title: Optional[str] = None
    company_name: Optional[str] = None
    source_url: Optional[str] = None
    source_type: str = "manual_entry"

@router.post("/parse", response_model=ParsedJobDescriptionResponse)
async def parse_job_description(
    req: JobParseRequest,
    db: AsyncSession = Depends(get_db),
):
    """Extract structured eligibility and competency requirements from raw JD text."""
    try:
        return await JobParserService.parse_job_description(
            db=db,
            raw_description=req.raw_description,
            title=req.title,
            company_name=req.company_name,
            source_url=req.source_url,
            source_type=req.source_type,
        )
    except JobValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Parsing error: {str(e)}")

def format_job_response(job: Job) -> JobResponse:
    elig_items = [
        JobEligibilityItem(
            id=e.id,
            criterion_type=e.criterion_type,
            operator=e.operator or "EQUALS",
            expected_value=e.expected_value,
            is_mandatory=e.is_mandatory,
            provenance=getattr(e, "provenance", None) or "extracted_from_jd",
        )
        for e in (job.eligibility_requirements or [])
    ]
    comp_items = [
        JobCompetencyItem(
            id=c.id,
            skill_id=c.skill_id,
            skill_slug=c.skill.slug if c.skill else "unknown",
            canonical_name=c.skill.canonical_name if c.skill else "Unknown",
            category=c.skill.category if c.skill else "other",
            is_required=c.is_required,
            importance_weight=c.importance_weight,
            importance_provenance=getattr(c, "importance_provenance", None) or "curated",
            required_proficiency_level=c.required_proficiency_level,
            interview_relevance_level=c.interview_relevance_level or "medium",
        )
        for c in (job.competency_requirements or [])
    ]
    loc_city = getattr(job, "location_city", None) or getattr(job, "location", None) or "Pune"
    loc_state = getattr(job, "location_state", None) or "Maharashtra"
    return JobResponse(
        id=job.id,
        title=job.title,
        target_role=job.target_role,
        company_name=job.company_name,
        location_city=loc_city,
        location_state=loc_state,
        raw_description=job.raw_description,
        source_url=job.source_url,
        source_type=job.source_type,
        posted_date=job.posted_date,
        is_active=job.is_active,
        eligibility_requirements=elig_items,
        competency_requirements=comp_items,
    )

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    req: JobCreateFromParsedRequest,
    db: AsyncSession = Depends(get_db),
):
    """Persist a validated structured job with eligibility and competency requirements."""
    try:
        job = await JobPersistenceService.persist_job(db=db, req=req)
        return format_job_response(job)
    except JobValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Persistence error: {str(e)}")

@router.get("", response_model=List[JobResponse])
async def list_jobs(
    db: AsyncSession = Depends(get_db),
):
    """List all available jobs in the system."""
    stmt = (
        select(Job)
        .options(
            selectinload(Job.eligibility_requirements),
            selectinload(Job.competency_requirements).selectinload(JobCompetencyRequirement.skill),
        )
        .order_by(Job.created_at.desc())
    )
    res = await db.execute(stmt)
    jobs = res.scalars().all()
    return [format_job_response(j) for j in jobs]

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve structured job details with requirements."""
    stmt = (
        select(Job)
        .options(
            selectinload(Job.eligibility_requirements),
            selectinload(Job.competency_requirements).selectinload(JobCompetencyRequirement.skill),
        )
        .where(Job.id == job_id)
    )
    res = await db.execute(stmt)
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return format_job_response(job)
