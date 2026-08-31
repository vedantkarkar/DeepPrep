"""
Pydantic Schemas for Preparation Planning and Roadmap Representation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class PreparationActivity(BaseModel):
    skill_slug: str
    canonical_name: str
    activity_type: str = Field(
        ...,
        description="Type of activity: LEARN (new concepts), PRACTICE (problem-solving/projects), ASSESS (validation tasks), MAINTAIN (revision)"
    )
    allocated_hours: float
    rationale: str

class WeeklySchedule(BaseModel):
    week_number: int
    focus_theme: str
    total_hours: float
    activities: List[PreparationActivity]

class PreparationMilestone(BaseModel):
    week_target: int
    title: str
    description: str
    skills_involved: List[str]

class PriorityArea(BaseModel):
    skill_slug: str
    canonical_name: str
    category: str
    required_level: int
    estimated_level: int
    gap_levels: int
    priority_tier: str  # high, medium, maintenance
    allocated_hours: float
    rationale: str

class PreparationPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    report_id: UUID
    total_hours_allocated: int
    available_hours_per_week: int
    weeks_until_target: int
    capacity_note: str
    priority_areas: List[PriorityArea]
    schedule: List[WeeklySchedule]
    milestones: List[PreparationMilestone]
    created_at: datetime
