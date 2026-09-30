from pydantic import BaseModel
from typing import List

class AnalyzeRequest(BaseModel):
    input_type: str   # "url" | "email" | "job" | "app"
    value: str

class ScoreFactor(BaseModel):
    name: str
    weight: float
    status: str        # "good" | "warning" | "bad"
    detail: str

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

class ReportRequest(BaseModel):
    target_value: str
    target_type: str
    category: str
    description: str
    evidence_url: str | None = None

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