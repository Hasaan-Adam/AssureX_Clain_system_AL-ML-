"""
AssureX Claim Engine - OCR Document Processing Service
Extracts raw text and confidence scores from uploaded images and invoices using pytesseract with fallback.
"""

from io import BytesIO
import logging
from pathlib import Path
import re
from typing import Any, Dict, Optional
from PIL import Image
from sqlalchemy.orm import Session

from src.models.document import Document

logger = logging.getLogger(__name__)


_rapid_ocr = None


def get_rapid_ocr():
    global _rapid_ocr
    if _rapid_ocr is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            _rapid_ocr = RapidOCR()
        except Exception as e:
            logger.warning(f"Could not initialize RapidOCR: {e}")
            _rapid_ocr = False
    return _rapid_ocr if _rapid_ocr is not False else None


def perform_ocr_on_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Execute OCR on raw image bytes.
    Uses RapidOCR (ONNX Runtime) as primary engine, pytesseract as secondary.
    """
    try:
        image = Image.open(BytesIO(image_bytes))
        width, height = image.size
    except Exception as e:
        logger.warning(f"Could not open image bytes: {e}")
        return {
            "text": "",
            "confidence": 0.0,
            "metadata": {"error": "Invalid image data"},
        }

    extracted_text = ""
    confidence = 0.0
    engine_used = "none"

    ocr_engine = get_rapid_ocr()
    if ocr_engine:
        try:
            import numpy as np
            image_np = np.array(image.convert("RGB"))
            result, _ = ocr_engine(image_np)
            if result:
                lines = [item[1] for item in result if item[1]]
                confs = [float(item[2]) for item in result if len(item) > 2 and item[2] is not None]
                extracted_text = "\n".join(lines).strip()
                confidence = round(sum(confs) / len(confs), 3) if confs else 0.85
                engine_used = "RapidOCR-ONNX"
        except Exception as e:
            logger.warning(f"RapidOCR error: {e}")

    if not extracted_text:
        try:
            import pytesseract
            extracted_text = pytesseract.image_to_string(image).strip()
            if extracted_text:
                confidence = 0.82
                engine_used = "pytesseract"
        except Exception as e:
            logger.info(f"Pytesseract not available or errored: {e}")

    return {
        "text": extracted_text,
        "confidence": confidence if extracted_text else 0.0,
        "metadata": {
            "image_width": width,
            "image_height": height,
            "engine": engine_used,
        },
    }


def process_document_ocr(db: Session, document_id: int) -> Document:
    """
    Load document file from disk, run OCR extraction, and persist results to Document record.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise ValueError(f"Document with ID {document_id} not found.")

    file_path = Path(document.file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Document file not found at {file_path}")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    ocr_result = perform_ocr_on_image(file_bytes)

    entities: Dict[str, Any] = {}
    if ocr_result.get("text"):
        from src.services.extraction_service import extract_entities_from_text

        entities = extract_entities_from_text(ocr_result["text"])

    document.apply_ocr_result(
        text=ocr_result["text"],
        confidence=ocr_result["confidence"],
        metadata=ocr_result["metadata"],
        entities=entities,
    )

    db.commit()
    db.refresh(document)
    return document