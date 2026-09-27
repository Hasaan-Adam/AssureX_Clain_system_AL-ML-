"""
Unit tests for Document Duplicate and SHA-256 Hash Matching.
"""

from datetime import date, timedelta

from src.models.document import Document
from src.services.duplicate_service import check_duplicate_document

DOC_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def _seed_claim(test_db, sample_warranty, customer_user):
    from database.models import Claim

    claim = Claim(
        claim_id="CLM-DUP-00001",
        claimant_id=customer_user.id,
        product_id=sample_warranty.product_id,
        warranty_id=sample_warranty.id,
        fault_occurrence_date=date.today() - timedelta(days=2),
        fault_type="Screen Damage",
        fault_description="Cracked panel after drop.",
        damage_type="physical_damage",
        claim_amount=120.0,
        claim_submission_date=date.today(),
        status="submitted",
    )
    test_db.add(claim)
    test_db.commit()
    test_db.refresh(claim)
    return claim


def test_document_hash_duplicate_detection(test_db, sample_warranty, customer_user):
    """Test detecting an identical document hash (SHA-256) on a stored document."""
    claim = _seed_claim(test_db, sample_warranty, customer_user)

    doc = Document(
        claim_id=claim.id,
        uploader_id=customer_user.id,
        document_type="purchase_invoice",
        file_path="/tmp/invoice.pdf",
        file_size=2048,
        mime_type="application/pdf",
        file_hash=DOC_HASH,
    )
    test_db.add(doc)
    test_db.commit()

    res = check_duplicate_document(test_db, file_hash=DOC_HASH)
    assert res["is_duplicate"] is True
    assert res["duplicate_type"] == "DOCUMENT_HASH_MATCH"
    assert res["match_count"] >= 1
    assert res["existing_document_id"] == doc.id


def test_document_hash_no_duplicate(test_db, sample_warranty, customer_user):
    """A unique hash must not be reported as a duplicate."""
    claim = _seed_claim(test_db, sample_warranty, customer_user)
    doc = Document(
        claim_id=claim.id,
        uploader_id=customer_user.id,
        document_type="purchase_invoice",
        file_path="/tmp/invoice-2.pdf",
        file_size=1024,
        mime_type="application/pdf",
        file_hash="a" * 64,
    )
    test_db.add(doc)
    test_db.commit()

    res = check_duplicate_document(test_db, file_hash="b" * 64)
    assert res["is_duplicate"] is False
    assert res["match_count"] == 0
