"""Duplicate Service - Duplicate Claim & Document Detection"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from database.models import Claim, Document


def check_duplicate_claim(
    db_or_claim: Any,
    claim_data: Optional[Dict[str, Any]] = None,
    warranty_id: Optional[int] = None,
    fault_type: Optional[str] = None,
    claim_history: Optional[List[Dict[str, Any]]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Check for duplicate claims across DB records or in-memory historical claims.
    """
    # 1. In-memory history check
    if claim_history is not None:
        target_claim = db_or_claim if isinstance(db_or_claim, dict) else (claim_data or {})
        matching = []
        target_user = target_claim.get("user_id") or target_claim.get("claimant_id")
        target_serial = target_claim.get("serial_number")
        target_fault = target_claim.get("fault_type")
        
        for old in claim_history:
            old_user = old.get("user_id") or old.get("claimant_id")
            old_serial = old.get("serial_number")
            old_fault = old.get("fault_type")
            if target_user == old_user and target_serial == old_serial and target_fault == old_fault:
                matching.append(old.get("claim_id") or old.get("claim_number") or "CLM-PREV")
                
        if matching:
            return {
                "is_duplicate": True,
                "reason": "Duplicate claim detected matching user, serial number, and fault type in history.",
                "matching_claim_numbers": matching,
                "duplicate_count": len(matching),
            }
        return {"is_duplicate": False, "matching_claim_numbers": [], "duplicate_count": 0}

    # 2. Direct DB session check by warranty_id and fault_type
    if isinstance(db_or_claim, Session):
        db = db_or_claim
        wid = warranty_id or (claim_data.get("warranty_id") if claim_data else None)
        ft = fault_type or (claim_data.get("fault_type") if claim_data else None)
        
        query = db.query(Claim)
        if wid:
            query = query.filter(Claim.warranty_id == wid)
        if ft:
            query = query.filter(Claim.fault_type.ilike(f"%{ft}%"))
            
        matches = query.all()
        if matches:
            claim_nums = [c.claim_id for c in matches]
            return {
                "is_duplicate": True,
                "reason": f"Found {len(matches)} previous claims on warranty #{wid} for '{ft}'.",
                "matching_claim_numbers": claim_nums,
                "duplicate_count": len(matches),
            }
        return {"is_duplicate": False, "matching_claim_numbers": [], "duplicate_count": 0}

    # 3. Dict-based check
    claim_dict = db_or_claim if isinstance(db_or_claim, dict) else (claim_data or {})
    if claim_dict.get("is_duplicate") in ("yes", True):
        return {"is_duplicate": True, "reason": "Claim flagged as duplicate.", "matching_claim_numbers": [], "duplicate_count": 1}

    return {"is_duplicate": False, "matching_claim_numbers": [], "duplicate_count": 0}


def check_duplicate_document(
    db_or_hash: Any,
    file_hash: Optional[str] = None,
    existing_hashes: Optional[List[str]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Check if a document SHA-256 hash has already been used in previous claims.
    """
    # 1. In-memory list check
    target_hash = db_or_hash if isinstance(db_or_hash, str) else file_hash
    if existing_hashes is not None:
        if target_hash in existing_hashes:
            return {
                "is_duplicate": True,
                "duplicate_type": "DOCUMENT_HASH_MATCH",
                "reason": f"Document hash {target_hash[:12]}... matches existing document in submission history.",
                "file_hash": target_hash,
                "match_count": 1,
            }
        return {"is_duplicate": False, "duplicate_type": None, "match_count": 0}

    # 2. Database query check
    if isinstance(db_or_hash, Session):
        db = db_or_hash
        target = file_hash or kwargs.get("hash")
        if target:
            matches = db.query(Document).filter(Document.file_hash == target).all()
            if matches:
                first = matches[0]
                return {
                    "is_duplicate": True,
                    "duplicate_type": "DOCUMENT_HASH_MATCH",
                    "reason": f"Document hash {target[:12]}... was already uploaded "
                              f"({len(matches)} matching document(s) found).",
                    "existing_document_id": first.id,
                    "existing_claim_id": first.claim_id,
                    "matching_document_ids": [doc.id for doc in matches],
                    "match_count": len(matches),
                    "file_hash": target,
                }
        return {"is_duplicate": False, "duplicate_type": None, "match_count": 0}

    return {"is_duplicate": False, "duplicate_type": None, "match_count": 0}