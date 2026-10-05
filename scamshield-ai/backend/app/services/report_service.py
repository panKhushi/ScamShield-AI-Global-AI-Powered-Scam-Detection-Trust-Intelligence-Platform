from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db_models import Report
from app.models import ScoreFactor

REPORT_LOOKBACK_DAYS = 90

def get_report_count(db: Session, target_value: str) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=REPORT_LOOKBACK_DAYS)
    return (
        db.query(Report)
        .filter(
            Report.target_value == target_value,
            Report.created_at >= cutoff,
            Report.review_status.in_(["approved", None]),
        )
        .count()
    )


def get_community_reports_factor(db: Session, target_value: str) -> ScoreFactor:
    count = get_report_count(db, target_value)

    if count == 0:
        return ScoreFactor(
            name="Community Reports", weight=0.25, status="good",
            detail="No user reports found for this target"
        )
    elif count <= 2:
        return ScoreFactor(
            name="Community Reports", weight=0.25, status="warning",
            detail=f"{count} user report(s) filed in the last {REPORT_LOOKBACK_DAYS} days"
        )
    else:
        return ScoreFactor(
            name="Community Reports", weight=0.25, status="bad",
            detail=f"{count} user reports filed in the last {REPORT_LOOKBACK_DAYS} days — high risk"
        )