"""AI Summary Service - Claim Summarization"""

from typing import Any, Dict, List, Optional


def summarize_claim(claim_data: Dict[str, Any], max_length: int = 200) -> str:
    """Generate a concise claim summary."""
    parts = []
    
    product = claim_data.get("product_name", "Product")
    brand = claim_data.get("brand", "")
    if brand:
        product = f"{brand} {product}"
    parts.append(f"Product: {product}")
    
    remaining = claim_data.get("remaining_warranty_days", 0)
    if remaining >= 0:
        parts.append(f"Warranty: {remaining} days remaining")
    else:
        parts.append(f"Warranty: Expired {abs(remaining)} days ago")
    
    fault = claim_data.get("fault_type", "Unknown fault")
    fault_desc = claim_data.get("fault_description", "")
    if fault_desc:
        parts.append(f"Fault: {fault} - {fault_desc[:100]}")
    else:
        parts.append(f"Fault: {fault}")
    
    repair_count = claim_data.get("repair_history_count", 0)
    if repair_count > 0:
        auth = claim_data.get("repair_authorized", "none")
        parts.append(f"Repairs: {repair_count} ({auth})")
    
    missing = claim_data.get("missing_document_count", 0)
    if missing > 0:
        parts.append(f"Missing documents: {missing}")
    
    if claim_data.get("has_contradiction") == "yes":
        parts.append(f"Contradiction: {claim_data.get('contradiction_type', 'unknown')}")
    
    serial = claim_data.get("serial_status", "match")
    if serial != "match":
        parts.append(f"Serial: {serial}")
    
    summary = ". ".join(parts)
    if len(summary) > max_length:
        summary = summary[:max_length-3] + "..."
    
    return summary


def generate_claim_summary(claim_data: Dict[str, Any]) -> str:
    """Alias for summarize_claim."""
    return summarize_claim(claim_data)


def generate_claim_executive_summary(claim_data: Dict[str, Any], final_result: Optional[Dict[str, Any]] = None) -> str:
    """Generate executive summary for claim adjudication report."""
    cid = claim_data.get("claim_id", "CLM-UNKNOWN")
    product = claim_data.get("product_name", "Equipment")
    brand = claim_data.get("brand", "")
    p_name = f"{brand} {product}".strip()
    outcome = final_result.get("final_decision", "Under Review") if final_result else "Evaluated"
    return f"Executive Summary for Claim {cid}: {p_name} analyzed. Adjudication outcome resolved as '{outcome}' based on dynamic ML inference, warranty policy checks, and evidence corroboration."


def generate_claim_narrative(claim_data: Dict[str, Any]) -> str:
    """Generate narrative paragraph of the claim history and submission details."""
    summary = summarize_claim(claim_data, max_length=500)
    return f"Claim narrative: {summary}"