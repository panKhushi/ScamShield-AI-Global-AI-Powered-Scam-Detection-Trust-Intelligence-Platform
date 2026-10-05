from pydantic import BaseModel, Field
from typing import List

class AnalyzeRequest(BaseModel):
    input_type: str = Field(min_length=2, max_length=32)
    value: str = Field(min_length=1, max_length=20000)

class PhoneAnalyzeRequest(AnalyzeRequest):
    input_type: str = "phone"

class ScoreFactor(BaseModel):
    name: str
    weight: float
    status: str        # "good" | "warning" | "bad"
    detail: str

class HistoricalIntelligence(BaseModel):
    entity_type: str
    found: bool = False
    first_seen: str | None = None
    last_seen: str | None = None
    reports_last_3_months: int = 0
    scans_last_3_months: int = 0
    recent_reports: int = 0
    recency_status: str = "NO_HISTORICAL_DATA"
    historical_risk: str = "UNKNOWN"
    trend: str = "INSUFFICIENT_DATA"
    matches: List[dict] = []
    timeline: List[dict] = []

class FeatureExplanation(BaseModel):
    feature: str
    contribution: float
    direction: str

class AnalyzeResponse(BaseModel):
    input_value: str
    input_type: str
    trust_score: int
    verdict: str
    factors: List[ScoreFactor]
    ml_scam_probability: float
    recommendations: List[str] = []
    risk_breakdown: dict = {}
    explanation: List[FeatureExplanation] = []
    historical_intelligence: HistoricalIntelligence | None = None

class ReportRequest(BaseModel):
    target_value: str = Field(min_length=1, max_length=2000)
    target_type: str = Field(min_length=2, max_length=32)
    category: str = Field(min_length=2, max_length=64)
    description: str = Field(min_length=5, max_length=5000)
    evidence_url: str | None = Field(default=None, max_length=2048)

class ReportReviewRequest(BaseModel):
    review_status: str = Field(pattern="^(pending|approved|rejected)$")
    moderator_note: str | None = Field(default=None, max_length=2000)

class TrendPoint(BaseModel):
    date: str
    scans: int
    reports: int
    dangerous: int

class TrendResponse(BaseModel):
    window_days: int
    points: List[TrendPoint]
    top_entities: List[dict] = []

class ReportResponse(BaseModel):
    id: int
    target_value: str
    category: str
    description: str
    evidence_url: str | None = None
    created_at: str

class CompanyVerifyRequest(BaseModel):
    company_name: str
    website: str

class RecruiterVerifyRequest(BaseModel):
    recruiter_email: str
    claimed_company: str