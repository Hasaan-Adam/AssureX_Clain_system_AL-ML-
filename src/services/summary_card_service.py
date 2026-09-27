"""AssureX Claim Summary Card Service.

Provides high-level services for dynamically rendering, saving, and encoding
Claim Summary Card images for single claims using the PIL renderer engine,
as well as preparing summary card metadata dictionaries.
"""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from PIL import Image

from src.card.renderer import (
    DEFAULT_HEIGHT,
    DEFAULT_THEME,
    DEFAULT_WIDTH,
    render_claim_card,
    save_claim_card,
)

CARDS_OUTPUT_DIR = Path("data/cards/temp")


def render_summary_card_image(
    claim_data: Dict[str, Any],
    theme: Optional[Dict[str, Any]] = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    font_family: Optional[str] = None,
) -> Image.Image:
    """Renders a PIL Image representing the Claim Summary Card.

    Args:
        claim_data: Dictionary containing factual claim fields.
        theme: Optional visual theme dict.
        width: Image width in pixels.
        height: Image height in pixels.
        font_family: Optional custom font name.

    Returns:
        PIL.Image in RGB mode.
    """
    return render_claim_card(
        claim=claim_data,
        theme=theme,
        width=width,
        height=height,
        font_family=font_family,
    )


def render_card_bytes(
    claim_data: Dict[str, Any],
    theme: Optional[Dict[str, Any]] = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    image_format: str = "PNG",
) -> bytes:
    """Renders the summary card and returns raw image bytes."""
    img = render_summary_card_image(claim_data, theme=theme, width=width, height=height)
    buf = io.BytesIO()
    img.save(buf, format=image_format, optimize=True)
    return buf.getvalue()


def generate_summary_card_base64(
    claim_data: Dict[str, Any],
    theme: Optional[Dict[str, Any]] = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    include_prefix: bool = True,
) -> str:
    """Renders the summary card and returns a base64 encoded string.

    Args:
        claim_data: Dictionary containing claim data.
        theme: Optional theme configuration.
        width: Card width in pixels.
        height: Card height in pixels.
        include_prefix: If True, prefixes with 'data:image/png;base64,'.

    Returns:
        Base64 encoded string.
    """
    img_bytes = render_card_bytes(claim_data, theme=theme, width=width, height=height)
    b64_str = base64.b64encode(img_bytes).decode("utf-8")
    if include_prefix:
        return f"data:image/png;base64,{b64_str}"
    return b64_str


def generate_summary_card(
    claim_data: Dict[str, Any],
    output_path: Optional[Union[str, Path]] = None,
    theme: Optional[Dict[str, Any]] = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> Path:
    """Generates and saves the Claim Summary Card to disk.

    Args:
        claim_data: Dictionary containing claim data.
        output_path: Optional destination file path. If None, saves to data/cards/temp/{claim_id}.png.
        theme: Optional styling theme.
        width: Canvas width in pixels.
        height: Canvas height in pixels.

    Returns:
        Path to the saved image file.
    """
    if output_path is None:
        claim_id = str(claim_data.get("claim_id", claim_data.get("claim_number", "CLM_TEMP"))).replace("/", "_")
        CARDS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = CARDS_OUTPUT_DIR / f"{claim_id}.png"
    else:
        output_path = Path(output_path)

    return save_claim_card(
        claim=claim_data,
        output_path=output_path,
        theme=theme,
        width=width,
        height=height,
    )


def build_summary_card_data(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Constructs summary card dictionary suitable for frontend card components."""
    return {
        "claim_number": claim_data.get("claim_number", claim_data.get("claim_id", "CLM-UNKNOWN")),
        "product_title": f"{claim_data.get('brand', '')} {claim_data.get('product_name', '')}".strip(),
        "serial_number": claim_data.get("serial_number", "N/A"),
        "fault_type": claim_data.get("fault_type", "General Defect"),
        "status": claim_data.get("status", "submitted"),
        "adjudication_decision": claim_data.get("ai_decision", "PENDING"),
        "confidence_badge": f"{(claim_data.get('ai_confidence', 0.90) * 100):.0f}%",
        "fraud_risk_level": "HIGH" if claim_data.get("fraud_score", 0.0) >= 0.70 else ("MEDIUM" if claim_data.get("fraud_score", 0.0) >= 0.30 else "LOW"),
    }