"""Prep Assist Service - Pre-submission Claim Readiness Check"""

from typing import Any, Dict, List, Optional

from database.models import Claim, Document
from src.services.missing_doc_service import check_missing_documents
from src.services.contradiction_service import detect_contradictions
from src.services.duplicate_service import check_duplicate_claim
from src.services.serial_service import verify_serial_number
from src.core.config import settings


def analyze_claim_readiness(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze claim readiness before submission."""
    
    issues = []
    warnings = []
    suggestions = []
    
    doc_check = check_missing_documents(claim_data)
    if doc_check["missing_count"] > 0:
        for doc in doc_check["missing"]:
            if doc in ["receipt", "warranty_card", "fault_evidence"]:
                issues.append(f"Missing mandatory document: {doc.replace('_', ' ').title()}")
            else:
                warnings.append(f"Missing supporting document: {doc.replace('_', ' ').title()}")
    
    contra_check = detect_contradictions(claim_data)
    if contra_check["has_contradiction"]:
        issues.append(f"Data contradiction detected: {contra_check['contradiction_type']}")
    
    dup_check = check_duplicate_claim(claim_data)
    if dup_check["is_duplicate"]:
        issues.append("Potential duplicate claim detected")
    
    serial_check = verify_serial_number(claim_data)
    if serial_check["status"] == "mismatch":
        issues.append("Serial number mismatch detected")
    elif serial_check["status"] == "missing_evidence":
        warnings.append("Serial number evidence missing")
    
    remaining_days = claim_data.get("remaining_warranty_days")
    if remaining_days is not None:
        if remaining_days < 0:
            issues.append(f"Warranty expired {abs(remaining_days)} days ago")
        elif remaining_days <= 15:
            warnings.append(f"Warranty expires in {remaining_days} days (within grace period)")

    reporting_days = claim_data.get("claim_reporting_days")
    if reporting_days is not None:
        if reporting_days > 30:
            issues.append(f"Claim reported {reporting_days} days after fault (deadline: 30 days)")
        elif reporting_days >= 25:
            warnings.append(f"Close to reporting deadline ({reporting_days}/30 days)")

    proof = claim_data.get("proof_of_purchase")
    if proof == "no":
        issues.append("No proof of purchase provided")
    elif proof == "uncertain":
        warnings.append("Proof of purchase status uncertain")

    missing_items: List[str] = []
    if not claim_data.get("warranty_id"):
        missing_items.append("warranty_id")
    if not claim_data.get("fault_type"):
        missing_items.append("fault_type")
    if not (claim_data.get("description") or claim_data.get("fault_description")):
        missing_items.append("description")
    for doc in doc_check["missing_mandatory_docs"]:
        missing_items.append(doc)
    if missing_items:
        issues.append(f"Incomplete claim payload: missing {', '.join(missing_items)}")

    score = max(0, min(100, 100 - (len(issues) * 25) - (len(warnings) * 10)))
    return {
        "is_ready": not issues,
        "readiness_score": score,
        "issues": issues,
        "blockers": list(issues),
        "warnings": warnings,
        "suggestions": suggestions,
        "missing_items": missing_items,
        "missing_documents": _get_missing_docs(claim_data),
        "document_check": doc_check,
    }


def assess_claim_readiness(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess claim readiness score and readiness status."""
    res = analyze_claim_readiness(claim_data)
    res["readiness_score"] = max(0, min(100, res.get("readiness_score", 85)))
    return res



def _get_missing_docs(claim_data: Dict[str, Any]) -> List[str]:
    doc_check = check_missing_documents(claim_data)
    return [doc.replace("_", " ").title() for doc in doc_check["missing"]]