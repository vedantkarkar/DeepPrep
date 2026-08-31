from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from uuid import UUID

class ExtractedEducationClaim(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    degree: Optional[str] = None
    branch: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    student_status: Optional[str] = None
    source_context: Optional[str] = None

class ExtractedSkillClaim(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    raw_text: str
    source_context: Optional[str] = None
    claimed_level: Optional[int] = None

class ExtractedProjectClaim(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    repository_url: Optional[str] = None
    source_context: Optional[str] = None

class ExtractedExperienceClaim(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role: str
    company: str
    duration: Optional[str] = None
    description: Optional[str] = None
    source_context: Optional[str] = None

class ExtractedCertificationClaim(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    credential_url: Optional[str] = None
    source_context: Optional[str] = None

class RawResumeExtraction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education_claims: List[ExtractedEducationClaim] = Field(default_factory=list)
    skill_claims: List[ExtractedSkillClaim] = Field(default_factory=list)
    project_claims: List[ExtractedProjectClaim] = Field(default_factory=list)
    experience_claims: List[ExtractedExperienceClaim] = Field(default_factory=list)
    certification_claims: List[ExtractedCertificationClaim] = Field(default_factory=list)
    raw_text: str = ""

class NormalizedSkillClaimItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_id: UUID
    skill_slug: str
    canonical_name: str
    category: str
    raw_text: str
    source_context: Optional[str] = None
    confirmed: bool = False
    claim_source: str = "resume"

class UnresolvedSkillClaimItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    raw_text: str
    source_context: Optional[str] = None
    reason: str = "Not found in canonical skill taxonomy"

class ResumeExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: str = "needs_confirmation"
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education_status: str # extracted, missing, ambiguous
    education_claims: List[ExtractedEducationClaim] = Field(default_factory=list)
    normalized_skill_claims: List[NormalizedSkillClaimItem] = Field(default_factory=list)
    unresolved_skill_claims: List[UnresolvedSkillClaimItem] = Field(default_factory=list)
    project_claims: List[ExtractedProjectClaim] = Field(default_factory=list)
    experience_claims: List[ExtractedExperienceClaim] = Field(default_factory=list)
    certification_claims: List[ExtractedCertificationClaim] = Field(default_factory=list)
