import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class PreparationSession(Base):
    __tablename__ = "preparation_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    available_hours_per_week = Column(Integer, default=15, nullable=False)
    weeks_until_target = Column(Integer, default=6, nullable=False)
    target_date = Column(Date, nullable=True)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    candidate = relationship("Candidate", back_populates="sessions")
    job = relationship("Job", back_populates="sessions")
    readiness_reports = relationship("ReadinessReport", back_populates="session", cascade="all, delete-orphan")
    preparation_plans = relationship("PreparationPlan", back_populates="session", cascade="all, delete-orphan")
