from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from enum import Enum
from uuid import UUID
from datetime import date, datetime

class EvidenceType(str, Enum):
    SELF_REPORT = "self_report"
    ACADEMIC_COURSEWORK = "academic_coursework"
    PROJECT = "project"
    GITHUB = "github"
    ASSESSMENT = "assessment"
    INTERNSHIP = "internship"
    PROFESSIONAL_EXPERIENCE = "professional_experience"
    COURSE = "course"
    CERTIFICATION = "certification"
    OTHER = "other"

class CandidateEvidenceCreate(BaseModel):
    skill_slug: str
    evidence_type: EvidenceType
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    date_obtained: Optional[date] = None

class CandidateEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID
    skill_id: UUID
    skill_slug: str
    canonical_name: str
    evidence_type: str
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    raw_metadata: Dict[str, Any] = {}
    verification_status: str
    confidence_score: float
    date_obtained: Optional[date] = None
    created_at: datetime
