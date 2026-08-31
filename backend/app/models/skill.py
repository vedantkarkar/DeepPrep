import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    canonical_name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False) # programming, cs_fundamentals, database, backend, frontend, cloud, devops, ai_ml, data, testing, system_design, soft_skill
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    aliases = relationship("SkillAlias", back_populates="skill", cascade="all, delete-orphan")
    candidate_claims = relationship("CandidateSkill", back_populates="skill")
    evidence = relationship("CandidateEvidence", back_populates="skill")
    competency_requirements = relationship("JobCompetencyRequirement", back_populates="skill")


class SkillAlias(Base):
    __tablename__ = "skill_aliases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    alias = Column(String(100), nullable=False)
    normalized_alias = Column(String(100), unique=True, nullable=False)

    skill = relationship("Skill", back_populates="aliases")
