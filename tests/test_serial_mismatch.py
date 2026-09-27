"""Unit tests for Serial Number Verification and Mismatch Detection."""

import pytest
from src.services.serial_service import (
    SerialService,
    calculate_similarity,
    compare_serials,
    get_serial_service,
    validate_serial_format,
    verify_claim_serial,
    verify_serial_number,
)


def test_serial_exact_match():
    """Verify exact match returns match status and is_valid True."""
    res = verify_serial_number("ELC-DEL-984830", "ELC-DEL-984830", prefix_expected="ELC-DEL-")
    assert res["status"] == "match"
    assert res["is_valid"] is True
    assert res["similarity"] == 1.0
    assert res["prefix_valid"] is True


def test_serial_exact_match_case_and_whitespace():
    """Verify exact match handles case differences and leading/trailing whitespace."""
    res = verify_serial_number("  elc-del-984830  ", "ELC-DEL-984830")
    assert res["status"] == "match"
    assert res["is_valid"] is True
    assert res["similarity"] == 1.0


def test_serial_fuzzy_match():
    """Verify 1-char OCR typo matches with fuzzy threshold."""
    res = verify_serial_number("ELC-DEL-98483O", "ELC-DEL-984830", threshold=0.85)  # O vs 0
    assert res["status"] == "fuzzy_match"
    assert res["is_valid"] is True
    assert res["similarity"] >= 0.85


def test_serial_mismatch():
    """Verify completely different serial returns mismatch."""
    res = verify_serial_number("SMG-GAL-112233", "ELC-DEL-984830")
    assert res["status"] == "mismatch"
    assert res["is_valid"] is False
    assert res["similarity"] < 0.85


def test_serial_prefix_mismatch():
    """Verify prefix validation flag is False when expected prefix is absent."""
    res = verify_serial_number("APP-IPH-984830", "APP-IPH-984830", prefix_expected="ELC-DEL-")
    assert res["status"] == "match"
    assert res["prefix_valid"] is False


def test_validate_serial_format_variations():
    """Verify format checks on short, empty, or valid serial strings."""
    valid, err = validate_serial_format("ELC-DEL-984830")
    assert valid is True
    assert err is None

    short_valid, err = validate_serial_format("A1")
    assert short_valid is False
    assert "too short" in err

    empty_valid, err = validate_serial_format("")
    assert empty_valid is False
    assert "required" in err

    none_valid, err = validate_serial_format(None)
    assert none_valid is False


def test_compare_serials_missing_evidence():
    """Verify missing OCR evidence returns missing_evidence status."""
    res = compare_serials("ELC-DEL-984830", None)
    assert res["status"] == "missing_evidence"
    assert res["match"] is False

    res_empty = compare_serials("ELC-DEL-984830", "")
    assert res_empty["status"] == "missing_evidence"
    assert res_empty["match"] is False

    res_na = compare_serials("ELC-DEL-984830", "N/A")
    assert res_na["status"] == "missing_evidence"
    assert res_na["match"] is False


def test_verify_claim_serial_scenarios():
    """Verify verify_claim_serial with claim payload dicts."""
    # Match claim
    claim_valid = {
        "serial_number": "ELC-DEL-984830",
        "serial_status": "match",
        "serial_evidence_available": "yes",
    }
    res_valid = verify_claim_serial(claim_valid)
    assert res_valid["status"] == "match"
    assert res_valid["is_valid"] is True

    # Missing evidence claim
    claim_no_evidence = {
        "serial_number": "ELC-DEL-984830",
        "serial_evidence_available": "no",
    }
    res_no_ev = verify_claim_serial(claim_no_evidence)
    assert res_no_ev["status"] == "missing_evidence"
    assert res_no_ev["is_valid"] is False

    # Mismatch claim
    claim_mismatch = {
        "serial_number": "ELC-DEL-984830",
        "serial_status": "mismatch",
        "serial_evidence_available": "yes",
    }
    res_mismatch = verify_claim_serial(claim_mismatch)
    assert res_mismatch["status"] == "mismatch"
    assert res_mismatch["is_valid"] is False


def test_serial_service_class_wrapper():
    """Verify SerialService instance methods."""
    service = get_serial_service()
    assert isinstance(service, SerialService)

    v_res = service.verify("SN12345", "SN12345")
    assert v_res["status"] == "match"

    fmt_ok, _ = service.validate_format("SN12345")
    assert fmt_ok is True

    cmp_res = service.compare("SN12345", "SN12345")
    assert cmp_res["match"] is True