from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db_models import ScanRecord

CACHE_WINDOW_HOURS = 24

def get_recent_scan(db: Session, domain: str) -> ScanRecord | None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=CACHE_WINDOW_HOURS)
    return (
        db.query(ScanRecord)
        .filter(ScanRecord.domain == domain, ScanRecord.created_at >= cutoff)
        .order_by(ScanRecord.created_at.desc())
        .first()
    )