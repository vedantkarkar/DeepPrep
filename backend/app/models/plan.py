import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class PreparationPlan(Base):
    __tablename__ = "preparation_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("readiness_reports.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("preparation_sessions.id", ondelete="CASCADE"), nullable=False)
    total_hours_allocated = Column(Integer, nullable=False)
    schedule = Column(JSONB, default=list, nullable=False)
    milestones = Column(JSONB, default=list, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    report = relationship("ReadinessReport", back_populates="preparation_plans")
    session = relationship("PreparationSession", back_populates="preparation_plans")
