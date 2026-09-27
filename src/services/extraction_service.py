"""
AssureX Claim Engine - Structured Entity Extraction Service
Parses OCR textual output to extract receipt dates, retailer names, prices, model numbers, and serials.
"""

from datetime import datetime
import re
from typing import Any, Dict, List, Optional


# Regex Patterns for entity extraction
DATE_PATTERNS = [
    r"\b(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\b",           # 2024-05-13, 2024/05/13, 2024.05.13
    r"\b(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})\b",           # 13-05-2024, 05/13/2024, 13.05.2024
    r"\b([A-Za-z]{3,9}\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})\b",  # May 13, 2024 or May 13th 2024
    r"\b(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]{3,9},?\s+\d{4})\b",  # 13 May 2024 or 13th May, 2024
    r"\b(\d{1,2}-[A-Za-z]{3,9}-\d{4})\b",            # 13-May-2024
]

PRICE_PATTERNS = [
    r"(?:Total|Amount|Price|Paid|Grand\s+Total|Subtotal|Cost|Net\s+Amount)[\s:]*(?:\$|€|£|Rs\.?|USD|PKR|CAD|AUD)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)",
    r"(?:\$|€|£|Rs\.?|USD|PKR)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)",
    r"\b([0-9]{1,3}(?:,[0-9]{3})+\.[0-9]{2})\b",
    r"\b([0-9]+\.[0-9]{2})\b",
]

SERIAL_PATTERNS = [
    r"(?:Serial\s+(?:Number|No\.?|#)|S/N|SN|Serial)[\s:#\-]+([A-Za-z0-9\-_]{4,35})",
    r"\b(SN-[A-Za-z0-9\-]{4,25})\b",
    r"\b(SER-[A-Za-z0-9\-]{4,25})\b",
    r"\b([A-Z]{2,4}-[A-Z0-9]{3,6}-[0-9]{4,10})\b",
]

MODEL_PATTERNS = [
    r"(?:Model\s+(?:Number|No\.?|#)|Item\s+(?:Number|No\.?|#)|Product\s+(?:Code|No\.?|#)|Model|Item)[\s:#\-]+([A-Za-z0-9\-_\s]{3,30})",
    r"\b([A-Z0-9]{2,6}-[A-Z0-9]{2,6})\b",
]

RETAILER_KEYWORDS = [
    "Best Buy", "Walmart", "Target", "Amazon", "Apple Store",
    "Samsung Store", "Samsung Official Store", "City Mart Stores",
    "Metro Electronics", "Costco", "Home Depot", "Micro Center",
    "MediaMarkt", "Currys", "B&H Photo", "Newegg", "Sony Store",
    "Dell Technologies", "HP Store", "LG Electronics", "IKEA",
]

INVOICE_PATTERNS = [
    r"\b(INV-[A-Za-z0-9\-]{3,25})\b",
    r"\b(REC-[A-Za-z0-9\-]{3,25})\b",
    r"\b(ORD-[A-Za-z0-9\-]{3,25})\b",
    r"\b(TXN-[A-Za-z0-9\-]{3,25})\b",
    r"\b(BILL-[A-Za-z0-9\-]{3,25})\b",
    r"(?:Invoice\s+(?:Number|No\.?|#|ID)|Tax\s+Invoice\s+(?:No\.?|#|ID|Number)?|Invoice|INV\s*(?:#|No\.?|ID)?|Receipt\s+(?:Number|No\.?|#|ID)|Receipt|Bill\s+(?:Number|No\.?|#|ID)|Order\s+(?:ID|#|Number)|Transaction\s+(?:ID|#|Number)|Ref\s+(?:No\.?|#|ID)|Reference\s+(?:No\.?|#|ID))[\s:#\-]+([A-Za-z0-9\-_ /]{3,30})",
    r"\b(INV\d{4,12})\b",
    r"\b(REC\d{4,12})\b",
    r"\b(#\d{4,12})\b",
]

EXCLUDED_INVOICE_WORDS = {
    "TOTAL", "PRICE", "AMOUNT", "DATE", "CASH", "CARD", "ITEMS", "STORE", "RECEIPT",
    "INVOICE", "NUMBER", "PRODUCT", "CUSTOMER", "DEVICE", "BEST", "BUY", "WALMART", "APPLE",
    "TAX", "SUBTOTAL", "PAID", "VISA", "MASTERCARD", "DETAILS", "OFFICIAL"
}


def extract_invoice_number(text: str) -> Optional[str]:
    """
    Search for invoice, receipt, or order numbers across:
    1. First priority: Formatted standard invoice tokens (e.g. 'INV-2026-98102', 'REC-88391', 'ORD-2024-001')
    2. Hash-prefixed IDs (e.g. '#981023', '#INV4092')
    3. Single-line labeled key-value (e.g. 'Invoice Number: 981024', 'Tax Invoice No: TX-8819')
    4. Multi-line stacked layouts (e.g. 'INVOICE NUMBER' on line N, value on line N+1)
    5. Standalone numeric/alphanumeric order codes near receipt header
    """
    if not text:
        return None

    # 1. First priority: Standard formatted prefix tokens (INV-XXXX, REC-XXXX, ORD-XXXX, TXN-XXXX, BILL-XXXX)
    formatted_m = re.search(r"\b((?:INV|REC|ORD|TXN|BILL|DOC|VCH|REF)-[A-Za-z0-9\-]{3,25})\b", text, re.IGNORECASE)
    if formatted_m:
        token = formatted_m.group(1).upper()
        if token.upper() not in EXCLUDED_INVOICE_WORDS:
            return token

    # 2. Hash prefixed e.g. #981023
    hash_m = re.search(r"\b#([A-Za-z0-9\-]{4,20})\b", text)
    if hash_m:
        val = f"#{hash_m.group(1)}"
        if val.upper() not in EXCLUDED_INVOICE_WORDS:
            return val

    # 3. Single-line labeled patterns (e.g. 'Invoice No: 10492', 'Invoice #: SM-991')
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        m = re.search(
            r"(?:Invoice\s*(?:Number|No\.?|#|ID)?|Tax\s+Invoice\s*(?:No\.?|#|ID|Number)?|Receipt\s*(?:Number|No\.?|#|ID)?|Bill\s*(?:Number|No\.?|#|ID)?|Order\s*(?:ID|#|Number)?|Transaction\s*(?:ID|#|Number)?|Ref\s*(?:No\.?|#|ID)?|Doc\s*(?:No\.?|#|ID)?|Voucher\s*(?:No\.?|#|ID)?)\s*[:#\-]\s*([A-Za-z0-9\-_ /]{3,30})",
            line,
            re.IGNORECASE,
        )
        if m:
            val = m.group(1).strip()
            val = re.sub(r"^[#:\-\s]+|[#:\-\s]+$", "", val)
            val_no_space = re.sub(r"\s+", "", val)
            if len(val_no_space) >= 3 and val_no_space.upper() not in EXCLUDED_INVOICE_WORDS:
                return val

    # 4. Multi-line stacked search (Label on Line N, Value on Line N+1 or Line N+2)
    label_pattern = re.compile(
        r"^(?:Invoice\s*(?:Number|No\.?|#|ID)?|Tax\s+Invoice\s*(?:No\.?|#|ID|Number)?|INV\s*(?:#|No\.?|ID)?|Receipt\s*(?:Number|No\.?|#|ID)?|Bill\s*(?:Number|No\.?|#|ID)?|Order\s*(?:ID|#|Number)?|Transaction\s*(?:ID|#|Number)?|Ref\s*(?:No\.?|#|ID)?|Document\s*(?:No\.?|#|ID)?|Doc\s*(?:No\.?|#|ID)?|Voucher\s*(?:No\.?|#|ID)?)$",
        re.IGNORECASE,
    )
    for i, line in enumerate(lines):
        if label_pattern.match(line) or re.search(r"\b(?:INVOICE|RECEIPT|BILL|ORDER)\s*(?:#|NO\.?|ID)?$", line, re.IGNORECASE):
            for offset in (1, 2):
                if i + offset < len(lines):
                    candidate = lines[i + offset].strip()
                    candidate = re.sub(r"^[#:\-\s]+|[#:\-\s]+$", "", candidate)
                    candidate_clean = re.sub(r"\s+", "", candidate)
                    if (
                        len(candidate_clean) >= 3
                        and candidate_clean.upper() not in EXCLUDED_INVOICE_WORDS
                        and not re.search(r"^(?:Date|Total|Price|Amount|Paid|Subtotal|Cash|Card|Store|Tax|USD|\$)", candidate, re.IGNORECASE)
                        and not re.search(r"^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}$", candidate)
                        and not re.search(r"^\d{1,2}[-/.]\d{1,2}[-/.]\d{4}$", candidate)
                    ):
                        return candidate

    # 5. Generic invoice regex list
    for pattern in INVOICE_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            val = match.group(1).strip()
            val = re.sub(r"^[#:\-\s]+|[#:\-\s]+$", "", val)
            val_no_space = re.sub(r"\s+", "", val)
            if len(val_no_space) >= 3 and val_no_space.upper() not in EXCLUDED_INVOICE_WORDS:
                return val

    # 6. Fallback: Search for standalone alphanumeric codes in top 12 lines if invoice keyword is present
    has_invoice_word = re.search(r"\b(?:invoice|receipt|tax invoice|bill to|order)\b", text, re.IGNORECASE)
    if has_invoice_word:
        for line in lines[:12]:
            candidate_m = re.search(r"\b([A-Z0-9]{4,16})\b", line)
            if candidate_m:
                cand = candidate_m.group(1).strip()
                if (
                    cand.upper() not in EXCLUDED_INVOICE_WORDS
                    and not cand.isdigit()
                    and len(cand) >= 4
                    and not re.search(r"^(?:2024|2025|2026|2027)", cand)
                ):
                    return cand

    return None


def extract_date(text: str) -> Optional[str]:
    """Search for purchase or receipt dates and normalize to YYYY-MM-DD if possible."""
    if not text:
        return None

    for pattern in DATE_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            raw_date = match.group(1).strip()
            # Clean ordinal suffixes like 13th -> 13
            clean_date = re.sub(r"(\d+)(?:st|nd|rd|th)", r"\1", raw_date).replace(",", "")
            # Try parsing
            for fmt in (
                "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
                "%m/%d/%Y", "%m-%d-%Y", "%m.%d.%Y",
                "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y",
                "%b %d %Y", "%B %d %Y",
                "%d %b %Y", "%d %B %Y",
                "%d-%b-%Y", "%d-%B-%Y"
            ):
                try:
                    dt = datetime.strptime(clean_date, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            return raw_date
    return None


def extract_price(text: str) -> Optional[float]:
    """Search for total price or amount paid."""
    if not text:
        return None

    # Line by line check prioritized by label
    for line in text.splitlines():
        if re.search(r"(?:Total|Grand\s+Total|Net\s+Amount|Amount\s+Due|Paid|Price|Amount)", line, re.IGNORECASE):
            for pat in PRICE_PATTERNS:
                m = re.search(pat, line, re.IGNORECASE)
                if m:
                    raw_str = m.group(1).replace(",", "").strip()
                    try:
                        val = float(raw_str)
                        if val > 0:
                            return round(val, 2)
                    except ValueError:
                        pass

    for pattern in PRICE_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for m in matches:
            raw_str = m.group(1).replace(",", "").strip()
            try:
                val = float(raw_str)
                if val > 0:
                    return round(val, 2)
            except ValueError:
                continue
    return None


def extract_serial_number(text: str) -> Optional[str]:
    """Search for product serial numbers."""
    if not text:
        return None

    # 1. Line-by-line check with prefix
    for line in text.splitlines():
        m = re.search(r"(?:Serial\s+(?:Number|No\.?|#)|S/N|SN|Serial)[\s:#\-]+([A-Za-z0-9\-_]{4,35})", line, re.IGNORECASE)
        if m:
            ser = m.group(1).strip()
            if len(ser) >= 4 and ser.upper() not in EXCLUDED_INVOICE_WORDS:
                return ser

    # 2. General patterns
    for pattern in SERIAL_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            ser = match.group(1).strip()
            # Avoid matching invoice patterns
            if not ser.startswith("INV-") and not ser.startswith("ORD-") and not ser.startswith("REC-"):
                if len(ser) >= 4 and ser.upper() not in EXCLUDED_INVOICE_WORDS:
                    return ser
    return None


def extract_model_number(text: str) -> Optional[str]:
    """Search for product model numbers."""
    if not text:
        return None

    for line in text.splitlines():
        m = re.search(r"(?:Model\s+(?:Number|No\.?|#)|Item\s+(?:Number|No\.?|#)|Product\s+(?:Code|No\.?|#))[\s:#\-]+([A-Za-z0-9\-_\s]{3,30})", line, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if not val.startswith("INV-") and not val.startswith("REC-") and not val.startswith("SN-") and val.upper() not in EXCLUDED_INVOICE_WORDS:
                return val

    for pattern in MODEL_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            if not val.startswith("INV-") and not val.startswith("REC-") and not val.startswith("ORD-") and not val.startswith("SN-") and val.upper() not in EXCLUDED_INVOICE_WORDS:
                return val
    return None


def extract_retailer(text: str) -> Optional[str]:
    """Search for known retailer or store names."""
    if not text:
        return None

    for retailer in RETAILER_KEYWORDS:
        if re.search(r"\b" + re.escape(retailer) + r"\b", text, re.IGNORECASE):
            return retailer

    # Fallback to first non-empty header line
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        first_line = lines[0]
        if len(first_line) < 40 and not re.search(r"\d{4}", first_line) and not re.search(r"(?:invoice|receipt|total|claim)", first_line, re.IGNORECASE):
            return first_line

    return None


def extract_warranty_duration(text: str) -> Optional[int]:
    """Search for warranty duration in months or years."""
    if not text:
        return None

    patterns = [
        r"(\d+)\s*(?:year|yr)s?\s*(?:limited\s*)?warranty",
        r"warranty[:\s]*(\d+)\s*(?:year|yr)s?",
        r"(\d+)\s*(?:month|mo)s?\s*(?:limited\s*)?warranty",
        r"warranty[:\s]*(\d+)\s*(?:month|mo)s?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = int(match.group(1))
            if "year" in match.group(0).lower() or "yr" in match.group(0).lower():
                return val * 12
            return val
    return None


def extract_entities_from_text(text: str) -> Dict[str, Any]:
    """
    Extract structured fields from OCR text and calculate overall entity confidence.
    """
    if not text:
        return {
            "invoice_number": None,
            "purchase_date": None,
            "purchase_price": None,
            "serial_number": None,
            "model_number": None,
            "retailer": None,
            "warranty_duration": None,
            "entity_count": 0,
            "extraction_confidence": 0.0,
        }

    invoice_val = extract_invoice_number(text)
    date_val = extract_date(text)
    price_val = extract_price(text)
    serial_val = extract_serial_number(text)
    model_val = extract_model_number(text)
    retailer_val = extract_retailer(text)
    warranty_dur = extract_warranty_duration(text)

    found_entities = [e for e in [invoice_val, date_val, price_val, serial_val, model_val, retailer_val, warranty_dur] if e is not None]
    confidence = round(len(found_entities) / 7.0, 2)

    return {
        "invoice_number": invoice_val,
        "purchase_date": date_val,
        "purchase_price": price_val,
        "serial_number": serial_val,
        "model_number": model_val,
        "retailer": retailer_val,
        "warranty_duration": warranty_dur,
        "entity_count": len(found_entities),
        "extraction_confidence": confidence,
    }