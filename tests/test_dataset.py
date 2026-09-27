"""Pytest tests for Phase 1: Dataset generation, split, and validation."""

import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_PATH = DATA_DIR / "raw" / "claims_all.csv"
TRAIN_PATH = DATA_DIR / "train" / "claims_train.csv"
VAL_PATH = DATA_DIR / "validation" / "claims_validation.csv"
TEST_PATH = DATA_DIR / "test" / "claims_test.csv"
SPLIT_MAP_PATH = DATA_DIR / "claim_id_split_map.csv"


def _read(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="session")
def raw_data():
    return _read(RAW_PATH)


@pytest.fixture(scope="session")
def split_data():
    return {
        "train": _read(TRAIN_PATH),
        "validation": _read(VAL_PATH),
        "test": _read(TEST_PATH),
    }


class TestDatasetBasics:
    def test_raw_exists(self):
        assert RAW_PATH.exists(), "Raw dataset not generated"

    def test_splits_exist(self):
        for p in (TRAIN_PATH, VAL_PATH, TEST_PATH):
            assert p.exists(), f"Split missing: {p}"

    def test_total_records(self, raw_data):
        assert len(raw_data) == 1500

    def test_class_balance(self, raw_data):
        from collections import Counter
        counts = Counter(r["label"] for r in raw_data)
        assert counts["Valid Claim"] == 500
        assert counts["Invalid Claim"] == 500
        assert counts["Manual Review"] == 500

    def test_unique_claim_ids(self, raw_data):
        ids = [r["claim_id"] for r in raw_data]
        assert len(ids) == len(set(ids))

    def test_split_sizes(self, split_data):
        assert len(split_data["train"]) == 1050
        assert len(split_data["validation"]) == 225
        assert len(split_data["test"]) == 225

    def test_split_class_balance(self, split_data):
        from collections import Counter
        for name, part in split_data.items():
            counts = Counter(r["label"] for r in part)
            assert counts["Valid Claim"] > 0
            assert counts["Invalid Claim"] > 0
            assert counts["Manual Review"] > 0

    def test_no_split_leakage(self, split_data):
        train_ids = {r["claim_id"] for r in split_data["train"]}
        val_ids = {r["claim_id"] for r in split_data["validation"]}
        test_ids = {r["claim_id"] for r in split_data["test"]}
        assert len(train_ids & val_ids) == 0
        assert len(train_ids & test_ids) == 0
        assert len(val_ids & test_ids) == 0

    def test_split_covers_raw(self, raw_data, split_data):
        raw_ids = {r["claim_id"] for r in raw_data}
        all_split = set()
        for part in split_data.values():
            all_split.update(r["claim_id"] for r in part)
        assert all_split == raw_ids


class TestValidClaimInvariants:
    @pytest.fixture
    def valid_claims(self, raw_data):
        return [r for r in raw_data if r["label"] == "Valid Claim"]

    def test_warranty_active(self, valid_claims):
        for r in valid_claims:
            assert r["warranty_active"] == "yes"

    def test_covered_fault(self, valid_claims):
        for r in valid_claims:
            assert r["covered_fault"] == "yes"

    def test_excluded_damage(self, valid_claims):
        for r in valid_claims:
            assert r["excluded_damage"] == "no"

    def test_proof_of_purchase(self, valid_claims):
        for r in valid_claims:
            assert r["proof_of_purchase"] == "yes"

    def test_serial_match(self, valid_claims):
        for r in valid_claims:
            assert r["serial_status"] == "match"

    def test_no_contradiction(self, valid_claims):
        for r in valid_claims:
            assert r["has_contradiction"] == "no"

    def test_no_duplicate(self, valid_claims):
        for r in valid_claims:
            assert r["is_duplicate"] == "no"

    def test_mandatory_docs_complete(self, valid_claims):
        for r in valid_claims:
            assert r["mandatory_docs_complete"] == "yes"

    def test_within_reporting(self, valid_claims):
        for r in valid_claims:
            assert r["within_reporting_period"] == "yes"

    def test_zero_missing_docs(self, valid_claims):
        for r in valid_claims:
            assert int(r["missing_document_count"]) == 0

    def test_remaining_nonnegative(self, valid_claims):
        for r in valid_claims:
            assert int(r["remaining_warranty_days"]) >= 0


class TestInvalidClaimHardSignals:
    @pytest.fixture
    def invalid_claims(self, raw_data):
        return [r for r in raw_data if r["label"] == "Invalid Claim"]

    def test_each_has_hard_signal(self, invalid_claims):
        for r in invalid_claims:
            hard = (
                r["warranty_active"] == "no"
                or r["excluded_damage"] == "yes"
                or r["proof_of_purchase"] == "no"
                or r["is_duplicate"] == "yes"
                or r["serial_status"] == "mismatch"
            )
            assert hard, f"{r['claim_id']} ({r['scenario']}) has no hard signal"


class TestManualReviewAmbiguity:
    @pytest.fixture
    def mr_claims(self, raw_data):
        return [r for r in raw_data if r["label"] == "Manual Review"]

    def test_each_has_ambiguity(self, mr_claims):
        for r in mr_claims:
            has_amb = (
                int(r["missing_document_count"]) > 0
                or r["has_contradiction"] == "yes"
                or r["serial_status"] == "missing_evidence"
                or r["repair_authorized"] == "no"
                or r["proof_of_purchase"] == "uncertain"
                or -15 <= int(r["remaining_warranty_days"]) < 0
                or int(r["claim_reporting_days"]) >= 24
                or r["ocr_quality"] in ("medium", "low")
            )
            assert has_amb, f"{r['claim_id']} ({r['scenario']}) missing ambiguity signal"

    def test_not_clearly_invalid(self, mr_claims):
        for r in mr_claims:
            assert r["excluded_damage"] == "no"
            assert r["is_duplicate"] == "no"


class TestDerivedFieldsConsistency:
    def test_product_age(self, raw_data):
        from datetime import date
        for r in raw_data:
            pd_ = date.fromisoformat(r["purchase_date"])
            cd = date.fromisoformat(r["claim_submission_date"])
            assert int(r["product_age_days"]) == (cd - pd_).days

    def test_remaining_warranty(self, raw_data):
        from datetime import date
        for r in raw_data:
            cd = date.fromisoformat(r["claim_submission_date"])
            we = date.fromisoformat(r["warranty_expiry_date"])
            assert int(r["remaining_warranty_days"]) == (we - cd).days

    def test_reporting_days(self, raw_data):
        from datetime import date
        for r in raw_data:
            cd = date.fromisoformat(r["claim_submission_date"])
            fd = date.fromisoformat(r["fault_occurrence_date"])
            assert int(r["claim_reporting_days"]) == (cd - fd).days

    def test_within_reporting(self, raw_data):
        for r in raw_data:
            actual = int(r["claim_reporting_days"]) <= 30
            recorded = r["within_reporting_period"] == "yes"
            assert actual == recorded


class TestDocumentStates:
    def test_repair_report_na_when_no_repairs(self, raw_data):
        for r in raw_data:
            rc = int(r["repair_history_count"])
            if rc == 0:
                assert r["repair_report_available"] == "n/a"
            else:
                assert r["repair_report_available"] in ("yes", "no")

    def test_missing_count_consistency(self, raw_data):
        for r in raw_data:
            doc_keys = [
                "receipt_available", "warranty_card_available",
                "product_image_available", "serial_evidence_available",
                "fault_evidence_available", "repair_report_available",
            ]
            calc = sum(1 for k in doc_keys if r[k] == "no")
            assert calc == int(r["missing_document_count"])

    def test_mandatory_docs_consistency(self, raw_data):
        for r in raw_data:
            mandatory = ["receipt_available", "warranty_card_available", "fault_evidence_available"]
            if int(r["repair_history_count"]) > 0:
                mandatory.append("repair_report_available")
            ok = all(r[k] == "yes" for k in mandatory)
            assert (r["mandatory_docs_complete"] == "yes") == ok

    def test_proof_of_purchase_states(self, raw_data):
        for r in raw_data:
            pop = r["proof_of_purchase"]
            assert pop in ("yes", "no", "uncertain")
            if pop == "yes":
                assert r["receipt_available"] == "yes"
            if pop == "no":
                assert r["receipt_available"] == "no"


class TestProofOfPurchaseLogic:
    def test_valid_proof_yes(self, raw_data):
        valid = [r for r in raw_data if r["label"] == "Valid Claim"]
        for r in valid:
            assert r["proof_of_purchase"] == "yes"

    def test_invalid_no_proof_scenario(self, raw_data):
        no_proof = [r for r in raw_data if r["scenario"] == "no_proof_of_purchase"]
        for r in no_proof:
            assert r["proof_of_purchase"] == "no"
            assert r["receipt_available"] == "no"

    def test_mr_missing_mandatory_proof_uncertain(self, raw_data):
        mr_missing = [r for r in raw_data if r["scenario"] == "missing_mandatory_documents"]
        for r in mr_missing:
            assert r["proof_of_purchase"] == "uncertain"
            assert r["receipt_available"] == "no"


class TestNoLabelLeakage:
    def test_scenario_unique_to_label(self, raw_data):
        from collections import defaultdict
        by_sc = defaultdict(set)
        for r in raw_data:
            by_sc[r["scenario"]].add(r["label"])
        for s, labs in by_sc.items():
            assert len(labs) == 1, f"Scenario '{s}' leaks across labels: {labs}"

    def test_ocr_quality_not_perfect_predictor(self, raw_data):
        # Valid shouldn't be 100% high OCR
        valid_ocr = [r["ocr_quality"] for r in raw_data if r["label"] == "Valid Claim"]
        high_pct = valid_ocr.count("high") / len(valid_ocr)
        assert high_pct < 1.0, "Valid Claim has 100% high OCR (leakage risk)"


class TestSplitMap:
    def test_split_map_exists(self):
        assert SPLIT_MAP_PATH.exists()

    def test_split_map_matches(self, split_data):
        split_map = _read(SPLIT_MAP_PATH)
        for row in split_map:
            claim_id = row["claim_id"]
            expected_split = row["split"]
            found = False
            for split_name, part in split_data.items():
                if any(r["claim_id"] == claim_id for r in part):
                    assert split_name == expected_split
                    found = True
                    break
            assert found, f"{claim_id} not found in any split"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])