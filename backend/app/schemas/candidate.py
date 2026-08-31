from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class CandidateCreateRequest(BaseModel):
    full_name: str
    email: Optional[str] = Field(None, description="Optional for prototype. No auth/account management.")
    phone: Optional[str] = None
    location_city: Optional[str] = "Pune"
    location_state: Optional[str] = "Maharashtra"
    degree: Optional[str] = None
    branch: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    student_status: Optional[str] = None

class CandidateUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    student_status: Optional[str] = None

class EducationConfirmRequest(BaseModel):
    degree: str
    branch: str
    institution: str
    graduation_year: int
    student_status: str # final_year, recent_graduate, early_career
    confirmed: bool = True

class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    student_status: Optional[str] = None
    education_confirmed_by_user: bool = False
    created_at: datetime
    updated_at: datetime

class CandidateSkillClaimCreate(BaseModel):
    skill_slug: str
    claim_source: str = "resume" # resume, manual_entry
    raw_text: Optional[str] = None
    confirmed_by_user: bool = False
    self_assessment_level: Optional[int] = Field(
        None, ge=1, le=5,
        description="Subjective candidate rating. NOT capability evidence."
    )

class CandidateSkillClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID
    skill_id: UUID
    skill_slug: str
    canonical_name: str
    claim_source: str
    raw_claim_text: Optional[str] = None
    confirmed_by_user: bool
    self_assessment_level: Optional[int] = None
    created_at: datetime

class ConfirmClaimsRequest(BaseModel):
    confirmed_skill_slugs: List[str]
    rejected_skill_slugs: List[str] = Field(default_factory=list)
