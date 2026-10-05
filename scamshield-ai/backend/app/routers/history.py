from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.db_models import ScanRecord
from app.models import AnalyzeRequest, HistoricalIntelligence
from app.services.auth_service import get_optional_current_user
from app.services.historical_intelligence import check_history

router = APIRouter()


@router.post("/history/check", response_model=HistoricalIntelligence)
def check_entity_history(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    user: dict | None = Depends(get_optional_current_user),
):
    return check_history(db, request.input_type, request.value)

@router.get("/history")
def get_history(
    limit: int = 100,
    db: Session = Depends(get_db),
    user: dict | None = Depends(get_optional_current_user),
):
    query = db.query(ScanRecord).order_by(ScanRecord.created_at.desc())

    if user:
        query = query.filter(ScanRecord.user_id == user.get("sub"))

    records = query.limit(limit).all()
    return [
        {
            "id": r.id,
            "input_value": r.input_value,
            "input_type": r.input_type,
            "domain": r.domain,
            "trust_score": r.trust_score,
            "verdict": r.verdict,
            "factors": r.factors or [],
            "created_at": r.created_at,
        }
        for r in records
    ]