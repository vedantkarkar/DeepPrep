import uuid
from datetime import datetime, date, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Date, Float, Boolean, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    target_role = Column(String(100), nullable=False)
    company_name = Column(String(255), nullable=False)
    location = Column(String(100), nullable=True)
    raw_description = Column(Text, nullable=False)
    source_url = Column(Text, nullable=True)
    source_type = Column(String(50), default="fixture", nullable=False) # fixture, direct_company, job_board, manual_entry
    posted_date = Column(Date, nullable=True)
    last_seen_date = Column(Date, default=date.today, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    eligibility_requirements = relationship("JobEligibilityRequirement", back_populates="job", cascade="all, delete-orphan")
    competency_requirements = relationship("JobCompetencyRequirement", back_populates="job", cascade="all, delete-orphan")
    sessions = relationship("PreparationSession", back_populates="job", cascade="all, delete-orphan")


class JobEligibilityRequirement(Base):
    __tablename__ = "job_eligibility_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    criterion_type = Column(String(50), nullable=False) # degree, branch, min_graduation_year, max_graduation_year, min_experience_years, location_constraint
    operator = Column(String(20), default="EQUALS", nullable=False) # EQUALS, IN, GREATER_EQUAL, LESS_EQUAL
    expected_value = Column(JSONB, nullable=False) # e.g. ["B.Tech", "B.E."], 2024, 0
    is_mandatory = Column(Boolean, default=True, nullable=False)
    provenance = Column(String(50), default="extracted_from_jd", nullable=False) # curated, extracted_from_jd, derived
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    job = relationship("Job", back_populates="eligibility_requirements")


class JobCompetencyRequirement(Base):
    __tablename__ = "job_competency_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    is_required = Column(Boolean, default=True, nullable=False)
    importance_weight = Column(Float, default=1.0, nullable=False) # 0.1 to 1.0
    importance_provenance = Column(String(50), default="curated", nullable=False) # curated, extracted_from_jd, derived
    required_proficiency_level = Column(Integer, default=3, nullable=False) # 1 to 5
    interview_relevance_level = Column(String(20), default="medium", nullable=False) # low, medium, high
    interview_relevance_notes = Column(Text, nullable=True)
    evidence_expectation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("job_id", "skill_id", name="unique_job_competency"),
    )

    job = relationship("Job", back_populates="competency_requirements")
    skill = relationship("Skill", back_populates="competency_requirements")
