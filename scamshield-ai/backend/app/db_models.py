from sqlalchemy import Column, Integer, String, DateTime, JSON
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())