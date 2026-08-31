from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from enum import Enum
from uuid import UUID
from datetime import date

class InterviewRelevanceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ProvenanceType(str, Enum):
    CURATED = "curated"
    EXTRACTED_FROM_JD = "extracted_from_jd"
    DERIVED = "derived"

class JobEligibilityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    criterion_type: str
    operator: str = "EQUALS"
    expected_value: Any
    is_mandatory: bool = True
    provenance: Optional[str] = "extracted_from_jd"

class JobCompetencyItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    skill_id: Optional[UUID] = None
    skill_slug: Optional[str] = None
    canonical_name: Optional[str] = None
    category: Optional[str] = None
    is_required: bool = True
    importance_weight: float = Field(ge=0.1, le=1.0, default=1.0)
    importance_provenance: Optional[str] = "curated"
    required_proficiency_level: int = Field(ge=1, le=5, default=3)
    interview_relevance_level: Optional[str] = "medium"
    interview_relevance_notes: Optional[str] = None
    evidence_expectation: Optional[str] = None

class JobSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    target_role: str
    company_name: str
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    source_type: str
    posted_date: Optional[date] = None
    is_active: bool

class JobDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    target_role: str
    company_name: str
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    raw_description: str
    source_url: Optional[str] = None
    source_type: str
    posted_date: Optional[date] = None
    is_active: bool
    eligibility_requirements: List[JobEligibilityItem] = Field(default_factory=list)
    competency_requirements: List[JobCompetencyItem] = Field(default_factory=list)

# Alias for convenience
JobResponse = JobDetailResponse
