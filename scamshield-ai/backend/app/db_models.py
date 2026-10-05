from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database import Base

class ScanRecord(Base):
    __tablename__ = "scan_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)
    input_value = Column(String, index=True)
    input_type = Column(String)
    domain = Column(String, index=True)
    trust_score = Column(Integer)
    verdict = Column(String)
    factors = Column(JSON)          # store the full factors list as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)           # Supabase user's "sub" claim
    target_value = Column(String, index=True)       # domain, email, or job text snippet
    target_type = Column(String)                    # "url" | "job" | "email"
    category = Column(String)                       # e.g. "payment_scam", "fake_job", "phishing"
    description = Column(String)
    evidence_url = Column(String, nullable=True)
    review_status = Column(String, nullable=True, default="pending", index=True)
    moderator_note = Column(Text, nullable=True)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HistoricalRecord(Base):
    __tablename__ = "historical_records"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True, nullable=False)
    entity_hash = Column(String, unique=True, index=True, nullable=False)
    normalized_value = Column(Text, nullable=False)
    original_value = Column(Text, nullable=True)
    risk_score = Column(Integer, nullable=True)
    classification = Column(String, nullable=True)
    source = Column(String, nullable=True)
    first_seen = Column(DateTime(timezone=True), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=False, index=True)
    scan_count = Column(Integer, nullable=False, default=0)
    confirmed_report_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class HistoricalEvent(Base):
    __tablename__ = "historical_events"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("historical_records.id"), index=True, nullable=False)
    event_type = Column(String, nullable=False)
    source = Column(String, nullable=False)
    classification = Column(String, nullable=True)
    risk_score = Column(Integer, nullable=True)
    user_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)