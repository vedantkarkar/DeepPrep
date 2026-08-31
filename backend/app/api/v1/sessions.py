from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.session import PreparationSession
from app.models.readiness import ReadinessReport, ReadinessItemBreakdown
from app.schemas.session import (
    PreparationSessionCreate,
    PreparationSessionResponse,
)
from app.schemas.readiness import (
    ReadinessReportResponse,
    ReadinessItemBreakdownResponse,
)
from app.domains.readiness.service import ReadinessService
from app.domains.planning.models import PreparationPlanResponse
from app.domains.planning.service import PreparationPlanService

router = APIRouter(prefix="/sessions", tags=["Preparation Sessions"])

def format_readiness_report(report: ReadinessReport) -> ReadinessReportResponse:
    breakdowns = [
        ReadinessItemBreakdownResponse(
            skill_slug=b.skill.slug if b.skill else "unknown",
            canonical_name=b.skill.canonical_name if b.skill else "Unknown Skill",
            category=b.skill.category if b.skill else "other",
            required_level=b.required_level,
            estimated_level=b.estimated_level,
            importance_weight=b.importance_weight,
            gap_score=b.gap_score,
            classification=b.classification,
            supporting_evidence_ids=[UUID(eid) for eid in (b.supporting_evidence_ids or []) if eid],
            explanation=b.explanation,
        )
        for b in (report.item_breakdowns or [])
    ]
    return ReadinessReportResponse(
        report_id=report.id,
        session_id=report.session_id,
        candidate_id=report.candidate_id,
        job_id=report.job_id,
        overall_readiness_score=report.overall_readiness_score,
        technical_readiness_score=report.technical_readiness_score,
        evidence_confidence_score=report.evidence_confidence_score,
        eligibility_status=report.eligibility_status,
        eligibility_summary=report.eligibility_summary or {},
        strengths_summary=report.strengths_summary or [],
        critical_gaps_summary=report.critical_gaps_summary or [],
        item_breakdowns=breakdowns,
        generated_at=report.generated_at,
    )

@router.post("", response_model=PreparationSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    req: PreparationSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new preparation session for a candidate targeting a job."""
    res_c = await db.execute(select(Candidate).where(Candidate.id == req.candidate_id))
    if not res_c.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Candidate not found.")

    res_j = await db.execute(select(Job).where(Job.id == req.job_id))
    if not res_j.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found.")

    session = PreparationSession(
        candidate_id=req.candidate_id,
        job_id=req.job_id,
        available_hours_per_week=req.available_hours_per_week,
        weeks_until_target=req.weeks_until_target,
        target_date=req.target_date,
        status="active",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

@router.get("/{session_id}", response_model=PreparationSessionResponse)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve preparation session details."""
    res = await db.execute(select(PreparationSession).where(PreparationSession.id == session_id))
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session

@router.post("/{session_id}/evaluate", response_model=ReadinessReportResponse)
async def evaluate_session_readiness(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Run the deterministic Phase 2 Readiness Engine on the session and return report."""
    try:
        report = await ReadinessService.evaluate_session(db=db, session_id=session_id)
        return format_readiness_report(report)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@router.get("/{session_id}/report", response_model=ReadinessReportResponse)
async def get_session_report(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve existing readiness report for the session."""
    stmt = (
        select(ReadinessReport)
        .options(
            selectinload(ReadinessReport.item_breakdowns).selectinload(ReadinessItemBreakdown.skill)
        )
        .where(ReadinessReport.session_id == session_id)
        .order_by(ReadinessReport.generated_at.desc())
    )
    res = await db.execute(stmt)
    report = res.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Readiness report not found for this session. Please evaluate first.")
    return format_readiness_report(report)

@router.post("/{session_id}/plan", response_model=PreparationPlanResponse, status_code=status.HTTP_201_CREATED)
async def generate_preparation_plan(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Generate a deterministic preparation plan based on evaluated readiness and available hours."""
    try:
        plan = await PreparationPlanService.generate_plan(db=db, session_id=session_id)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")

@router.get("/{session_id}/plan", response_model=PreparationPlanResponse)
async def get_preparation_plan(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve existing preparation plan for the session."""
    try:
        plan = await PreparationPlanService.get_plan(db=db, session_id=session_id)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve plan: {str(e)}")
