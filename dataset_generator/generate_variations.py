"""Generate variations for training split Claim Summary Cards.

Produces augmented visual variations of summary cards to enhance computer vision robustness.
Generates >= 2 variations per training record (2,100 variation images total).

Usage:
    python -m dataset_generator.generate_variations
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path
from typing import Dict, List

from src.card.variations import render_card_variation

# Paths
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
TRAIN_CSV = DATA_DIR / "train" / "claims_train.csv"
TRAIN_CARDS_DIR = DATA_DIR / "train" / "cards"

LABEL_TO_DIR: Dict[str, str] = {
    "Valid Claim": "valid_claim",
    "Invalid Claim": "invalid_claim",
    "Manual Review": "manual_review",
}

NUM_VARIATIONS = 2  # Produces 1050 * 2 = 2,100 variation images


def get_label_folder(label: str) -> str:
    """Map human label to clean folder name."""
    if label in LABEL_TO_DIR:
        return LABEL_TO_DIR[label]
    return label.strip().lower().replace(" ", "_")


def read_csv(path: Path) -> List[Dict[str, str]]:
    """Read CSV into list of dicts."""
    if not path.exists():
        raise FileNotFoundError(f"Missing train CSV: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def generate_train_variations(num_variations: int = NUM_VARIATIONS) -> int:
    """Generate visual variations for all training claims."""
    rows = read_csv(TRAIN_CSV)
    print("=" * 60)
    print(f"AssureX Claim Engine — Generating Training Card Variations ({num_variations} per claim)")
    print("=" * 60)
    print(f"Total training claims: {len(rows)}")
    print(f"Expected variation images: {len(rows) * num_variations}")

    start_time = time.time()
    total_generated = 0

    for idx, row in enumerate(rows, 1):
        claim_id = row.get("claim_id", f"CLM-{idx:05d}")
        label = row.get("label", "Manual Review")
        label_dir = get_label_folder(label)
        target_dir = TRAIN_CARDS_DIR / label_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        for v_idx in range(1, num_variations + 1):
            out_path = target_dir / f"{claim_id}_var{v_idx}.png"
            img = render_card_variation(row, variation_index=v_idx)
            img.save(out_path, format="PNG", optimize=True)
            total_generated += 1

        if idx % 150 == 0 or idx == len(rows):
            elapsed = time.time() - start_time
            print(f"  -> Processed {idx}/{len(rows)} claims ({total_generated} variations generated, {elapsed:.1f}s)")

    print(f"\nVariations generation complete! Total variations generated: {total_generated}")
    print("=" * 60)
    return total_generated


def main() -> None:
    generate_train_variations()


if __name__ == "__main__":
    main()