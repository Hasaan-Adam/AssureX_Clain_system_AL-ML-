"""Stratified 70/15/15 split of the raw claim dataset.

Usage:
    python -m dataset_generator.stratified_split
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

from dataset_generator.generate_dataset import COLUMNS, RAW_PATH, SEED

ROOT = Path(__file__).resolve().parents[1]
TRAIN_PATH = ROOT / "data" / "train" / "claims_train.csv"
VAL_PATH = ROOT / "data" / "validation" / "claims_validation.csv"
TEST_PATH = ROOT / "data" / "test" / "claims_test.csv"

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15


def load_raw(path: Path = RAW_PATH) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def stratified_split(
    rows: list[dict],
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    test_ratio: float = TEST_RATIO,
    seed: int = SEED,
) -> tuple[list[dict], list[dict], list[dict]]:
    rng = random.Random(seed)
    by_label: dict[str, list[dict]] = {}
    for row in rows:
        by_label.setdefault(row["label"], []).append(row)

    train: list[dict] = []
    val: list[dict] = []
    test: list[dict] = []

    for label in sorted(by_label):
        group = by_label[label]
        rng.shuffle(group)
        n = len(group)
        n_train = int(round(n * train_ratio))
        n_val = int(round(n * val_ratio))
        n_test = n - n_train - n_val
        if n_test < 0:
            n_val += n_test
            n_test = 0
        train.extend(group[:n_train])
        val.extend(group[n_train:n_train + n_val])
        test.extend(group[n_train + n_val:])

    for part in (train, val, test):
        rng.shuffle(part)
    return train, val, test


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_id_map(train: list[dict], val: list[dict], test: list[dict]) -> None:
    path = ROOT / "data" / "claim_id_split_map.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["claim_id", "label", "split"])
        for row in train:
            writer.writerow([row["claim_id"], row["label"], "train"])
        for row in val:
            writer.writerow([row["claim_id"], row["label"], "validation"])
        for row in test:
            writer.writerow([row["claim_id"], row["label"], "test"])


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Perform stratified split on raw dataset.")
    parser.add_argument("--train-ratio", type=float, default=TRAIN_RATIO, help="Train split ratio")
    parser.add_argument("--val-ratio", type=float, default=VAL_RATIO, help="Validation split ratio")
    parser.add_argument("--test-ratio", type=float, default=TEST_RATIO, help="Test split ratio")
    args = parser.parse_args()

    rows = load_raw()
    train, val, test = stratified_split(
        rows,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
    )
    write_csv(train, TRAIN_PATH)
    write_csv(val, VAL_PATH)
    write_csv(test, TEST_PATH)
    write_id_map(train, val, test)

    def label_counts(part: list[dict]) -> dict[str, int]:
        c: dict[str, int] = {}
        for r in part:
            c[r["label"]] = c.get(r["label"], 0) + 1
        return c

    print(f"Train: {len(train)} -> {TRAIN_PATH.name} {label_counts(train)}")
    print(f"Val:   {len(val)} -> {VAL_PATH.name} {label_counts(val)}")
    print(f"Test:  {len(test)} -> {TEST_PATH.name} {label_counts(test)}")


if __name__ == "__main__":
    main()
