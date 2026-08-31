from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID

class SkillAliasResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    alias: str

class SkillSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    canonical_name: str
    slug: str
    category: str
    description: Optional[str] = None
    aliases: List[str] = []
