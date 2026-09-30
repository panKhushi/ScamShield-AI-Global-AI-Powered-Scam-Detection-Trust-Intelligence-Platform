from sqlalchemy.orm import Session
from app.db_models_v2 import Scan, ScanResult, Evidence, ModelPrediction, Domain, Url
from app.db_models_v2 import User
from app.models import ScoreFactor


def get_or_create_domain(db: Session, domain_name: str) -> Domain:
    domain = db.query(Domain).filter(Domain.domain_name == domain_name).first()
    if domain is None:
        domain = Domain(domain_name=domain_name)
        db.add(domain)
        db.flush()  # get domain.id without a full commit yet
    return domain


def write_normalized_scan(
    db: Session,
    user_id: str | None,
    input_type: str,
    raw_input: str,
    domain_name: str | None,
    trust_score: int,
    verdict: str,
    factors: list[ScoreFactor],
    ml_probability: float,
    ml_model_name: str,
    explanation: list | None = None,
):
    """
    Writes a full normalized record set for one scan: Scan -> ScanResult ->
    Evidence (one row per factor) -> ModelPrediction, plus Domain/Url linkage
    for URL scans. Runs alongside the existing flat ScanRecord write —
    does not replace it.
    """
    if user_id is not None and db.get(User, user_id) is None:
        db.add(User(id=user_id))
        db.flush()

    scan = Scan(user_id=user_id, input_type=input_type, raw_input=raw_input[:1000])
    db.add(scan)
    db.flush()

    if domain_name and domain_name != "N/A":
        domain = get_or_create_domain(db, domain_name)
        url_row = Url(scan_id=scan.id, domain_id=domain.id, full_url=raw_input[:500])
        db.add(url_row)

    scan_result = ScanResult(
        scan_id=scan.id,
        trust_score=trust_score,
        verdict=verdict,
        confidence=ml_probability,
    )
    db.add(scan_result)
    db.flush()

    for factor in factors:
        db.add(Evidence(
            scan_result_id=scan_result.id,
            name=factor.name,
            weight=factor.weight,
            status=factor.status,
            detail=factor.detail,
        ))

    db.add(ModelPrediction(
        scan_result_id=scan_result.id,
        model_name=ml_model_name,
        probability=ml_probability,
        explanation=explanation if explanation else None,
    ))

    db.commit()