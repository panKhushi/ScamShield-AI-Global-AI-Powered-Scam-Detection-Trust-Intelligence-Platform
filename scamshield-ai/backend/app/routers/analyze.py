from fastapi import APIRouter, Depends
import logging
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from app.models import AnalyzeRequest, AnalyzeResponse
from app.database import get_db
from app.db_models import ScanRecord
from app.services.whois_service import analyze_whois, get_raw_domain_age_days
from app.services.safe_browsing_service import analyze_safe_browsing
from app.services.virustotal_service import analyze_virustotal
from app.services.cache_service import get_recent_scan
from app.services.auth_service import get_current_user
from app.services.report_service import get_community_reports_factor
from app.services.job_analyzer import analyze_job_text
from app.services.email_analyzer import analyze_email_text
from app.services.sms_analyzer import analyze_sms_text
from app.services.recommendation_engine import generate_recommendations
from app.services.risk_fusion_engine import fuse_risk, build_anomaly_factor
from app.services.website_analyzer import analyze_website_content
from app.services.scorer import compute_rule_based_score
from app.ml.collect_features import collect_ml_features
from app.ml.predictor import predict_scam_probability
from app.ml.text_predictor import (
    predict_job_scam_probability,
    predict_email_phishing_probability,
    predict_sms_scam_probability,
)
from app.ml.explainability import explain_prediction
from app.ml.anomaly_predictor import detect_anomaly
from app.limiter import rate_limit
from app.services.normalized_write_service import write_normalized_scan


router = APIRouter()
logger = logging.getLogger(__name__)


def extract_domain(value: str) -> str:
    if not value.startswith(("http://", "https://")):
        value = "http://" + value
    return urlparse(value).netloc


def persist_normalized_scan_safely(
    db: Session,
    user_id: str | None,
    input_type: str,
    raw_input: str,
    domain_name: str | None,
    trust_score: int,
    verdict: str,
    factors: list,
    ml_probability: float,
    ml_model_name: str,
    explanation: list | None,
) -> None:
    try:
        write_normalized_scan(
            db=db,
            user_id=user_id,
            input_type=input_type,
            raw_input=raw_input,
            domain_name=domain_name,
            trust_score=trust_score,
            verdict=verdict,
            factors=factors,
            ml_probability=ml_probability,
            ml_model_name=ml_model_name,
            explanation=explanation,
        )
    except Exception:
        db.rollback()
        logger.exception("Normalized %s scan write failed; returning the completed scan result", input_type)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(body: AnalyzeRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user), _: None = Depends(rate_limit(10, 60))):
    domain = extract_domain(body.value)

    cached = get_recent_scan(db, domain)
    if cached:
        return AnalyzeResponse(
            input_value=cached.input_value,
            input_type=cached.input_type,
            trust_score=cached.trust_score,
            verdict=cached.verdict,
            factors=cached.factors,
            ml_scam_probability=cached.factors[0].get("ml_scam_probability", 0) if cached.factors else 0,
            recommendations=[],
            risk_breakdown={},
            explanation=[],
        )

    whois_factor = analyze_whois(domain)
    safe_browsing_factor = await analyze_safe_browsing(body.value)
    virustotal_factor = await analyze_virustotal(body.value)
    community_factor = get_community_reports_factor(db, domain)
    factors = [whois_factor, safe_browsing_factor, virustotal_factor, community_factor]

    website_factors = analyze_website_content(body.value)
    factors.extend(website_factors)

    domain_age_days = get_raw_domain_age_days(domain)
    ml_features = collect_ml_features(body.value, domain_age_days)
    scam_probability = predict_scam_probability(ml_features)
    explanation = explain_prediction(ml_features)

    preliminary_score = compute_rule_based_score(factors)
    anomaly_result = detect_anomaly(preliminary_score, factors)
    anomaly_factor = build_anomaly_factor(anomaly_result)
    factors.append(anomaly_factor)

    final_score, verdict, risk_breakdown = fuse_risk(factors, scam_probability)
    recommendations = generate_recommendations(factors, verdict)

    record = ScanRecord(
        input_value=body.value,
        input_type=body.input_type,
        domain=domain,
        trust_score=final_score,
        verdict=verdict,
        factors=[f.dict() for f in factors],
    )
    db.add(record)
    db.commit()


    persist_normalized_scan_safely(
        db=db,
        user_id=user.get("sub"),
        input_type=body.input_type,
        raw_input=body.value,
        domain_name=domain,
        trust_score=final_score,
        verdict=verdict,
        factors=factors,
        ml_probability=scam_probability,
        ml_model_name="url_randomforest",
        explanation=explanation,
    )

    return AnalyzeResponse(
        input_value=body.value,
        input_type=body.input_type,
        trust_score=final_score,
        verdict=verdict,
        factors=factors,
        ml_scam_probability=scam_probability,
        recommendations=recommendations,
        risk_breakdown=risk_breakdown,
        explanation=explanation,
    )


@router.post("/analyze-job", response_model=AnalyzeResponse)
async def analyze_job(body: AnalyzeRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user), _: None = Depends(rate_limit(10, 60))):
    factors = analyze_job_text(body.value)
    ml_probability = predict_job_scam_probability(body.value)
    score, verdict, risk_breakdown = fuse_risk(factors, ml_probability)
    recommendations = generate_recommendations(factors, verdict)

    record = ScanRecord(
        input_value=body.value[:500],
        input_type="job",
        domain="N/A",
        trust_score=score,
        verdict=verdict,
        factors=[f.dict() for f in factors],
    )
    db.add(record)
    db.commit()
    persist_normalized_scan_safely(
        db=db,
        user_id=user.get("sub"),
        input_type="job",
        raw_input=body.value,
        domain_name=None,
        trust_score=score,
        verdict=verdict,
        factors=factors,
        ml_probability=ml_probability,
        ml_model_name="job_logreg",
        explanation=None,
    )

    return AnalyzeResponse(
        input_value=body.value[:200] + ("..." if len(body.value) > 200 else ""),
        input_type="job",
        trust_score=score,
        verdict=verdict,
        factors=factors,
        ml_scam_probability=ml_probability,
        recommendations=recommendations,
        risk_breakdown=risk_breakdown,
        explanation=[],
    )


@router.post("/analyze-email", response_model=AnalyzeResponse)
async def analyze_email(body: AnalyzeRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user), _: None = Depends(rate_limit(10, 60))):
    factors = analyze_email_text(body.value)
    ml_probability = predict_email_phishing_probability(body.value)
    score, verdict, risk_breakdown = fuse_risk(factors, ml_probability)
    recommendations = generate_recommendations(factors, verdict)

    record = ScanRecord(
        input_value=body.value[:500],
        input_type="email",
        domain="N/A",
        trust_score=score,
        verdict=verdict,
        factors=[f.dict() for f in factors],
    )
    db.add(record)
    db.commit()
    persist_normalized_scan_safely(
        db=db,
        user_id=user.get("sub"),
        input_type="email",
        raw_input=body.value,
        domain_name=None,
        trust_score=score,
        verdict=verdict,
        factors=factors,
        ml_probability=ml_probability,
        ml_model_name="email_logreg",
        explanation=None,
    )

    return AnalyzeResponse(
        input_value=body.value[:200] + ("..." if len(body.value) > 200 else ""),
        input_type="email",
        trust_score=score,
        verdict=verdict,
        factors=factors,
        ml_scam_probability=ml_probability,
        recommendations=recommendations,
        risk_breakdown=risk_breakdown,
        explanation=[],
    )


@router.post("/analyze-sms", response_model=AnalyzeResponse)
async def analyze_sms(body: AnalyzeRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user), _: None = Depends(rate_limit(10, 60))):
    factors = analyze_sms_text(body.value)
    ml_probability = predict_sms_scam_probability(body.value)
    score, verdict, risk_breakdown = fuse_risk(factors, ml_probability)
    recommendations = generate_recommendations(factors, verdict)

    record = ScanRecord(
        input_value=body.value[:500],
        input_type="sms",
        domain="N/A",
        trust_score=score,
        verdict=verdict,
        factors=[f.dict() for f in factors],
    )
    db.add(record)
    db.commit()
    persist_normalized_scan_safely(
        db=db,
        user_id=user.get("sub"),
        input_type="sms",
        raw_input=body.value,
        domain_name=None,
        trust_score=score,
        verdict=verdict,
        factors=factors,
        ml_probability=ml_probability,
        ml_model_name="sms_logreg",
        explanation=None,
    )

    return AnalyzeResponse(
        input_value=body.value[:200] + ("..." if len(body.value) > 200 else ""),
        input_type="sms",
        trust_score=score,
        verdict=verdict,
        factors=factors,
        ml_scam_probability=ml_probability,
        recommendations=recommendations,
        risk_breakdown=risk_breakdown,
        explanation=[],
    )


@router.get("/whoami")
def whoami(user: dict = Depends(get_current_user)):
    return {"user_id": user.get("sub"), "email": user.get("email")}