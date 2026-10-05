from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import HistoricalEvent, HistoricalRecord
from app.models import TrendResponse, TrendPoint
from app.services.auth_service import get_optional_current_user
from app.services.historical_intelligence import WINDOW_DAYS

router = APIRouter(tags=["analytics"])


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


@router.get("/analytics/trends", response_model=TrendResponse)
def get_trends(
    db: Session = Depends(get_db),
    _: dict | None = Depends(get_optional_current_user),
):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=WINDOW_DAYS)
    events = db.query(HistoricalEvent).filter(HistoricalEvent.created_at >= cutoff).all()
    buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"scans": 0, "reports": 0, "dangerous": 0})
    for event in events:
        day = _aware(event.created_at).date().isoformat()
        if event.event_type == "scan":
            buckets[day]["scans"] += 1
        elif event.event_type == "report":
            buckets[day]["reports"] += 1
        if event.classification in {"dangerous", "scam"}:
            buckets[day]["dangerous"] += 1

    points = [TrendPoint(date=day, **buckets[day]) for day in sorted(buckets)]
    top_records = db.query(HistoricalRecord).order_by(HistoricalRecord.confirmed_report_count.desc()).limit(10).all()
    top_entities = [
        {
            "entity_type": record.entity_type,
            "scan_count": record.scan_count,
            "confirmed_report_count": record.confirmed_report_count,
            "last_seen": _aware(record.last_seen).isoformat(),
        }
        for record in top_records
        if record.confirmed_report_count > 0
    ]
    return TrendResponse(window_days=WINDOW_DAYS, points=points, top_entities=top_entities)
