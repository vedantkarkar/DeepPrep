from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime

class PreparationSessionCreate(BaseModel):
    candidate_id: UUID
    job_id: UUID
    available_hours_per_week: int = Field(default=15, ge=1, le=80)
    weeks_until_target: int = Field(default=6, ge=1, le=52)
    target_date: Optional[date] = None

class PreparationSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID
    job_id: UUID
    available_hours_per_week: int
    weeks_until_target: int
    target_date: Optional[date] = None
    status: str
    created_at: datetime
