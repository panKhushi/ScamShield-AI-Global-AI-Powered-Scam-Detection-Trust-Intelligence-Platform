from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import ScanRecord
from app.models import CompanyVerifyRequest, RecruiterVerifyRequest, AnalyzeResponse
from app.services.verification_service import verify_company_domain_match, verify_recruiter_email_domain
from app.services.whois_service import analyze_whois
from app.services.safe_browsing_service import analyze_safe_browsing
from app.services.virustotal_service import analyze_virustotal
from app.services.risk_fusion_engine import fuse_risk
from app.services.recommendation_engine import generate_recommendations

router = APIRouter()


def extract_domain(value: str) -> str:
    from urllib.parse import urlparse
    if not value.startswith(("http://", "https://")):
        value = "http://" + value
    return urlparse(value).netloc


@router.post("/verify-company", response_model=AnalyzeResponse)
async def verify_company(request: CompanyVerifyRequest, db: Session = Depends(get_db)):
    domain = extract_domain(request.website)

    consistency_factor = verify_company_domain_match(request.company_name, domain)
    whois_factor = analyze_whois(domain)
    safe_browsing_factor = await analyze_safe_browsing(request.website)
    virustotal_factor = await analyze_virustotal(request.website)

    factors = [consistency_factor, whois_factor, safe_browsing_factor, virustotal_factor]
    score, verdict, risk_breakdown = fuse_risk(factors, ml_scam_probability=0.0)
    recommendations = generate_recommendations(factors, verdict)

    record = ScanRecord(
        input_value=f"{request.company_name} ({request.website})",
        input_type="company",
        domain=domain,
        trust_score=score,
        verdict=verdict,
        factors=[f.dict() for f in factors],
    )
    db.add(record)
    db.commit()

    return AnalyzeResponse(
        input_value=f"{request.company_name} ({request.website})",
        input_type="company",
        trust_score=score,
        verdict=verdict,
        factors=factors,
        ml_scam_probability=0.0,
        recommendations=recommendations,
        risk_breakdown=risk_breakdown,
        explanation=[],
    )


@router.post("/verify-recruiter", response_model=AnalyzeResponse)
async def verify_recruiter(request: RecruiterVerifyRequest, db: Session = Depends(get_db)):
    consistency_factor = verify_recruiter_email_domain(request.recruiter_email, request.claimed_company)

    factors = [consistency_factor]
    score, verdict, risk_breakdown = fuse_risk(factors, ml_scam_probability=0.0)
    recommendations = generate_recommendations(factors, verdict)

    record = ScanRecord(
        input_value=f"{request.recruiter_email} claiming {request.claimed_company}",
        input_type="recruiter",
        domain="N/A",
        trust_score=score,
        verdict=verdict,
        factors=[f.dict() for f in factors],
    )
    db.add(record)
    db.commit()

    return AnalyzeResponse(
        input_value=f"{request.recruiter_email} claiming {request.claimed_company}",
        input_type="recruiter",
        trust_score=score,
        verdict=verdict,
        factors=factors,
        ml_scam_probability=0.0,
        recommendations=recommendations,
        risk_breakdown=risk_breakdown,
        explanation=[],
    )