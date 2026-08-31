import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Date, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class CandidateEvidence(Base):
    __tablename__ = "candidate_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String(50), nullable=False) # self_report, academic_coursework, project, github, assessment, internship, professional_experience, course, certification, other
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    raw_metadata = Column(JSONB, default=dict, nullable=False)
    verification_status = Column(String(50), default="unverified", nullable=False) # unverified, verified, self_attested
    confidence_score = Column(Float, default=0.5, nullable=False) # 0.0 to 1.0
    date_obtained = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    candidate = relationship("Candidate", back_populates="evidence")
    skill = relationship("Skill", back_populates="evidence")
