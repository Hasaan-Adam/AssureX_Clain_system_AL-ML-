"""Serial Service - Serial Number Verification & OCR Corroboration"""

from typing import Any, Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from database.models import Product, Claim


def calculate_similarity(serial1: Optional[str], serial2: Optional[str]) -> float:
    """Calculate SequenceMatcher similarity ratio between two serial numbers."""
    if not serial1 or not serial2:
        return 0.0
    return SequenceMatcher(None, serial1.strip().upper(), serial2.strip().upper()).ratio()


def validate_serial_format(serial: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Validate serial format (min length >= 3, non-empty)."""
    if not serial or not str(serial).strip():
        return False, "Serial number is required."
    clean = str(serial).strip()
    if len(clean) < 3:
        return False, "Serial number is too short (min 3 characters)."
    return True, None


def compare_serials(registered_serial: Optional[str], ocr_serial: Optional[str], threshold: float = 0.85) -> Dict[str, Any]:
    """Compare registered serial against OCR extracted serial."""
    if not ocr_serial or str(ocr_serial).strip() in ("", "N/A", "None", "null"):
        return {
            "status": "missing_evidence",
            "match": False,
            "similarity": 0.0,
            "message": "Missing OCR serial evidence",
        }
    if not registered_serial:
        return {
            "status": "missing_evidence",
            "match": False,
            "similarity": 0.0,
            "message": "Missing registered serial",
        }
    
    sim = calculate_similarity(registered_serial, ocr_serial)
    if sim == 1.0:
        return {"status": "match", "match": True, "similarity": 1.0, "message": "Exact serial match"}
    elif sim >= threshold:
        return {"status": "fuzzy_match", "match": True, "similarity": sim, "message": f"Fuzzy serial match ({sim:.2f})"}
    else:
        return {"status": "mismatch", "match": False, "similarity": sim, "message": f"Serial mismatch ({sim:.2f})"}


def verify_serial_number(
    serial_or_claim: Any,
    expected_serial: Optional[str] = None,
    prefix_expected: Optional[str] = None,
    threshold: float = 0.85,
) -> Dict[str, Any]:
    """Verify serial number between provided & expected, or from claim data dictionary."""
    if isinstance(serial_or_claim, dict):
        claim_data = serial_or_claim
        serial = str(claim_data.get("serial_number", "")).strip().upper()
        if not serial:
            return {"status": "missing_evidence", "is_valid": False, "similarity": 0.0, "message": "Serial number not provided"}
        
        serial_status = claim_data.get("serial_status", "match")
        if serial_status == "mismatch":
            return {"status": "mismatch", "is_valid": False, "similarity": 0.0, "message": "Serial mismatch", "provided": serial}
        elif serial_status == "missing_evidence":
            return {"status": "missing_evidence", "is_valid": False, "similarity": 0.0, "message": "Missing serial evidence", "provided": serial}
        else:
            return {"status": "match", "is_valid": True, "similarity": 1.0, "message": "Serial matches", "provided": serial}
    
    # Otherwise serial_or_claim is serial1 string, expected_serial is serial2
    s1 = str(serial_or_claim).strip().upper() if serial_or_claim else ""
    s2 = str(expected_serial).strip().upper() if expected_serial else ""
    
    if not s1 or not s2:
        return {"status": "missing_evidence", "is_valid": False, "similarity": 0.0, "prefix_valid": True}
    
    sim = calculate_similarity(s1, s2)
    prefix_valid = True
    if prefix_expected:
        prefix_valid = s1.startswith(prefix_expected.upper())
        
    if sim == 1.0:
        return {"status": "match", "is_valid": True, "similarity": 1.0, "prefix_valid": prefix_valid}
    elif sim >= threshold:
        return {"status": "fuzzy_match", "is_valid": True, "similarity": sim, "prefix_valid": prefix_valid}
    else:
        return {"status": "mismatch", "is_valid": False, "similarity": sim, "prefix_valid": prefix_valid}


def verify_claim_serial(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Verify serial based on claim dictionary attributes."""
    if claim_data.get("serial_evidence_available") == "no":
        return {"status": "missing_evidence", "is_valid": False, "similarity": 0.0}
    if claim_data.get("serial_status") == "mismatch":
        return {"status": "mismatch", "is_valid": False, "similarity": 0.0}
    if claim_data.get("serial_status") == "missing_evidence":
        return {"status": "missing_evidence", "is_valid": False, "similarity": 0.0}
    return {"status": "match", "is_valid": True, "similarity": 1.0}


def verify_serial_against_db(db: Session, serial: str, claimant_id: int) -> Dict[str, Any]:
    """Verify serial against registered products in DB."""
    product = db.query(Product).filter(
        Product.serial_number == serial,
        Product.owner_id == claimant_id,
    ).first()
    
    if not product:
        other = db.query(Product).filter(Product.serial_number == serial).first()
        if other:
            return {"status": "mismatch", "message": "Serial registered to different user"}
        return {"status": "not_found", "message": "Serial not found in registry"}
    
    return {"status": "match", "message": "Serial verified", "product_id": product.id}


def fuzzy_serial_match(serial1: str, serial2: str, threshold: float = 0.85) -> bool:
    """Fuzzy match serial numbers."""
    return SequenceMatcher(None, serial1.upper(), serial2.upper()).ratio() >= threshold


class SerialService:
    def verify(self, s1: str, s2: str, threshold: float = 0.85) -> Dict[str, Any]:
        return verify_serial_number(s1, s2, threshold=threshold)

    def validate_format(self, serial: Optional[str]) -> Tuple[bool, Optional[str]]:
        return validate_serial_format(serial)

    def compare(self, s1: Optional[str], s2: Optional[str]) -> Dict[str, Any]:
        return compare_serials(s1, s2)

    def verify_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        return verify_claim_serial(claim_data)


_serial_service = SerialService()

def get_serial_service() -> SerialService:
    return _serial_service