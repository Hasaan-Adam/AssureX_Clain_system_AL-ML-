"""
AssureX Claim Engine - Reports & Exports API Router
Provides PDF claim downloads, CSV datasets, and formatted Excel reports.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from database.session import get_db
from src.dependencies import current_user_role, get_current_user, require_reviewer
from src.models.user import User
from src.services import claim_service, export_service, report_service

router = APIRouter(prefix="/reports", tags=["Reports & Exports"])


@router.get("/claim/{claim_id}/pdf")
def download_claim_report_pdf(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate and download a professional PDF adjudication report for a claim."""
    claim = claim_service.get_claim_by_id(
        db=db,
        claim_id=claim_id,
        user_id=current_user.id,
        role=current_user_role(current_user),
    )
    pdf_bytes = report_service.generate_claim_pdf_report(db, claim.id)
    filename = f"claim_{claim.claim_id}_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/claim/{claim_id}/json")
def get_claim_report_payload(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Machine-readable adjudication payload (model agreement, rules, human decision)."""
    claim = claim_service.get_claim_by_id(
        db=db,
        claim_id=claim_id,
        user_id=current_user.id,
        role=current_user_role(current_user),
    )
    return report_service.build_claim_report(db, claim.id)


@router.get("/export/claims/csv")
def export_claims_csv(
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(require_reviewer),
    db: Session = Depends(get_db),
):
    """Download claims dataset in CSV format."""
    csv_str = export_service.export_claims_csv(db, filters={"status": status})
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=claims_export.csv"},
    )


@router.get("/export/claims/excel")
def export_claims_excel(
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(require_reviewer),
    db: Session = Depends(get_db),
):
    """Download claims dataset in Excel (.xlsx) format."""
    excel_bytes = export_service.export_claims_excel(db, filters={"status": status})
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=claims_export.xlsx"},
    )


@router.get("/export/reviews/csv")
def export_reviews_csv(
    current_user: User = Depends(require_reviewer),
    db: Session = Depends(get_db),
):
    """Download manual review logs in CSV format."""
    csv_str = export_service.export_reviews_csv(db)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=reviews_export.csv"},
    )
