"""Export Service - CSV / Excel exports of claims, reviews and audit logs"""

from __future__ import annotations

import csv
import io
import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from database.models import AuditLog, Claim, Product, Review, User, Warranty

CLAIM_CSV_HEADERS = [
    "Claim Number",
    "Customer Email",
    "Product",
    "Serial Number",
    "Status",
    "Submission Date",
    "Claim Amount",
    "Final Decision",
    "Python Prediction",
    "Teachable Machine Prediction",
    "Models Agree",
    "Fraud Score",
    "Filed By",
    "Filing Channel",
]

REVIEW_CSV_HEADERS = [
    "Review ID",
    "Claim Number",
    "Reviewer",
    "Decision",
    "Comments",
    "Override Reason",
    "Created At",
]

AUDIT_CSV_HEADERS = ["User ID", "Action", "Entity Type", "Entity ID", "Old Values", "New Values", "IP Address", "Created At"]


def _iso(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def _claims_query(db: Session, filters: Optional[Dict[str, Any]] = None):
    query = db.query(Claim)
    filters = filters or {}
    if filters.get("status"):
        query = query.filter(Claim.status.ilike(f"%{filters['status']}%"))
    if filters.get("claimant_id"):
        query = query.filter(Claim.claimant_id == filters["claimant_id"])
    if filters.get("date_from"):
        query = query.filter(Claim.claim_submission_date >= filters["date_from"])
    if filters.get("date_to"):
        query = query.filter(Claim.claim_submission_date <= filters["date_to"])
    return query.order_by(Claim.created_at.desc())


def _claim_rows(db: Session, filters: Optional[Dict[str, Any]] = None) -> List[List[Any]]:
    rows: List[List[Any]] = []
    for claim in _claims_query(db, filters).all():
        product = claim.product
        rows.append(
            [
                claim.claim_id,
                claim.claimant.email if claim.claimant else "",
                product.name if product else "",
                product.serial_number if product else "",
                claim.status,
                _iso(claim.claim_submission_date),
                claim.claim_amount if claim.claim_amount is not None else "",
                claim.final_decision or "",
                claim.python_prediction or "",
                claim.tm_prediction or "",
                "yes" if claim.model_agreement_score is None or claim.model_agreement_score >= 0.5 else "no",
                claim.fraud_score,
                claim.filed_by or "",
                claim.filing_channel or "",
            ]
        )
    return rows


def _to_csv(headers: List[str], rows: List[List[Any]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return output.getvalue()


def _to_xlsx(sheet_title: str, headers: List[str], rows: List[List[Any]]) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_title[:31]
    sheet.append(headers)
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for row in rows:
        sheet.append(row)
    for index, header in enumerate(headers, start=1):
        width = max(len(str(header)) + 2, 12)
        sheet.column_dimensions[sheet.cell(row=1, column=index).column_letter].width = min(width, 40)

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def export_claims_csv(db: Session, filters: Optional[Dict[str, Any]] = None) -> str:
    """Export claims to CSV (reviewer/admin only - enforced by the router)."""
    return _to_csv(CLAIM_CSV_HEADERS, _claim_rows(db, filters))


def export_claims_excel(db: Session, filters: Optional[Dict[str, Any]] = None) -> bytes:
    """Export claims to a real .xlsx workbook."""
    return _to_xlsx("Claims", CLAIM_CSV_HEADERS, _claim_rows(db, filters))


def _review_rows(db: Session) -> List[List[Any]]:
    rows: List[List[Any]] = []
    for review in db.query(Review).order_by(Review.created_at.desc()).all():
        rows.append(
            [
                review.id,
                review.claim.claim_id if review.claim else "",
                review.reviewer.email if review.reviewer else "",
                review.decision,
                review.comments or "",
                review.override_reason or "",
                _iso(review.created_at),
            ]
        )
    return rows


def export_reviews_csv(db: Session) -> str:
    """Export the human review log to CSV."""
    return _to_csv(REVIEW_CSV_HEADERS, _review_rows(db))


def export_reviews_excel(db: Session) -> bytes:
    """Export the human review log to .xlsx."""
    return _to_xlsx("Reviews", REVIEW_CSV_HEADERS, _review_rows(db))


def export_audit_logs_csv(db: Session) -> str:
    """Export the audit trail to CSV."""
    rows = [
        [
            log.user_id or "",
            log.action,
            log.entity_type or "",
            log.entity_id or "",
            _iso(log.old_values),
            _iso(log.new_values),
            log.ip_address or "",
            _iso(log.created_at),
        ]
        for log in db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
    ]
    return _to_csv(AUDIT_CSV_HEADERS, rows)
