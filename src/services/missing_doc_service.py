"""
Missing Document Service - document completeness check.

Vocabulary follows the SRS data dictionary (documentation/project_report/
09_data_dictionary.md) and `database.models.DocumentType`:

    receipt, warranty_card, product_image, serial_evidence, fault_evidence,
    repair_report

Required documents depend on the product category, and `repair_report`
becomes mandatory as soon as the device has repair history (SRS Rule 5).
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

#: Mandatory for every category.
MANDATORY_DOCS: tuple = ("receipt", "fault_evidence")

#: Optional evidence that improves confidence.
OPTIONAL_DOCS: tuple = ("warranty_card", "product_image", "serial_evidence", "repair_report")

ALL_DOCS: tuple = MANDATORY_DOCS + OPTIONAL_DOCS

#: Extra documents a category always needs on top of the mandatory bundle.
CATEGORY_REQUIRED_DOCS: Dict[str, tuple] = {
    "electronics": ("serial_evidence",),
    "laptop": ("serial_evidence",),
    "mobile": ("serial_evidence",),
    "tablet": ("serial_evidence",),
    "home_appliance": ("serial_evidence",),
    "automotive": ("purchase_invoice", "serial_evidence"),
    "furniture": ("purchase_invoice",),
    "other": (),
}

#: Legacy / UI vocabulary mapped onto the canonical names.
DOC_ALIASES: Dict[str, str] = {
    "purchase_invoice": "receipt",
    "purchase_receipt": "receipt",
    "invoice": "receipt",
    "receipt_available": "receipt",
    "warranty_card_photo": "warranty_card",
    "warranty_certificate": "warranty_card",
    "serial_number_photo": "serial_evidence",
    "serial_number": "serial_evidence",
    "serial_photo": "serial_evidence",
    "damage_photo": "fault_evidence",
    "damage_evidence": "fault_evidence",
    "fault_photo": "fault_evidence",
    "product_photo": "product_image",
    "warranty_card_photo_available": "warranty_card",
}

_TRUTHY = {"yes", "true", "1", "y", "available", "present"}


def _canonical(name: Any) -> str:
    key = str(name or "").strip().lower()
    return DOC_ALIASES.get(key, key)


def _is_available(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    return str(value or "").strip().lower() in _TRUTHY


def _available_from_claim(claim_data: Dict[str, Any]) -> List[str]:
    """Derive the available document set from `<doc>_available` flags."""
    available: List[str] = []
    for doc in ALL_DOCS:
        if _is_available(claim_data.get(f"{doc}_available")):
            available.append(doc)
    # Documents may also be supplied as a real list of document types.
    for key in ("available_doc_types", "documents", "document_types"):
        for entry in claim_data.get(key) or []:
            name = _canonical(getattr(entry, "value", entry))
            if name and name not in available:
                available.append(name)
    return available


def _required_for(category: Optional[str], repair_history_count: int, repair_report_available: bool) -> List[str]:
    key = str(category or "other").strip().lower().replace(" ", "_")
    required = list(MANDATORY_DOCS)
    for extra in CATEGORY_REQUIRED_DOCS.get(key, CATEGORY_REQUIRED_DOCS["other"]):
        if extra not in required:
            required.append(extra)
    if repair_history_count > 0 and not repair_report_available:
        required.append("repair_report")
    return required


def check_missing_documents(
    claim_data: Optional[Dict[str, Any]] = None,
    *,
    claim: Optional[Dict[str, Any]] = None,
    category: Optional[str] = None,
    available_doc_types: Optional[Iterable[Any]] = None,
    repair_history_count: Optional[int] = None,
    repair_report_available: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Evaluate document completeness for a claim.

    Accepts either a full claim dictionary (``check_missing_documents(claim)``
    / ``check_missing_documents(claim=claim)``) or an explicit
    ``category`` + ``available_doc_types`` pair.

    Note: ``missing_count`` counts the *required* documents that are absent,
    which is what claim readiness depends on. ``missing_all_count`` covers
    every tracked document flag (the ML feature `missing_document_count`
    uses that wider definition).
    """
    data: Dict[str, Any] = dict(claim or claim_data or {})

    if available_doc_types is not None:
        available = []
        for entry in available_doc_types:
            name = _canonical(getattr(entry, "value", entry))
            if name and name not in available:
                available.append(name)
    else:
        available = _available_from_claim(data)

    category = category or data.get("product_category") or data.get("category")
    if repair_history_count is None:
        repair_history_count = data.get("repair_history_count") or 0
    repair_history_count = int(repair_history_count or 0)
    if repair_report_available is None:
        repair_report_available = data.get("repair_report_available")
    repair_report_ok = _is_available(repair_report_available) or "repair_report" in available

    required = _required_for(category, repair_history_count, repair_report_ok)
    available_set = set(available)
    missing_required = [doc for doc in required if doc not in available_set]
    missing_optional = [doc for doc in OPTIONAL_DOCS if doc not in available_set and doc not in required]
    missing_all = [doc for doc in ALL_DOCS if doc not in available_set]

    is_complete = not missing_required
    score = round(len(set(required) & available_set) / len(required), 4) if required else 1.0

    return {
        "is_complete": is_complete,
        "action_needed": "PROCEED" if is_complete else "REQUEST_DOCUMENTS",
        "required_documents": list(required),
        "available_documents": [doc for doc in ALL_DOCS if doc in available_set],
        "missing_documents": missing_required,
        "missing_mandatory_docs": missing_required,
        "missing_optional_docs": missing_optional,
        "missing": missing_required + missing_optional,
        "missing_count": len(missing_required),
        "missing_all_count": len(missing_all),
        "completeness_score": score,
        "mandatory_docs_complete": is_complete,
        "repair_report_required": repair_history_count > 0,
    }
