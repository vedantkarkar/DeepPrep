from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime

class ReadinessItemBreakdownResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_slug: str
    canonical_name: str
    category: str
    required_level: int
    estimated_level: int
    importance_weight: float
    gap_score: float
    classification: str # strength, aligned, moderate_gap, critical_gap
    supporting_evidence_ids: List[UUID] = []
    explanation: str

class ReadinessReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    report_id: UUID
    session_id: UUID
    candidate_id: UUID
    job_id: UUID
    overall_readiness_score: int
    technical_readiness_score: int
    evidence_confidence_score: str
    eligibility_status: str
    eligibility_summary: Dict[str, Any]
    strengths_summary: List[str]
    critical_gaps_summary: List[Dict[str, Any]]
    item_breakdowns: List[ReadinessItemBreakdownResponse] = []
    generated_at: datetime
