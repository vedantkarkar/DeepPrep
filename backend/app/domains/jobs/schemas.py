from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

class ExtractedEligibilityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    criterion_type: str # degree, branch, min_experience_years, max_experience_years, min_graduation_year, location_constraint
    expected_value: Any
    operator: str = "EQUALS" # EQUALS, IN, GREATER_EQUAL, LESS_EQUAL
    is_mandatory: bool = True
    supporting_text: Optional[str] = None
    provenance: str = "extracted_from_jd"

class ExtractedCompetencyItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    raw_skill_text: str
    is_required: bool = True
    importance_level: str = "required" # required, preferred, nice_to_have
    interview_relevance: Optional[str] = None # high, medium, low
    supporting_text: Optional[str] = None
    is_explicit: bool = True
    provenance: str = "extracted_from_jd"

class RawJobExtraction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    target_role: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    employment_type: Optional[str] = "Full-time"
    eligibility_requirements: List[ExtractedEligibilityItem] = Field(default_factory=list)
    competency_requirements: List[ExtractedCompetencyItem] = Field(default_factory=list)
    raw_description: str = ""

class NormalizedCompetencyItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    skill_id: UUID
    skill_slug: str
    canonical_name: str
    category: str
    required_proficiency_level: int = Field(ge=1, le=5, default=3)
    importance_weight: float = Field(ge=0.1, le=1.0, default=0.85)
    is_required: bool = True
    interview_relevance_level: str = "medium" # high, medium, low
    supporting_text: Optional[str] = None
    importance_provenance: str = "derived"

class UnresolvedJobSkillItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    raw_term: str
    supporting_text: Optional[str] = None
    reason: str = "Not recognized in canonical skill taxonomy"

class ParsedJobDescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    company_name: str
    target_role: str
    location_city: Optional[str] = "Pune"
    location_state: Optional[str] = "Maharashtra"
    employment_type: Optional[str] = "Full-time"
    source_url: Optional[str] = None
    source_type: str = "manual_entry" # fixture, direct_company, job_board, manual_entry
    posted_date: Optional[date] = None
    eligibility_requirements: List[ExtractedEligibilityItem] = Field(default_factory=list)
    competency_requirements: List[NormalizedCompetencyItem] = Field(default_factory=list)
    unresolved_skills: List[UnresolvedJobSkillItem] = Field(default_factory=list)
    raw_description: str

class JobCreateFromParsedRequest(BaseModel):
    title: str
    company_name: str
    target_role: str
    location_city: Optional[str] = "Pune"
    location_state: Optional[str] = "Maharashtra"
    employment_type: Optional[str] = "Full-time"
    source_url: Optional[str] = None
    source_type: str = "manual_entry"
    posted_date: Optional[date] = None
    raw_description: str
    eligibility_requirements: List[ExtractedEligibilityItem] = Field(default_factory=list)
    competency_requirements: List[NormalizedCompetencyItem] = Field(default_factory=list)
