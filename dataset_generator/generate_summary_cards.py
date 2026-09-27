"""Generate Claim Summary Card images for train, validation, and test splits.

Usage:
    python -m dataset_generator.generate_summary_cards
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path
from typing import Dict, List

from src.card.renderer import render_claim_card

# Paths
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"

SPLITS = {
    "train": DATA_DIR / "train" / "claims_train.csv",
    "validation": DATA_DIR / "validation" / "claims_validation.csv",
    "test": DATA_DIR / "test" / "claims_test.csv",
}

LABEL_TO_DIR: Dict[str, str] = {
    "Valid Claim": "valid_claim",
    "Invalid Claim": "invalid_claim",
    "Manual Review": "manual_review",
}


def get_label_folder(label: str) -> str:
    """Map human label to clean filesystem folder name."""
    if label in LABEL_TO_DIR:
        return LABEL_TO_DIR[label]
    clean = label.strip().lower().replace(" ", "_")
    return clean


def read_csv(path: Path) -> List[Dict[str, str]]:
    """Read a CSV file into a list of row dictionaries."""
    if not path.exists():
        raise FileNotFoundError(f"Missing CSV file: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def generate_split_cards(split_name: str, csv_path: Path) -> int:
    """Generate base summary cards for all claims in a split."""
    rows = read_csv(csv_path)
    output_base = DATA_DIR / split_name / "cards"
    
    # Ensure label directories exist
    for sub in LABEL_TO_DIR.values():
        (output_base / sub).mkdir(parents=True, exist_ok=True)

    print(f"[{split_name.upper()}] Generating {len(rows)} summary cards...")
    start_time = time.time()
    
    count = 0
    for idx, row in enumerate(rows, 1):
        claim_id = row.get("claim_id", f"CLM-{idx:05d}")
        label = row.get("label", "Manual Review")
        label_dir = get_label_folder(label)
        
        target_path = output_base / label_dir / f"{claim_id}.png"
        img = render_claim_card(row)
        img.save(target_path, format="PNG", optimize=True)
        count += 1

        if idx % 150 == 0 or idx == len(rows):
            elapsed = time.time() - start_time
            print(f"  -> Generated {idx}/{len(rows)} cards ({elapsed:.1f}s)")

    return count


def generate_all_summary_cards() -> Dict[str, int]:
    """Generate base summary cards across train, validation, and test splits."""
    print("=" * 60)
    print("AssureX Claim Engine — Generating Base Summary Cards")
    print("=" * 60)

    results = {}
    total = 0
    for split_name, csv_path in SPLITS.items():
        count = generate_split_cards(split_name, csv_path)
        results[split_name] = count
        total += count

    print(f"\nAll base cards generated successfully! Total: {total} cards.")
    for split, count in results.items():
        print(f"  - {split.title()}: {count} cards")
    print("=" * 60)
    return results


def main() -> None:
    generate_all_summary_cards()


if __name__ == "__main__":
    main()