from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.candidate import Candidate
from app.models.skill import Skill
from app.models.evidence import CandidateEvidence
from app.schemas.evidence import (
    CandidateEvidenceCreate,
    CandidateEvidenceResponse,
)

router = APIRouter(prefix="/candidates/{candidate_id}/evidence", tags=["Evidence"])

@router.post("", response_model=CandidateEvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate_evidence(
    candidate_id: UUID,
    req: CandidateEvidenceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register verified or candidate-provided evidence for a skill."""
    # Verify candidate exists
    res_cand = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = res_cand.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    # Resolve skill
    res_skill = await db.execute(select(Skill).where(Skill.slug == req.skill_slug))
    skill = res_skill.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=400, detail=f"Skill '{req.skill_slug}' not recognized.")

    evidence = CandidateEvidence(
        candidate_id=candidate_id,
        skill_id=skill.id,
        evidence_type=req.evidence_type.value,
        title=req.title,
        description=req.description,
        url=req.url,
        raw_metadata=req.metadata,
        verification_status="verified" if req.url else "self_attested",
        confidence_score=0.80 if req.url else 0.60,
        date_obtained=req.date_obtained,
    )
    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)

    return CandidateEvidenceResponse(
        id=evidence.id,
        candidate_id=evidence.candidate_id,
        skill_id=evidence.skill_id,
        skill_slug=skill.slug,
        canonical_name=skill.canonical_name,
        evidence_type=evidence.evidence_type,
        title=evidence.title,
        description=evidence.description,
        url=evidence.url,
        raw_metadata=evidence.raw_metadata,
        verification_status=evidence.verification_status,
        confidence_score=evidence.confidence_score,
        date_obtained=evidence.date_obtained,
        created_at=evidence.created_at,
    )

@router.get("", response_model=List[CandidateEvidenceResponse])
async def list_candidate_evidence(
    candidate_id: UUID,
    skill_slug: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all registered evidence for a candidate, optionally filtered by skill."""
    stmt = (
        select(CandidateEvidence)
        .options(selectinload(CandidateEvidence.skill))
        .where(CandidateEvidence.candidate_id == candidate_id)
    )
    if skill_slug:
        stmt = stmt.join(Skill).where(Skill.slug == skill_slug)

    res = await db.execute(stmt)
    items = res.scalars().all()

    return [
        CandidateEvidenceResponse(
            id=ev.id,
            candidate_id=ev.candidate_id,
            skill_id=ev.skill_id,
            skill_slug=ev.skill.slug,
            canonical_name=ev.skill.canonical_name,
            evidence_type=ev.evidence_type,
            title=ev.title,
            description=ev.description,
            url=ev.url,
            raw_metadata=ev.raw_metadata,
            verification_status=ev.verification_status,
            confidence_score=ev.confidence_score,
            date_obtained=ev.date_obtained,
            created_at=ev.created_at,
        )
        for ev in items
    ]
