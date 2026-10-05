import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import Report
from app.db_models_v2 import User
from app.models import ReportReviewRequest
from app.services.auth_service import get_current_user
from app.services.historical_intelligence import record_report

router = APIRouter(prefix="/admin", tags=["admin"])
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def require_admin(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    configured_admins = {
        email.strip().lower()
        for email in os.getenv("SCAMSHIELD_ADMIN_EMAILS", "").split(",")
        if email.strip()
    }
    configured_ids = {
        user_id.strip()
        for user_id in os.getenv("SCAMSHIELD_ADMIN_USER_IDS", "").split(",")
        if user_id.strip()
    }
    app_metadata = user.get("app_metadata") or {}
    if (
        user.get("email", "").lower() in configured_admins
        or user.get("sub") in configured_ids
        or app_metadata.get("role") == "admin"
    ):
        return user

    account = db.query(User).filter(User.id == user.get("sub")).first()
    if account is None or account.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user


@router.get("/reports")
def list_reports(
    status: str = Query("pending", pattern="^(pending|approved|rejected|all)$"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    query = db.query(Report).order_by(Report.created_at.desc())
    if status != "all":
        query = query.filter(Report.review_status == status)
    return [
        {
            "id": report.id,
            "target_value": report.target_value,
            "target_type": report.target_type,
            "category": report.category,
            "description": report.description,
            "evidence_url": report.evidence_url,
            "review_status": report.review_status,
            "moderator_note": report.moderator_note,
            "created_at": report.created_at,
        }
        for report in query.limit(200).all()
    ]


@router.patch("/reports/{report_id}")
def review_report(
    report_id: int,
    request: ReportReviewRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    was_approved = report.review_status == "approved"
    report.review_status = request.review_status
    report.moderator_note = request.moderator_note
    report.reviewed_by = user.get("sub")
    report.reviewed_at = datetime.now(timezone.utc)
    db.commit()

    if request.review_status == "approved" and not was_approved:
        record_report(db, report.target_type, report.target_value, user_id=report.user_id)

    return {"id": report.id, "review_status": report.review_status}
