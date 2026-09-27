"""Generate 1,500 unique warranty claim records (500 / 500 / 500).

Usage:
    python -m dataset_generator.generate_dataset
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from dataset_generator.claim_templates import (
    CONTRADICTION_TYPES,
    COVERED_FAULTS,
    DAMAGE_TYPES,
    EXCLUDED_FAULTS,
    FAULT_DESCRIPTIONS,
    PRODUCT_CATALOG,
    RETAILERS,
    SERIAL_PREFIXES,
)
from dataset_generator.scenarios import (
    ALL_DOC_KEYS,
    GRACE_PERIOD_DAYS,
    REPORTING_DEADLINE_DAYS,
    SCENARIOS_BY_LABEL,
)

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "claims_all.csv"

SEED = 42
RECORDS_PER_CLASS = 10000
BASE_DATE = date(2026, 6, 1)

COLUMNS = [
    "claim_id",
    "label",
    "scenario",
    "product_id",
    "user_id",
    "product_name",
    "product_category",
    "brand",
    "model_number",
    "serial_number",
    "serial_status",
    "purchase_date",
    "purchase_price",
    "retailer",
    "warranty_duration_months",
    "warranty_type",
    "warranty_start_date",
    "warranty_expiry_date",
    "claim_submission_date",
    "product_age_days",
    "remaining_warranty_days",
    "fault_occurrence_date",
    "fault_type",
    "fault_description",
    "damage_type",
    "covered_fault",
    "claim_reporting_days",
    "within_reporting_period",
    "reporting_deadline_days",
    "repair_history_count",
    "last_repair_date",
    "repair_authorized",
    "previous_replacement",
    "receipt_available",
    "warranty_card_available",
    "product_image_available",
    "serial_evidence_available",
    "fault_evidence_available",
    "repair_report_available",
    "missing_document_count",
    "mandatory_docs_complete",
    "has_contradiction",
    "contradiction_type",
    "is_duplicate",
    "proof_of_purchase",
    "warranty_active",
    "excluded_damage",
    "ocr_quality",
]


def _iso(d: date) -> str:
    return d.isoformat()


def _add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)


def _serial(rng: random.Random, category: str, brand: str) -> str:
    prefix = SERIAL_PREFIXES.get(category, "GEN")
    return f"{prefix}-{brand[:3].upper()}-{rng.randint(100000, 999999)}"


def _build_base(rng: random.Random, label: str, scenario: dict) -> dict:
    product = rng.choice(PRODUCT_CATALOG)
    brand = rng.choice(product["brands"])
    category = product["category"]

    purchase_date = BASE_DATE - timedelta(days=rng.randint(30, 1100))
    warranty_months = rng.choice(product["warranty_months_options"])
    warranty_type = scenario.get("warranty_type")
    if warranty_type is None:
        warranty_type = "extended" if (warranty_months > 24 and rng.random() < 0.3) else "standard"
    if warranty_type == "extended":
        warranty_months = warranty_months + rng.choice([6, 12])

    warranty_start = purchase_date
    warranty_expiry = _add_months(warranty_start, warranty_months)

    min_gap = 0
    if scenario.get("reporting_days_range"):
        min_gap = scenario["reporting_days_range"][1]

    if scenario.get("force_active_warranty") is True:
        if scenario.get("remaining_days_range"):
            lo, hi = scenario["remaining_days_range"]
            remaining = rng.randint(lo, hi)
            claim_date = warranty_expiry - timedelta(days=remaining)
            if claim_date <= purchase_date + timedelta(days=min_gap):
                claim_date = purchase_date + timedelta(days=min_gap + 1)
        else:
            span = max((warranty_expiry - purchase_date).days - 5, 1)
            claim_date = purchase_date + timedelta(days=rng.randint(min_gap + 5, min(span, min_gap + 200)))
            if claim_date > warranty_expiry:
                claim_date = warranty_expiry - timedelta(days=rng.randint(1, 10))
    elif scenario.get("force_active_warranty") is False and scenario.get("grace_applied"):
        lo, hi = scenario.get("expired_days_range", (1, GRACE_PERIOD_DAYS))
        days_past = rng.randint(lo, hi)
        claim_date = warranty_expiry + timedelta(days=days_past)
    elif scenario.get("force_active_warranty") is False:
        lo, hi = scenario.get("expired_days_range", (30, 400))
        days_past = rng.randint(lo, hi)
        claim_date = warranty_expiry + timedelta(days=days_past)
    else:
        claim_date = purchase_date + timedelta(days=rng.randint(min_gap + 20, 400))

    if claim_date <= purchase_date + timedelta(days=min_gap):
        claim_date = purchase_date + timedelta(days=min_gap + 1)

    if scenario.get("reporting_days_range"):
        lo, hi = scenario["reporting_days_range"]
        max_possible = (claim_date - purchase_date).days
        hi = min(hi, max_possible)
        if lo > hi:
            lo = hi
        reporting_days = rng.randint(lo, hi)
        fault_date = claim_date - timedelta(days=reporting_days)
    else:
        reporting_days = rng.randint(1, min(20, max((claim_date - purchase_date).days, 1)))
        fault_date = claim_date - timedelta(days=reporting_days)

    covered = scenario.get("force_covered_fault")
    if covered is True:
        fault_type = rng.choice(COVERED_FAULTS)
        damage_type = rng.choice(DAMAGE_TYPES[:3])
        fault_desc = rng.choice(FAULT_DESCRIPTIONS["covered"])
    elif covered is False:
        fault_type = rng.choice(EXCLUDED_FAULTS)
        damage_type = rng.choice(DAMAGE_TYPES[3:])
        fault_desc = rng.choice(FAULT_DESCRIPTIONS["excluded"])
    else:
        fault_type = rng.choice(COVERED_FAULTS + EXCLUDED_FAULTS)
        damage_type = rng.choice(DAMAGE_TYPES)
        fault_desc = rng.choice(FAULT_DESCRIPTIONS["covered"])

    excluded_damage = scenario.get("force_excluded_damage")
    if excluded_damage is None:
        excluded_damage = fault_type in EXCLUDED_FAULTS

    repair_mode = scenario.get("repair_mode", "none_or_authorized")
    if repair_mode == "none_or_authorized":
        if rng.random() < 0.45:
            repair_count = rng.randint(1, 2)
            repair_authorized = "yes"
            last_repair = purchase_date + timedelta(days=rng.randint(10, max((claim_date - purchase_date).days, 11)))
            if last_repair > claim_date:
                last_repair = claim_date - timedelta(days=1)
        else:
            repair_count = 0
            repair_authorized = "none"
            last_repair = None
    elif repair_mode == "authorized":
        repair_count = rng.randint(1, 3)
        repair_authorized = "yes"
        last_repair = purchase_date + timedelta(days=rng.randint(10, max((claim_date - purchase_date).days, 11)))
        if last_repair > claim_date:
            last_repair = claim_date - timedelta(days=1)
    else:
        repair_count = rng.randint(1, 2)
        repair_authorized = "no"
        last_repair = purchase_date + timedelta(days=rng.randint(10, max((claim_date - purchase_date).days, 11)))
        if last_repair > claim_date:
            last_repair = claim_date - timedelta(days=1)

    previous_replacement = "yes" if (repair_count >= 2 and rng.random() < 0.3) else "no"

    missing = set(scenario.get("missing_docs", []))
    docs = {k: "no" if k in missing else "yes" for k in ALL_DOC_KEYS}
    if repair_count == 0:
        docs["repair_report"] = "n/a"

    proof_val = scenario.get("proof_of_purchase_value")
    if proof_val is None:
        if docs["receipt"] == "yes":
            proof_val = "yes"
        elif label == "Manual Review":
            proof_val = "uncertain"
        else:
            proof_val = "no"
    proof_bool = proof_val == "yes"

    serial = _serial(rng, category, brand)
    serial_status = scenario.get("force_serial_status", "match")
    if serial_status is None:
        serial_status = "match"

    has_contra = scenario.get("force_contradiction", False)
    contradiction_type = "none"
    if has_contra:
        allowed = scenario.get("allowed_contradictions")
        contradiction_type = rng.choice(allowed) if allowed else rng.choice(CONTRADICTION_TYPES)

    is_dup = bool(scenario.get("force_duplicate", False))

    within = scenario.get("force_within_reporting", True)
    within_bool = within and reporting_days <= REPORTING_DEADLINE_DAYS

    mandatory_keys = ["receipt", "warranty_card", "fault_evidence"]
    if repair_count > 0:
        mandatory_keys.append("repair_report")
    mandatory_complete = all(docs[k] == "yes" for k in mandatory_keys)

    product_age_days = (claim_date - purchase_date).days
    remaining_warranty_days = (warranty_expiry - claim_date).days
    warranty_active = claim_date <= warranty_expiry
    if scenario.get("grace_applied"):
        warranty_active = remaining_warranty_days >= -GRACE_PERIOD_DAYS

    missing_count = sum(1 for v in docs.values() if v == "no")

    if serial_status == "missing_evidence":
        ocr_quality = "low"
    elif has_contra or missing_count >= 2:
        ocr_quality = "medium"
    else:
        if label == "Valid Claim" and rng.random() < 0.15:
            ocr_quality = "medium"
        else:
            ocr_quality = "high"

    price = rng.randint(product["price_range"][0], product["price_range"][1])
    model_number = f"{brand[:2].upper()}{rng.randint(100, 999)}-{category[:3].upper()}"

    covered_fault_val = "yes" if fault_type in COVERED_FAULTS else "no"

    return {
        "label": label,
        "scenario": scenario["name"],
        "product_id": f"PRD-{category[:3].upper()}-{rng.randint(10000, 99999)}",
        "user_id": f"USR-{rng.randint(10000, 99999)}",
        "product_name": product["name"],
        "product_category": category,
        "brand": brand,
        "model_number": model_number,
        "serial_number": serial,
        "serial_status": serial_status,
        "purchase_date": _iso(purchase_date),
        "purchase_price": price,
        "retailer": rng.choice(RETAILERS),
        "warranty_duration_months": warranty_months,
        "warranty_type": warranty_type,
        "warranty_start_date": _iso(warranty_start),
        "warranty_expiry_date": _iso(warranty_expiry),
        "claim_submission_date": _iso(claim_date),
        "product_age_days": product_age_days,
        "remaining_warranty_days": remaining_warranty_days,
        "fault_occurrence_date": _iso(fault_date),
        "fault_type": fault_type,
        "fault_description": fault_desc,
        "damage_type": damage_type,
        "covered_fault": covered_fault_val,
        "claim_reporting_days": reporting_days,
        "within_reporting_period": "yes" if within_bool else "no",
        "reporting_deadline_days": REPORTING_DEADLINE_DAYS,
        "repair_history_count": repair_count,
        "last_repair_date": _iso(last_repair) if last_repair else "",
        "repair_authorized": repair_authorized,
        "previous_replacement": previous_replacement,
        "receipt_available": docs["receipt"],
        "warranty_card_available": docs["warranty_card"],
        "product_image_available": docs["product_image"],
        "serial_evidence_available": docs["serial_evidence"],
        "fault_evidence_available": docs["fault_evidence"],
        "repair_report_available": docs["repair_report"],
        "missing_document_count": missing_count,
        "mandatory_docs_complete": "yes" if mandatory_complete else "no",
        "has_contradiction": "yes" if has_contra else "no",
        "contradiction_type": contradiction_type,
        "is_duplicate": "yes" if is_dup else "no",
        "proof_of_purchase": proof_val,
        "warranty_active": "yes" if warranty_active else "no",
        "excluded_damage": "yes" if excluded_damage else "no",
        "ocr_quality": ocr_quality,
    }


def generate(records_per_class: int = RECORDS_PER_CLASS) -> list[dict]:
    rng = random.Random(SEED)
    rows: list[dict] = []
    claim_seq = 1

    for label in ("Valid Claim", "Invalid Claim", "Manual Review"):
        scenarios = SCENARIOS_BY_LABEL[label]
        total_weight = sum(s["weight"] for s in scenarios)
        counts = []
        allocated = 0
        for i, s in enumerate(scenarios):
            if i == len(scenarios) - 1:
                n = records_per_class - allocated
            else:
                n = int(records_per_class * s["weight"] / total_weight)
                allocated += n
            counts.append(n)

        for scenario, n in zip(scenarios, counts):
            for _ in range(n):
                rec = _build_base(rng, label, scenario)
                rec["claim_id"] = f"CLM-{claim_seq:05d}"
                claim_seq += 1
                rows.append(rec)

    rng.shuffle(rows)
    for i, rec in enumerate(rows, 1):
        rec["claim_id"] = f"CLM-{i:05d}"
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic claims dataset.")
    parser.add_argument("--per-class", type=int, default=RECORDS_PER_CLASS, help="Records per class (default 10,000)")
    parser.add_argument("--output", type=str, default=str(RAW_PATH), help="Output raw CSV path")
    args = parser.parse_args()

    rows = generate(records_per_class=args.per_class)
    out_path = Path(args.output)
    write_csv(rows, out_path)
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["label"]] = counts.get(r["label"], 0) + 1
    print(f"Generated {len(rows)} records -> {out_path}")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()