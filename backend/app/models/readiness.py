import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class ReadinessReport(Base):
    __tablename__ = "readiness_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("preparation_sessions.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    overall_readiness_score = Column(Integer, nullable=False) # 0 to 100
    technical_readiness_score = Column(Integer, nullable=False) # 0 to 100
    evidence_confidence_score = Column(String(50), nullable=False) # low, medium, high
    eligibility_status = Column(String(50), nullable=False) # eligible, partially_eligible, ineligible
    eligibility_summary = Column(JSONB, default=dict, nullable=False)
    strengths_summary = Column(JSONB, default=list, nullable=False)
    critical_gaps_summary = Column(JSONB, default=list, nullable=False)
    generated_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    session = relationship("PreparationSession", back_populates="readiness_reports")
    item_breakdowns = relationship("ReadinessItemBreakdown", back_populates="report", cascade="all, delete-orphan")
    preparation_plans = relationship("PreparationPlan", back_populates="report", cascade="all, delete-orphan")


class ReadinessItemBreakdown(Base):
    __tablename__ = "readiness_item_breakdowns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("readiness_reports.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    competency_requirement_id = Column(UUID(as_uuid=True), ForeignKey("job_competency_requirements.id", ondelete="SET NULL"), nullable=True)
    required_level = Column(Integer, nullable=False)
    estimated_level = Column(Integer, nullable=False)
    importance_weight = Column(Float, nullable=False)
    gap_score = Column(Float, nullable=False) # (required - estimated) * weight
    classification = Column(String(50), nullable=False) # strength, aligned, moderate_gap, critical_gap
    supporting_evidence_ids = Column(JSONB, default=list, nullable=False)
    explanation = Column(Text, nullable=False)

    report = relationship("ReadinessReport", back_populates="item_breakdowns")
    skill = relationship("Skill")
