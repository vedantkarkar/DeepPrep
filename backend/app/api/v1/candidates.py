from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete

from app.database import get_db
from app.models.candidate import Candidate, CandidateSkill
from app.models.skill import Skill
from app.schemas.candidate import (
    CandidateCreateRequest,
    CandidateResponse,
    EducationConfirmRequest,
    CandidateSkillClaimResponse,
    ConfirmClaimsRequest,
)

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    req: CandidateCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new lightweight candidate identity."""
    candidate = Candidate(
        full_name=req.full_name,
        email=req.email,
        phone=req.phone,
        location_city=req.location_city or "Pune",
        location_state=req.location_state or "Maharashtra",
        degree=req.degree,
        branch=req.branch,
        institution=req.institution,
        graduation_year=req.graduation_year,
        student_status=req.student_status,
        education_confirmed_by_user=False,
    )
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate

@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve candidate profile details."""
    res = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = res.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return candidate

@router.patch("/{candidate_id}/education", response_model=CandidateResponse)
async def confirm_candidate_education(
    candidate_id: UUID,
    req: EducationConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    """Confirm, correct, or supply missing candidate education details."""
    res = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = res.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    if req.graduation_year < 1980 or req.graduation_year > 2035:
        raise HTTPException(status_code=400, detail="Invalid graduation year.")

    candidate.degree = req.degree
    candidate.branch = req.branch
    candidate.institution = req.institution
    candidate.graduation_year = req.graduation_year
    candidate.student_status = req.student_status
    candidate.education_confirmed_by_user = req.confirmed

    await db.commit()
    await db.refresh(candidate)
    return candidate

@router.get("/{candidate_id}/claims", response_model=List[CandidateSkillClaimResponse])
async def get_candidate_claims(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all skill claims registered for a candidate."""
    stmt = (
        select(CandidateSkill)
        .options(selectinload(CandidateSkill.skill))
        .where(CandidateSkill.candidate_id == candidate_id)
    )
    res = await db.execute(stmt)
    claims = res.scalars().all()

    return [
        CandidateSkillClaimResponse(
            id=c.id,
            candidate_id=c.candidate_id,
            skill_id=c.skill_id,
            skill_slug=c.skill.slug,
            canonical_name=c.skill.canonical_name,
            claim_source=c.claim_source,
            raw_claim_text=c.raw_claim_text,
            confirmed_by_user=c.confirmed_by_user,
            self_assessment_level=c.self_assessment_level,
            created_at=c.created_at,
        )
        for c in claims
    ]

@router.post("/{candidate_id}/claims/confirm", response_model=List[CandidateSkillClaimResponse])
async def batch_confirm_claims(
    candidate_id: UUID,
    req: ConfirmClaimsRequest,
    db: AsyncSession = Depends(get_db),
):
    """Batch confirm, reject, or update candidate skill claims."""
    # Verify candidate exists
    res = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = res.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    # Remove rejected skills
    for slug in req.rejected_skill_slugs:
        s_res = await db.execute(select(Skill).where(Skill.slug == slug))
        s_obj = s_res.scalar_one_or_none()
        if s_obj:
            await db.execute(
                delete(CandidateSkill).where(
                    CandidateSkill.candidate_id == candidate_id,
                    CandidateSkill.skill_id == s_obj.id,
                )
            )

    # Upsert confirmed skills
    for slug in req.confirmed_skill_slugs:
        s_res = await db.execute(select(Skill).where(Skill.slug == slug))
        skill = s_res.scalar_one_or_none()
        if not skill:
            continue

        c_stmt = select(CandidateSkill).where(
            CandidateSkill.candidate_id == candidate_id,
            CandidateSkill.skill_id == skill.id,
        )
        c_res = await db.execute(c_stmt)
        claim = c_res.scalar_one_or_none()
        if not claim:
            claim = CandidateSkill(
                candidate_id=candidate_id,
                skill_id=skill.id,
                claim_source="resume",
                confirmed_by_user=True,
            )
            db.add(claim)
        else:
            claim.confirmed_by_user = True

    await db.commit()

    # Return updated list of claims
    return await get_candidate_claims(candidate_id=candidate_id, db=db)
