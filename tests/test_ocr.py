"""
Unit and API Integration tests for OCR extraction and structured entity parsing.
"""

from io import BytesIO
from PIL import Image
import pytest
from src.services.extraction_service import extract_entities_from_text
from src.services.ocr_service import perform_ocr_on_image


def test_perform_ocr_fallback():
    """Test OCR execution with generated synthetic image."""
    img = Image.new("RGB", (200, 100), color=(255, 255, 255))
    buf = BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    result = perform_ocr_on_image(img_bytes)
    assert "text" in result
    assert "confidence" in result
    assert result["confidence"] >= 0.0


def test_extract_entities_from_receipt_text():
    """Test entity extractor on simulated invoice string."""
    receipt_text = """
    BEST BUY #1024
    Date: 2024-05-13
    Invoice: INV-984830
    Product: Dell XPS 15 (DE926-ELE)
    Serial: ELC-DEL-984830
    Total: $1,499.99
    """
    entities = extract_entities_from_text(receipt_text)
    assert entities["purchase_date"] == "2024-05-13"
    assert entities["purchase_price"] == 1499.99
    assert entities["serial_number"] == "ELC-DEL-984830"
    assert entities["retailer"] == "Best Buy"
    assert entities["extraction_confidence"] > 0.5