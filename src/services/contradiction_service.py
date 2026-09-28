from typing import Any, Dict, List, Optional
from datetime import date, datetime
import pandas as pd

class ContradictionService:
    def detect(self, claim_data: Dict[str, Any], extracted_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return detect_contradictions(claim_data, extracted_data)

_contradiction_service = ContradictionService()

def get_contradiction_service() -> ContradictionService:
    return _contradiction_service


def detect_contradictions(claim_data: Dict[str, Any], extracted_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Detect logical contradictions in claim data and OCR extracted data."""
    contradictions = []
    contradiction_type = "none"
    penalty = 0.0
    has_hard = False
    
    extracted = extracted_data or {}
    
    c_sub = claim_data.get("claim_submission_date") or claim_data.get("claim_date")
    p_date = claim_data.get("purchase_date")
    f_date = claim_data.get("fault_occurrence_date") or claim_data.get("fault_date")
    
    if c_sub and p_date:
        try:
            claim_date = pd.to_datetime(c_sub).date()
            purchase = pd.to_datetime(p_date).date()
            if claim_date < purchase:
                contradictions.append({"code": "claim_before_purchase", "description": "Claim submitted before purchase date"})
                contradiction_type = "claim_before_purchase"
                has_hard = True
                penalty += 0.40
        except Exception:
            pass

    if f_date and p_date:
        try:
            fault = pd.to_datetime(f_date).date()
            purchase = pd.to_datetime(p_date).date()
            if fault < purchase:
                contradictions.append({"code": "fault_before_purchase", "description": "Fault occurred before product purchase date"})
                contradiction_type = "fault_before_purchase"
                has_hard = True
                penalty += 0.40
        except Exception:
            pass
            
    if f_date and c_sub:
        try:
            fault = pd.to_datetime(f_date).date()
            claim_date = pd.to_datetime(c_sub).date()
            if fault > claim_date:
                contradictions.append({"code": "fault_after_claim", "description": "Fault date occurs after claim submission date"})
                contradiction_type = "fault_after_claim"
                has_hard = True
                penalty += 0.35
        except Exception:
            pass
            
    r_date = claim_data.get("last_repair_date") or claim_data.get("repair_date")
    if r_date and p_date:
        try:
            repair = pd.to_datetime(r_date).date()
            purchase = pd.to_datetime(p_date).date()
            if repair < purchase:
                contradictions.append({"code": "repair_before_purchase", "description": "Prior repair recorded before product purchase date"})
                contradiction_type = "repair_before_purchase"
                has_hard = True
                penalty += 0.35
        except Exception:
            pass

    if extracted:
        if p_date and extracted.get("purchase_date"):
            try:
                p1 = pd.to_datetime(p_date).date()
                p2 = pd.to_datetime(extracted["purchase_date"]).date()
                diff_days = abs((p1 - p2).days)
                if diff_days > 7:
                    contradictions.append({"code": "purchase_date_mismatch", "description": f"Purchase date mismatch ({diff_days} days difference)"})
                    penalty += 0.20
            except Exception:
                pass
                
        price1 = claim_data.get("purchase_price")
        price2 = extracted.get("purchase_price")
        if price1 is not None and price2 is not None:
            try:
                if abs(float(price1) - float(price2)) > 50.0:
                    contradictions.append({"code": "price_mismatch", "description": "Purchase price discrepancy between claim and receipt"})
                    penalty += 0.15
            except Exception:
                pass
                
        sn1 = claim_data.get("serial_number")
        sn2 = extracted.get("serial_number")
        if sn1 and sn2 and str(sn1).strip().upper() != str(sn2).strip().upper():
            contradictions.append({"code": "ocr_serial_mismatch", "description": "Serial number mismatch against document"})
            has_hard = True
            penalty += 0.30

        m1 = claim_data.get("product_model") or claim_data.get("product_name") or claim_data.get("model_number")
        m2 = extracted.get("product_model") or extracted.get("product_name") or extracted.get("model_number")
        if m1 and m2 and str(m1).strip().lower() != str(m2).strip().lower():
            contradictions.append({"code": "ocr_model_mismatch", "description": "Product model mismatch against document"})
            has_hard = True
            penalty += 0.35

    return {
        "has_contradiction": len(contradictions) > 0,
        "has_hard_contradiction": has_hard,
        "contradiction_type": contradiction_type,
        "confidence_penalty": min(1.0, round(penalty, 2)),
        "contradictions": contradictions,
    }