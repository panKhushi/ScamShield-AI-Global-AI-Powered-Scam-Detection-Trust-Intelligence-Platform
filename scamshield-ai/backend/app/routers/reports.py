from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.db_models import Report
from app.models import ReportRequest, ReportResponse
from app.services.auth_service import get_current_user
from app.services.audit_log import log_report_submission

router = APIRouter()


@router.post("/report", response_model=ReportResponse)
def submit_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    report = Report(
        user_id=user.get("sub"),
        target_value=request.target_value,
        target_type=request.target_type,
        category=request.category,
        description=request.description,
    )
    db.add(report)
    db.commit()
    log_report_submission(user.get("sub"), request.target_value, request.category)
    db.refresh(report)

    return ReportResponse(
        id=report.id,
        target_value=report.target_value,
        category=report.category,
        description=report.description,
        created_at=report.created_at.isoformat(),
    )


@router.get("/reports/{target_value}")
def get_reports_for_target(target_value: str, db: Session = Depends(get_db)):
    reports = (
        db.query(Report)
        .filter(Report.target_value == target_value)
        .order_by(Report.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "category": r.category,
            "description": r.description,
            "created_at": r.created_at,
        }
        for r in reports
    ]