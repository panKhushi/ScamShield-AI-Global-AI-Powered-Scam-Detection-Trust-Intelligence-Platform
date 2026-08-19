from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)  # Supabase user_id (sub claim)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="user")  # user | admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    scans = relationship("Scan", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")


class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # nullable: anonymous scans allowed
    input_type = Column(String)  # url | job | email | company | recruiter
    raw_input = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="scans")
    scan_result = relationship("ScanResult", back_populates="scan", uselist=False)
    url = relationship("Url", back_populates="scan", uselist=False)
    email = relationship("Email", back_populates="scan", uselist=False)
    company = relationship("Company", back_populates="scan", uselist=False)
    recruiter = relationship("Recruiter", back_populates="scan", uselist=False)


class ScanResult(Base):
    __tablename__ = "scan_results"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    trust_score = Column(Integer)
    verdict = Column(String)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    scan = relationship("Scan", back_populates="scan_result")
    evidence_items = relationship("Evidence", back_populates="scan_result")
    model_predictions = relationship("ModelPrediction", back_populates="scan_result")


class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, index=True)
    domain_name = Column(String, unique=True, index=True)
    reputation_snapshot = Column(JSON, nullable=True)
    last_checked = Column(DateTime(timezone=True), server_default=func.now())

    features = relationship("DomainFeature", back_populates="domain", uselist=False)


class DomainFeature(Base):
    __tablename__ = "domain_features"
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    domain_age_days = Column(Integer, nullable=True)
    has_https = Column(Boolean, nullable=True)
    has_hyphen = Column(Boolean, nullable=True)
    subdomain_count = Column(Integer, nullable=True)
    website_traffic_rank = Column(Integer, nullable=True)

    domain = relationship("Domain", back_populates="features")


class Url(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=True)
    full_url = Column(String)
    lexical_features = Column(JSON, nullable=True)

    scan = relationship("Scan", back_populates="url")


class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    body_text = Column(Text)
    header_analysis = Column(JSON, nullable=True)

    scan = relationship("Scan", back_populates="email")


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    company_name = Column(String)
    website = Column(String)
    consistency_score = Column(Float, nullable=True)

    scan = relationship("Scan", back_populates="company")


class Recruiter(Base):
    __tablename__ = "recruiters"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    recruiter_email = Column(String)
    claimed_company = Column(String)
    consistency_score = Column(Float, nullable=True)

    scan = relationship("Scan", back_populates="recruiter")


class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=True)
    source = Column(String)  # "google_safe_browsing" | "virustotal"
    raw_response = Column(JSON)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())


class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, index=True)
    scan_result_id = Column(Integer, ForeignKey("scan_results.id"))
    name = Column(String)
    weight = Column(Float)
    status = Column(String)  # good | warning | bad
    detail = Column(Text)

    scan_result = relationship("ScanResult", back_populates="evidence_items")


class RiskScore(Base):
    __tablename__ = "risk_scores"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    score = Column(Integer)
    component_breakdown = Column(JSON)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    id = Column(Integer, primary_key=True, index=True)
    scan_result_id = Column(Integer, ForeignKey("scan_results.id"))
    model_name = Column(String)  # "url_randomforest" | "job_logreg" | "email_logreg"
    model_version = Column(String, nullable=True)
    probability = Column(Float)
    explanation = Column(JSON, nullable=True)  # SHAP top features, if applicable

    scan_result = relationship("ScanResult", back_populates="model_predictions")


class ExportedReport(Base):
    """Exportable report file metadata (per their spec — distinct from user feedback/community reports)."""
    __tablename__ = "exported_reports"
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    file_reference = Column(String, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class Feedback(Base):
    """User-submitted correctness feedback / community scam reports."""
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=True)
    target_value = Column(String, index=True)
    category = Column(String)
    description = Column(Text)
    evidence_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="feedback")


class Blacklist(Base):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, index=True)
    value_type = Column(String)  # domain | email
    reason = Column(String, nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())


class Whitelist(Base):
    __tablename__ = "whitelist"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, index=True)
    value_type = Column(String)
    added_at = Column(DateTime(timezone=True), server_default=func.now())