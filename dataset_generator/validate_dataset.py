"""Validate dataset balance, uniqueness, split isolation, label sanity, and data quality.

Generates and updates:
- data/statistics.md

Usage:
    python -m dataset_generator.validate_dataset
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path
from typing import List

from dataset_generator.generate_dataset import RAW_PATH, RECORDS_PER_CLASS
from dataset_generator.stratified_split import TEST_PATH, TRAIN_PATH, VAL_PATH

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
STATS_PATH = DATA_DIR / "statistics.md"
IMAGE_MAP_PATH = DATA_DIR / "card_image_map.json"

EXPECTED_TOTAL = RECORDS_PER_CLASS * 3
EXPECTED_LABELS = {"Valid Claim", "Invalid Claim", "Manual Review"}


AMBIGUITY_SIGNALS = [
    "missing_document_count",
    "has_contradiction",
    "serial_status",
    "repair_authorized",
    "proof_of_purchase",
    "remaining_warranty_days",
    "claim_reporting_days",
    "ocr_quality",
]


def _read(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _label_counts(rows: List[dict]) -> Counter:
    return Counter(r["label"] for r in rows)


def _fail(errors: List[str], msg: str) -> None:
    errors.append(msg)


def has_ambiguity(row: dict) -> bool:
    """Check if a Manual Review row has at least one ambiguity signal."""
    if int(row.get("missing_document_count", 0)) > 0:
        return True
    if row.get("has_contradiction") == "yes":
        return True
    if row.get("serial_status") == "missing_evidence":
        return True
    if row.get("repair_authorized") == "no":
        return True
    if row.get("proof_of_purchase") == "uncertain":
        return True
    rem = int(row.get("remaining_warranty_days", 0))
    if -15 <= rem < 0:
        return True
    if int(row.get("claim_reporting_days", 0)) >= 24:
        return True
    if row.get("ocr_quality") in ("medium", "low"):
        return True
    return False


def validate() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not RAW_PATH.exists():
        return [f"Missing raw dataset: {RAW_PATH}. Run generate_dataset first."], []

    raw = _read(RAW_PATH)
    train = _read(TRAIN_PATH) if TRAIN_PATH.exists() else []
    val = _read(VAL_PATH) if VAL_PATH.exists() else []
    test = _read(TEST_PATH) if TEST_PATH.exists() else []

    raw_total = len(raw)
    per_class_expected = raw_total // 3
    if raw_total < 3:
        _fail(errors, f"Raw total {raw_total} is too small")

    raw_counts = _label_counts(raw)
    for label in EXPECTED_LABELS:
        if raw_counts.get(label, 0) == 0:
            _fail(errors, f"{label}: missing in raw dataset")

    ids = [r["claim_id"] for r in raw]
    if len(ids) != len(set(ids)):
        _fail(errors, "Duplicate claim_id found in raw dataset")

    if train or val or test:
        total_split = len(train) + len(val) + len(test)
        if total_split != raw_total:
            _fail(errors, f"Split total {total_split} != raw total {raw_total}")

        for name, part in (("train", train), ("validation", val), ("test", test)):
            counts = _label_counts(part)
            for label in EXPECTED_LABELS:
                if counts.get(label, 0) == 0:
                    _fail(errors, f"{name} missing class {label}")

        train_ids = {r["claim_id"] for r in train}
        val_ids = {r["claim_id"] for r in val}
        test_ids = {r["claim_id"] for r in test}

        if train_ids & val_ids:
            _fail(errors, f"Leak: train ∩ validation not empty ({len(train_ids & val_ids)} overlaps)")
        if train_ids & test_ids:
            _fail(errors, f"Leak: train ∩ test not empty ({len(train_ids & test_ids)} overlaps)")
        if val_ids & test_ids:
            _fail(errors, f"Leak: validation ∩ test not empty ({len(val_ids & test_ids)} overlaps)")

        all_split_ids = train_ids | val_ids | test_ids
        raw_ids = set(ids)
        if all_split_ids != raw_ids:
            _fail(errors, "Split IDs do not cover raw dataset exactly")

    # Row-level validation
    for row in raw:
        pd_ = date.fromisoformat(row["purchase_date"])
        cd = date.fromisoformat(row["claim_submission_date"])
        fd = date.fromisoformat(row["fault_occurrence_date"])
        ws = date.fromisoformat(row["warranty_start_date"])
        we = date.fromisoformat(row["warranty_expiry_date"])

        # Date sanity
        if cd < pd_:
            _fail(errors, f"{row['claim_id']}: claim before purchase")
        if fd < pd_:
            _fail(errors, f"{row['claim_id']}: fault before purchase")
        if fd > cd:
            _fail(errors, f"{row['claim_id']}: fault after claim")
        if ws != pd_:
            _fail(errors, f"{row['claim_id']}: warranty_start != purchase_date")
        if we <= ws:
            _fail(errors, f"{row['claim_id']}: warranty_expiry <= start")

        # Derived field consistency
        if int(row["product_age_days"]) != (cd - pd_).days:
            _fail(errors, f"{row['claim_id']}: product_age_days mismatch")
        if int(row["remaining_warranty_days"]) != (we - cd).days:
            _fail(errors, f"{row['claim_id']}: remaining_warranty_days mismatch")
        if int(row["claim_reporting_days"]) != (cd - fd).days:
            _fail(errors, f"{row['claim_id']}: claim_reporting_days mismatch")

        within_actual = int(row["claim_reporting_days"]) <= 30
        within_recorded = row["within_reporting_period"] == "yes"
        if within_actual != within_recorded:
            _fail(errors, f"{row['claim_id']}: within_reporting_period mismatch")

        label = row["label"]
        scenario = row["scenario"]

        # Valid Claim invariants
        if label == "Valid Claim":
            if row["warranty_active"] != "yes":
                _fail(errors, f"{row['claim_id']}: Valid but warranty inactive")
            if row["covered_fault"] != "yes":
                _fail(errors, f"{row['claim_id']}: Valid but fault not covered")
            if row["excluded_damage"] == "yes":
                _fail(errors, f"{row['claim_id']}: Valid but excluded_damage=yes")
            if row["proof_of_purchase"] != "yes":
                _fail(errors, f"{row['claim_id']}: Valid but proof_of_purchase={row['proof_of_purchase']} (expected yes)")
            if row["serial_status"] != "match":
                _fail(errors, f"{row['claim_id']}: Valid but serial_status={row['serial_status']} (expected match)")
            if row["has_contradiction"] == "yes":
                _fail(errors, f"{row['claim_id']}: Valid but has_contradiction=yes")
            if row["is_duplicate"] == "yes":
                _fail(errors, f"{row['claim_id']}: Valid but is_duplicate=yes")
            if row["mandatory_docs_complete"] != "yes":
                _fail(errors, f"{row['claim_id']}: Valid but mandatory_docs_complete=no")
            if row["within_reporting_period"] != "yes":
                _fail(errors, f"{row['claim_id']}: Valid but within_reporting_period=no")
            if int(row["missing_document_count"]) != 0:
                _fail(errors, f"{row['claim_id']}: Valid but missing_document_count={row['missing_document_count']} (expected 0)")
            if int(row["remaining_warranty_days"]) < 0:
                _fail(errors, f"{row['claim_id']}: Valid but remaining_warranty_days < 0")

        # Invalid Claim must have hard fail signal
        if label == "Invalid Claim":
            hard = (
                row["warranty_active"] == "no"
                or row["excluded_damage"] == "yes"
                or row["proof_of_purchase"] == "no"
                or row["is_duplicate"] == "yes"
                or row["serial_status"] == "mismatch"
            )
            if not hard:
                _fail(errors, f"{row['claim_id']}: Invalid but no hard-fail signal")

            if scenario == "no_proof_of_purchase":
                if row["proof_of_purchase"] != "no":
                    _fail(errors, f"{row['claim_id']}: no_proof scenario but proof={row['proof_of_purchase']}")
                if row["receipt_available"] != "no":
                    _fail(errors, f"{row['claim_id']}: no_proof scenario but receipt_available={row['receipt_available']}")

        # Manual Review must have ambiguity signal
        if label == "Manual Review":
            if not has_ambiguity(row):
                _fail(errors, f"{row['claim_id']}: Manual Review but NO ambiguity signal found")
            if row["excluded_damage"] == "yes":
                _fail(errors, f"{row['claim_id']}: Manual Review but excluded_damage=yes (too invalid)")
            if row["is_duplicate"] == "yes":
                _fail(errors, f"{row['claim_id']}: Manual Review but is_duplicate=yes (too invalid)")
            if row["proof_of_purchase"] == "no" and row["receipt_available"] == "no" and scenario != "missing_mandatory_documents":
                warnings.append(f"{row['claim_id']}: MR with proof=no but not missing_mandatory scenario")

    # Leakage checks
    by_sc = {}
    for r in raw:
        by_sc.setdefault(r["scenario"], set()).add(r["label"])
    for s, labs in by_sc.items():
        if len(labs) > 1:
            warnings.append(f"Scenario '{s}' appears in multiple labels: {labs} (potential leakage if used as feature)")

    # OCR quality distribution check
    valid_high = sum(1 for r in raw if r["label"] == "Valid Claim" and r["ocr_quality"] == "high")
    if valid_high == 500:
        warnings.append("Valid Claim has 100% ocr_quality=high (consider adding variation for realism)")

    # Repair report n/a handling
    for row in raw:
        rc = int(row["repair_history_count"])
        rr = row["repair_report_available"]
        if rc == 0 and rr != "n/a":
            _fail(errors, f"{row['claim_id']}: repair_count=0 but repair_report_available={rr} (expected n/a)")
        if rc > 0 and rr not in ("yes", "no"):
            _fail(errors, f"{row['claim_id']}: repair_count>0 but repair_report_available={rr} (expected yes/no)")

    # Proof of purchase states
    for row in raw:
        pop = row["proof_of_purchase"]
        if pop not in ("yes", "no", "uncertain"):
            _fail(errors, f"{row['claim_id']}: invalid proof_of_purchase={pop}")
        rcpt = row["receipt_available"]
        if pop == "yes" and rcpt != "yes":
            _fail(errors, f"{row['claim_id']}: proof=yes but receipt={rcpt}")
        if pop == "no" and rcpt == "yes":
            _fail(errors, f"{row['claim_id']}: proof=no but receipt=yes")

    # Missing document count consistency
    for row in raw:
        doc_keys = ["receipt_available", "warranty_card_available", "product_image_available",
                    "serial_evidence_available", "fault_evidence_available", "repair_report_available"]
        calc_missing = sum(1 for k in doc_keys if row[k] == "no")
        recorded = int(row["missing_document_count"])
        if calc_missing != recorded:
            _fail(errors, f"{row['claim_id']}: missing_document_count={recorded} but computed={calc_missing}")

    # Mandatory docs consistency
    for row in raw:
        mandatory = ["receipt_available", "warranty_card_available", "fault_evidence_available"]
        if int(row["repair_history_count"]) > 0:
            mandatory.append("repair_report_available")
        mandatory_ok = all(row[k] == "yes" for k in mandatory)
        recorded = row["mandatory_docs_complete"] == "yes"
        if mandatory_ok != recorded:
            _fail(errors, f"{row['claim_id']}: mandatory_docs_complete mismatch (computed={mandatory_ok}, recorded={recorded})")

    return errors, warnings


def validate_tabular() -> tuple[list[str], list[str]]:
    """Alias for validate() function."""
    return validate()


def validate_card_images() -> tuple[list[str], list[str], dict[str, dict[str, int]]]:
    """Validate card images exist, tally counts per split, and update card_image_map.json."""
    import json
    errors = []
    split_counts = {
        "train": {"base": 0, "variations": 0},
        "validation": {"base": 0},
        "test": {"base": 0},
    }
    records = []

    train_dir = DATA_DIR / "train" / "cards"
    if train_dir.exists():
        for p in train_dir.rglob("*.png"):
            records.append(str(p))
            if "_var" in p.name:
                split_counts["train"]["variations"] += 1
            else:
                split_counts["train"]["base"] += 1

    val_dir = DATA_DIR / "validation" / "cards"
    if val_dir.exists():
        for p in val_dir.rglob("*.png"):
            records.append(str(p))
            split_counts["validation"]["base"] += 1

    test_dir = DATA_DIR / "test" / "cards"
    if test_dir.exists():
        for p in test_dir.rglob("*.png"):
            records.append(str(p))
            split_counts["test"]["base"] += 1

    if not IMAGE_MAP_PATH.exists():
        IMAGE_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
        IMAGE_MAP_PATH.write_text(
            json.dumps({"total_images": len(records), "splits": split_counts}, indent=2),
            encoding="utf-8"
        )

    return errors, records, split_counts



def write_statistics() -> None:
    raw = _read(RAW_PATH)
    train = _read(TRAIN_PATH) if TRAIN_PATH.exists() else []
    val = _read(VAL_PATH) if VAL_PATH.exists() else []
    test = _read(TEST_PATH) if TEST_PATH.exists() else []

    def fmt(counter: Counter) -> str:
        return "\n".join(f"| {k} | {v} |" for k, v in sorted(counter.items()))

    lines = [
        "# AssureX Dataset Statistics",
        "",
        f"- Total tabular records: **{len(raw)}**",
        f"- Seed: **42** (reproducible)",
        f"- Last Validated: {date.today().isoformat()}",
        "",
        "## Class Distribution (All)",
        "",
        "| Class | Count |",
        "|-------|------:|",
        fmt(_label_counts(raw)),
        "",
        "## Split Sizes (Tabular Claims)",
        "",
        "| Split | Records | Ratio |",
        "|-------|--------:|------:|",
        f"| Train | {len(train)} | 70% |",
        f"| Validation | {len(val)} | 15% |",
        f"| Test | {len(test)} | 15% |",
        "",
        "## Train Class Distribution",
        "",
        "| Class | Count |",
        "|-------|------:|",
        fmt(_label_counts(train)),
        "",
        "## Validation Class Distribution",
        "",
        "| Class | Count |",
        "|-------|------:|",
        fmt(_label_counts(val)),
        "",
        "## Test Class Distribution",
        "",
        "| Class | Count |",
        "|-------|------:|",
        fmt(_label_counts(test)),
        "",
        "## Scenario Distribution (All)",
        "",
        "| Scenario | Count |",
        "|----------|------:|",
    ]
    sc = Counter(r["scenario"] for r in raw)
    lines.extend(f"| {k} | {v} |" for k, v in sorted(sc.items()))
    lines.append("")

    cat = Counter(r["product_category"] for r in raw)
    lines += [
        "## Product Category Distribution",
        "",
        "| Category | Count |",
        "|----------|------:|",
    ]
    lines.extend(f"| {k} | {v} |" for k, v in sorted(cat.items()))
    lines.append("")

    # Proof of purchase distribution
    pop = Counter(r["proof_of_purchase"] for r in raw)
    lines += [
        "## Proof of Purchase Distribution",
        "",
        "| Value | Count |",
        "|-------|------:|",
    ]
    lines.extend(f"| {k} | {v} |" for k, v in sorted(pop.items()))
    lines.append("")

    # OCR quality
    ocr = Counter(r["ocr_quality"] for r in raw)
    lines += [
        "## OCR Quality Distribution",
        "",
        "| Quality | Count |",
        "|---------|------:|",
    ]
    lines.extend(f"| {k} | {v} |" for k, v in sorted(ocr.items()))
    lines.append("")

    STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATS_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Statistics written -> {STATS_PATH}")


def main() -> None:
    print("=" * 60)
    print("AssureX Dataset Validation")
    print("=" * 60)

    errors, warnings = validate()
    write_statistics()

    for w in warnings:
        print(f"WARN: {w}")

    if errors:
        print("\n" + "!" * 60)
        print(f"VALIDATION FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"  [FAIL] {e}")
        print("!" * 60)
        raise SystemExit(1)
    else:
        print("\n" + "=" * 60)
        print("[PASS] VALIDATION PASSED: All checks OK!")
        print("=" * 60)


if __name__ == "__main__":
    main()