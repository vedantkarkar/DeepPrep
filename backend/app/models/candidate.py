import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True) # Optional for prototype. No auth/account management.
    phone = Column(String(50), nullable=True)
    location_city = Column(String(100), default="Pune")
    location_state = Column(String(100), default="Maharashtra")
    degree = Column(String(100), nullable=True)
    branch = Column(String(100), nullable=True)
    institution = Column(String(255), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    student_status = Column(String(50), nullable=True) # final_year, recent_graduate, early_career
    education_confirmed_by_user = Column(Boolean, default=False, nullable=False)
    raw_education_claims = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    evidence = relationship("CandidateEvidence", back_populates="candidate", cascade="all, delete-orphan")
    sessions = relationship("PreparationSession", back_populates="candidate", cascade="all, delete-orphan")


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    claim_source = Column(String(50), nullable=False, default="resume") # resume, manual_entry
    raw_claim_text = Column(Text, nullable=True)
    confirmed_by_user = Column(Boolean, default=False, nullable=False)
    self_assessment_level = Column(Integer, nullable=True) # 1-5 SUBJECTIVE ONLY. NOT proficiency. Excluded from readiness.
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("candidate_id", "skill_id", name="unique_candidate_skill"),
    )

    candidate = relationship("Candidate", back_populates="skills")
    skill = relationship("Skill", back_populates="candidate_claims")
