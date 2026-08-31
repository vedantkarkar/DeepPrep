from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime

class PreparationPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    session_id: UUID
    total_hours_allocated: int
    schedule: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    created_at: datetime
