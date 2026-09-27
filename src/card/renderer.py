"""AssureX Claim Summary Card Renderer.

Renders high-quality visual Claim Summary Cards using Pillow (PIL).
Each card visually encapsulates raw factual information about a warranty claim:
product metadata, purchase history, warranty coverage, fault details, repair history,
document evidence checklist, and integrity signals.

CRITICAL REQUIREMENT:
Never render the target label/prediction or confidence scores on the summary card.
The card must only contain raw claim facts for machine vision analysis.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

# Canvas dimensions
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

# Color Palette Defaults (Classic Slate)
DEFAULT_THEME: Dict[str, Any] = {
    "name": "classic_slate",
    "canvas_bg": (241, 245, 249),       # slate-100
    "card_bg": (255, 255, 255),         # white
    "card_border": (203, 213, 225),     # slate-300
    "header_bg": (15, 23, 42),          # slate-900
    "header_title": (255, 255, 255),    # white
    "header_sub": (148, 163, 184),      # slate-400
    "section_bg": (248, 250, 252),      # slate-50
    "section_border": (226, 232, 240),  # slate-200
    "section_title": (30, 41, 59),      # slate-800
    "text_primary": (15, 23, 42),       # slate-900
    "text_secondary": (71, 85, 105),    # slate-600
    "text_muted": (100, 116, 139),      # slate-500
    "badge_yes_bg": (220, 252, 231),    # green-100
    "badge_yes_fg": (22, 101, 52),      # green-800
    "badge_no_bg": (254, 226, 226),     # red-100
    "badge_no_fg": (153, 27, 27),       # red-800
    "badge_neutral_bg": (226, 232, 240),# slate-200
    "badge_neutral_fg": (51, 65, 85),   # slate-700
    "badge_warn_bg": (254, 240, 138),   # yellow-200
    "badge_warn_fg": (133, 77, 14),     # yellow-800
    "footer_text": (148, 163, 184),     # slate-400
}

# Forbidden keys that must never be rendered
FORBIDDEN_FIELDS = {
    "label",
    "target",
    "scenario",
    "prediction",
    "predicted_label",
    "confidence",
    "score",
    "prediction_status",
    "model_decision",
}


def _resolve_color(c: Any) -> Any:
    if isinstance(c, str):
        if c.startswith("#"):
            return _hex_to_rgb(c)
        return c
    if isinstance(c, (tuple, list)) and len(c) in (3, 4):
        return tuple(c)
    return c


def get_font(size: int, bold: bool = False, mono: bool = False, font_family: Optional[str] = None) -> ImageFont.ImageFont:
    """Load a TrueType font with fallbacks."""
    candidates = []
    if font_family:
        candidates.append(font_family)

    if mono:
        candidates.extend(["consola.ttf", "consolab.ttf" if bold else "consola.ttf", "cour.ttf", "DejaVuSansMono.ttf"])
    elif bold:
        candidates.extend(["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf", "DejaVuSans-Bold.ttf"])
    else:
        candidates.extend(["segoeui.ttf", "arial.ttf", "calibri.ttf", "DejaVuSans.ttf"])

    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
        # Check standard Windows Font path
        win_path = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", candidate)
        if os.path.exists(win_path):
            try:
                return ImageFont.truetype(win_path, size)
            except Exception:
                pass

    return ImageFont.load_default()


def _sanitize_claim(claim: Dict[str, Any]) -> Dict[str, Any]:
    """Strip target predictions and scenario names to prevent label leakage."""
    return {k: v for k, v in claim.items() if k.lower() not in FORBIDDEN_FIELDS}


def _format_val(val: Any) -> str:
    """Format a value cleanly for card display."""
    if val is None or val == "":
        return "N/A"
    if isinstance(val, bool):
        return "YES" if val else "NO"
    return str(val).strip()


def _draw_badge(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[int, int, int, int],
    text: str,
    bg_color: Tuple[int, int, int],
    fg_color: Tuple[int, int, int],
    font: ImageFont.ImageFont,
    radius: int = 4,
) -> None:
    """Draw a compact pill badge with centered text."""
    draw.rounded_rectangle(xy, radius=radius, fill=bg_color)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    bx = xy[0] + (xy[2] - xy[0] - tw) // 2
    by = xy[1] + (xy[3] - xy[1] - th) // 2 - 1
    draw.text((bx, by), text, fill=fg_color, font=font)


def render_claim_card(
    claim: Dict[str, Any],
    theme: Optional[Dict[str, Any]] = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    font_family: Optional[str] = None,
) -> Image.Image:
    """Render a visual Claim Summary Card image from raw claim data.

    Parameters:
        claim: Dictionary with claim metadata and factual fields.
        theme: Optional theme dictionary overriding colors.
        width: Canvas width in pixels (default 800).
        height: Canvas height in pixels (default 600).
        font_family: Optional custom font name/file.

    Returns:
        PIL.Image in RGB mode.
    """
    # Strict sanitization
    data = _sanitize_claim(claim)

    # Merge theme with default
    t = {**DEFAULT_THEME, **(theme or {})}
    for k in t:
        if k != "name" and isinstance(t[k], (tuple, list, str)):
            t[k] = _resolve_color(t[k])

    # Initialize canvas
    img = Image.new("RGB", (width, height), color=t["canvas_bg"])
    draw = ImageDraw.Draw(img)

    # Fonts
    font_header_title = get_font(18, bold=True, font_family=font_family)
    font_header_sub = get_font(11, bold=False, font_family=font_family)
    font_header_badge = get_font(10, bold=True, mono=True, font_family=font_family)
    font_section_title = get_font(11, bold=True, font_family=font_family)
    font_label = get_font(10, bold=True, font_family=font_family)
    font_val = get_font(10, bold=False, font_family=font_family)
    font_badge = get_font(9, bold=True, font_family=font_family)
    font_doc_title = get_font(9, bold=True, font_family=font_family)
    font_doc_stat = get_font(9, bold=False, font_family=font_family)
    font_footer = get_font(9, bold=False, font_family=font_family)

    # Outer Card Box
    margin_x, margin_y = 16, 14
    card_x1, card_y1 = margin_x, margin_y
    card_x2, card_y2 = width - margin_x, height - margin_y
    draw.rounded_rectangle(
        (card_x1, card_y1, card_x2, card_y2),
        radius=10,
        fill=t["card_bg"],
        outline=t["card_border"],
        width=1,
    )

    # Header Bar
    header_h = 60
    draw.rounded_rectangle(
        (card_x1, card_y1, card_x2, card_y1 + header_h),
        radius=10,
        fill=t["header_bg"],
    )
    # Square off bottom of header inside card
    draw.rectangle(
        (card_x1, card_y1 + header_h - 10, card_x2, card_y1 + header_h),
        fill=t["header_bg"],
    )

    # Header Text
    claim_id = _format_val(data.get("claim_id", "CLM-UNKNOWN"))
    sub_date = _format_val(data.get("claim_submission_date", "YYYY-MM-DD"))
    user_id = _format_val(data.get("user_id", "N/A"))

    draw.text((card_x1 + 18, card_y1 + 10), "ASSUREX CLAIM SUMMARY", fill=t["header_title"], font=font_header_title)
    header_sub_str = f"Claim ID: {claim_id}   |   Submission Date: {sub_date}   |   Claimant: {user_id}"
    draw.text((card_x1 + 18, card_y1 + 36), header_sub_str, fill=t["header_sub"], font=font_header_sub)

    # Header Badge (OCR / Verification Status)
    ocr_quality = str(data.get("ocr_quality", "high")).upper()
    ocr_bg = t["badge_yes_bg"] if ocr_quality == "HIGH" else (t["badge_warn_bg"] if ocr_quality == "MEDIUM" else t["badge_no_bg"])
    ocr_fg = t["badge_yes_fg"] if ocr_quality == "HIGH" else (t["badge_warn_fg"] if ocr_quality == "MEDIUM" else t["badge_no_fg"])
    _draw_badge(
        draw,
        (card_x2 - 120, card_y1 + 16, card_x2 - 16, card_y1 + 42),
        f"OCR: {ocr_quality}",
        ocr_bg,
        ocr_fg,
        font_header_badge,
        radius=4,
    )

    # Section Grid Coordinates
    content_y = card_y1 + header_h + 10
    col_w = (card_x2 - card_x1 - 32) // 2  # Width of each 2-column box
    col1_x1 = card_x1 + 12
    col1_x2 = col1_x1 + col_w
    col2_x1 = col1_x2 + 8
    col2_x2 = card_x2 - 12

    # Section 1: Product & Purchase (Row 1 Left)
    sec1_y1 = content_y
    sec1_y2 = sec1_y1 + 152
    draw.rounded_rectangle((col1_x1, sec1_y1, col1_x2, sec1_y2), radius=6, fill=t["section_bg"], outline=t["section_border"], width=1)
    draw.text((col1_x1 + 10, sec1_y1 + 8), "1. PRODUCT & PURCHASE INFORMATION", fill=t["section_title"], font=font_section_title)

    prod_name = _format_val(data.get("product_name"))
    category = _format_val(data.get("product_category"))
    brand = _format_val(data.get("brand"))
    model = _format_val(data.get("model_number"))
    serial = _format_val(data.get("serial_number"))
    serial_status = str(data.get("serial_status", "match")).lower()
    price = data.get("purchase_price")
    price_str = f"PKR {int(price):,}" if price is not None and str(price).isdigit() else _format_val(price)
    p_date = _format_val(data.get("purchase_date"))
    p_age = _format_val(data.get("product_age_days"))
    retailer = _format_val(data.get("retailer"))

    fields_s1 = [
        ("Product / Brand:", f"{prod_name}  ({brand})"),
        ("Category / Model:", f"{category}  [{model}]"),
        ("Serial Number:", f"{serial}"),
        ("Purchase Date:", f"{p_date}  (Age: {p_age} days)"),
        ("Retailer / Price:", f"{retailer}  |  {price_str}"),
    ]
    cur_y = sec1_y1 + 28
    for lbl, val in fields_s1:
        draw.text((col1_x1 + 10, cur_y), lbl, fill=t["text_secondary"], font=font_label)
        draw.text((col1_x1 + 125, cur_y), val, fill=t["text_primary"], font=font_val)
        cur_y += 20

    # Serial Status Pill in Section 1
    s_bg = t["badge_yes_bg"] if serial_status == "match" else (t["badge_no_bg"] if serial_status == "mismatch" else t["badge_neutral_bg"])
    s_fg = t["badge_yes_fg"] if serial_status == "match" else (t["badge_no_fg"] if serial_status == "mismatch" else t["badge_neutral_fg"])
    _draw_badge(draw, (col1_x2 - 110, sec1_y1 + 6, col1_x2 - 8, sec1_y1 + 24), f"Serial: {serial_status.upper()}", s_bg, s_fg, font_badge)

    # Section 2: Warranty Status & Coverage (Row 1 Right)
    sec2_y1 = content_y
    sec2_y2 = sec2_y1 + 152
    draw.rounded_rectangle((col2_x1, sec2_y1, col2_x2, sec2_y2), radius=6, fill=t["section_bg"], outline=t["section_border"], width=1)
    draw.text((col2_x1 + 10, sec2_y1 + 8), "2. WARRANTY COVERAGE & VALIDITY", fill=t["section_title"], font=font_section_title)

    w_type = _format_val(data.get("warranty_type"))
    w_dur = _format_val(data.get("warranty_duration_months"))
    w_start = _format_val(data.get("warranty_start_date"))
    w_exp = _format_val(data.get("warranty_expiry_date"))
    rem_days = _format_val(data.get("remaining_warranty_days"))
    w_active = str(data.get("warranty_active", "no")).lower()
    pop = str(data.get("proof_of_purchase", "no")).lower()

    fields_s2 = [
        ("Warranty Plan:", f"{w_type.title()} ({w_dur} Months Duration)"),
        ("Coverage Dates:", f"{w_start}  to  {w_exp}"),
        ("Remaining Days:", f"{rem_days} days (from claim date)"),
        ("Warranty Active:", f"{w_active.upper()}"),
        ("Proof of Purchase:", f"{pop.upper()} (Valid Receipt Verified)"),
    ]
    cur_y = sec2_y1 + 28
    for lbl, val in fields_s2:
        draw.text((col2_x1 + 10, cur_y), lbl, fill=t["text_secondary"], font=font_label)
        # Highlight active status
        if "Active:" in lbl:
            fg = t["badge_yes_fg"] if w_active == "yes" else t["badge_no_fg"]
            draw.text((col2_x1 + 130, cur_y), val, fill=fg, font=font_label)
        elif "Proof" in lbl:
            fg = t["badge_yes_fg"] if pop == "yes" else t["badge_no_fg"]
            draw.text((col2_x1 + 130, cur_y), val, fill=fg, font=font_val)
        else:
            draw.text((col2_x1 + 130, cur_y), val, fill=t["text_primary"], font=font_val)
        cur_y += 20

    # Warranty Status Pill in Section 2
    if w_active == "yes":
        w_badge_text = "ACTIVE"
    else:
        try:
            w_badge_text = "EXPIRED" if int(rem_days) < 0 else "INACTIVE"
        except Exception:
            w_badge_text = "INACTIVE"
    w_bg = t["badge_yes_bg"] if w_active == "yes" else t["badge_no_bg"]
    w_fg = t["badge_yes_fg"] if w_active == "yes" else t["badge_no_fg"]
    _draw_badge(draw, (col2_x2 - 100, sec2_y1 + 6, col2_x2 - 8, sec2_y1 + 24), f"WTY: {w_badge_text}", w_bg, w_fg, font_badge)

    # Section 3: Fault Details & Incident Timeline (Row 2 Left)
    sec3_y1 = sec1_y2 + 8
    sec3_y2 = sec3_y1 + 160
    draw.rounded_rectangle((col1_x1, sec3_y1, col1_x2, sec3_y2), radius=6, fill=t["section_bg"], outline=t["section_border"], width=1)
    draw.text((col1_x1 + 10, sec3_y1 + 8), "3. FAULT & INCIDENT DETAILS", fill=t["section_title"], font=font_section_title)

    fault_type = _format_val(data.get("fault_type"))
    damage_type = _format_val(data.get("damage_type"))
    f_date = _format_val(data.get("fault_occurrence_date"))
    rep_days = _format_val(data.get("claim_reporting_days"))
    rep_limit = _format_val(data.get("reporting_deadline_days", "30"))
    within_rep = str(data.get("within_reporting_period", "yes")).lower()
    covered = str(data.get("covered_fault", "yes")).lower()
    excluded = str(data.get("excluded_damage", "no")).lower()
    fault_desc = _format_val(data.get("fault_description", "None provided."))

    fields_s3 = [
        ("Fault Category:", f"{fault_type}"),
        ("Damage Nature:", f"{damage_type} (Excluded: {excluded.upper()})"),
        ("Incident Date:", f"{f_date}"),
        ("Report Lag:", f"{rep_days} days (Policy Window: {rep_limit}d) - {'OK' if within_rep == 'yes' else 'LATE'}"),
        ("Covered Fault:", f"{covered.upper()}"),
    ]
    cur_y = sec3_y1 + 28
    for lbl, val in fields_s3:
        draw.text((col1_x1 + 10, cur_y), lbl, fill=t["text_secondary"], font=font_label)
        draw.text((col1_x1 + 125, cur_y), val, fill=t["text_primary"], font=font_val)
        cur_y += 19

    # Wrapped Fault Description
    desc_label = "Description:"
    draw.text((col1_x1 + 10, cur_y + 1), desc_label, fill=t["text_secondary"], font=font_label)
    # Simple line wrap for description
    desc_clean = fault_desc.replace("\n", " ")
    if len(desc_clean) > 42:
        d1 = desc_clean[:42]
        d2 = desc_clean[42:85]
        draw.text((col1_x1 + 125, cur_y + 1), d1, fill=t["text_muted"], font=font_val)
        draw.text((col1_x1 + 125, cur_y + 15), d2, fill=t["text_muted"], font=font_val)
    else:
        draw.text((col1_x1 + 125, cur_y + 1), desc_clean, fill=t["text_muted"], font=font_val)

    # Section 4: Repair History & Integrity Checks (Row 2 Right)
    sec4_y1 = sec2_y2 + 8
    sec4_y2 = sec4_y1 + 160
    draw.rounded_rectangle((col2_x1, sec4_y1, col2_x2, sec4_y2), radius=6, fill=t["section_bg"], outline=t["section_border"], width=1)
    draw.text((col2_x1 + 10, sec4_y1 + 8), "4. REPAIR HISTORY & INTEGRITY SIGNALS", fill=t["section_title"], font=font_section_title)

    rep_count = _format_val(data.get("repair_history_count", "0"))
    rep_auth = _format_val(data.get("repair_authorized", "none"))
    last_rep = _format_val(data.get("last_repair_date"))
    prev_repl = str(data.get("previous_replacement", "no")).lower()
    has_contr = str(data.get("has_contradiction", "no")).lower()
    contr_type = _format_val(data.get("contradiction_type", "none"))
    is_dup = str(data.get("is_duplicate", "no")).lower()

    fields_s4 = [
        ("Prior Repair Count:", f"{rep_count} repair(s) logged"),
        ("Repair Authorization:", f"{rep_auth.upper()} (Last: {last_rep})"),
        ("Prior Unit Replaced:", f"{prev_repl.upper()}"),
        ("Data Contradiction:", f"{has_contr.upper()} (Type: {contr_type})"),
        ("Duplicate Detection:", f"{is_dup.upper()}"),
        ("Integrity Scan:", f"OCR {ocr_quality} | Serial: {serial_status}"),
    ]
    cur_y = sec4_y1 + 28
    for lbl, val in fields_s4:
        draw.text((col2_x1 + 10, cur_y), lbl, fill=t["text_secondary"], font=font_label)
        if "Contradiction:" in lbl and has_contr == "yes":
            draw.text((col2_x1 + 130, cur_y), val, fill=t["badge_no_fg"], font=font_label)
        elif "Duplicate:" in lbl and is_dup == "yes":
            draw.text((col2_x1 + 130, cur_y), val, fill=t["badge_no_fg"], font=font_label)
        else:
            draw.text((col2_x1 + 130, cur_y), val, fill=t["text_primary"], font=font_val)
        cur_y += 19

    # Section 5: Document Verification Checklist (Row 3 Full Width)
    sec5_y1 = sec3_y2 + 8
    sec5_y2 = sec5_y1 + 100
    sec5_x1 = card_x1 + 12
    sec5_x2 = card_x2 - 12
    draw.rounded_rectangle((sec5_x1, sec5_y1, sec5_x2, sec5_y2), radius=6, fill=t["section_bg"], outline=t["section_border"], width=1)
    
    mand_complete = str(data.get("mandatory_docs_complete", "yes")).lower()
    missing_cnt = _format_val(data.get("missing_document_count", "0"))
    draw.text((sec5_x1 + 10, sec5_y1 + 8), "5. EVIDENCE & DOCUMENT VERIFICATION CHECKLIST", fill=t["section_title"], font=font_section_title)
    
    # Mandatory complete badge
    m_bg = t["badge_yes_bg"] if mand_complete == "yes" else t["badge_no_bg"]
    m_fg = t["badge_yes_fg"] if mand_complete == "yes" else t["badge_no_fg"]
    m_txt = "ALL MANDATORY DOCS PRESENT" if mand_complete == "yes" else f"MISSING DOCS: {missing_cnt}"
    _draw_badge(draw, (sec5_x2 - 210, sec5_y1 + 6, sec5_x2 - 8, sec5_y1 + 24), m_txt, m_bg, m_fg, font_badge)

    # Document Chips Checklist
    doc_items = [
        ("Receipt", str(data.get("receipt_available", "no")).lower() == "yes"),
        ("Warranty Card", str(data.get("warranty_card_available", "no")).lower() == "yes"),
        ("Product Photo", str(data.get("product_image_available", "no")).lower() == "yes"),
        ("Serial Proof", str(data.get("serial_evidence_available", "no")).lower() == "yes"),
        ("Fault Proof", str(data.get("fault_evidence_available", "no")).lower() == "yes"),
        ("Repair Report", str(data.get("repair_report_available", "no")).lower() == "yes"),
    ]

    total_doc_w = sec5_x2 - sec5_x1 - 20
    chip_gap = 6
    chip_w = (total_doc_w - (chip_gap * 5)) // 6
    chip_h = 52
    chip_y = sec5_y1 + 34

    for idx, (doc_name, is_avail) in enumerate(doc_items):
        cx1 = sec5_x1 + 10 + idx * (chip_w + chip_gap)
        cx2 = cx1 + chip_w
        cy1 = chip_y
        cy2 = cy1 + chip_h

        c_bg = t["badge_yes_bg"] if is_avail else t["badge_no_bg"]
        c_fg = t["badge_yes_fg"] if is_avail else t["badge_no_fg"]
        c_border = (187, 247, 208) if is_avail else (254, 202, 202)

        draw.rounded_rectangle((cx1, cy1, cx2, cy2), radius=4, fill=t["card_bg"], outline=c_border, width=1)
        # Inner mini-banner
        draw.rounded_rectangle((cx1 + 2, cy1 + 2, cx2 - 2, cy1 + 20), radius=2, fill=c_bg)
        stat_text = "[ OK ]" if is_avail else "[ MISSING ]"
        _draw_badge(draw, (cx1 + 4, cy1 + 3, cx2 - 4, cy1 + 19), stat_text, c_bg, c_fg, font_doc_stat)

        # Label below
        tb = draw.textbbox((0, 0), doc_name, font=font_doc_title)
        tw = tb[2] - tb[0]
        tx = cx1 + (chip_w - tw) // 2
        draw.text((tx, cy1 + 27), doc_name, fill=t["text_primary"], font=font_doc_title)

    # Footer
    footer_text = "AssureX Claim Intelligence System  •  Standardized Claim Summary Record  •  Computer Vision Input"
    draw.text((card_x1 + 16, card_y2 - 18), footer_text, fill=t["footer_text"], font=font_footer)

    return img


def save_claim_card(
    claim: Dict[str, Any],
    output_path: str | Path,
    theme: Optional[Dict[str, Any]] = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    font_family: Optional[str] = None,
) -> Path:
    """Render and save a Claim Summary Card image to disk."""
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    img = render_claim_card(claim, theme=theme, width=width, height=height, font_family=font_family)
    img.save(out_file, format="PNG", optimize=True)
    return out_file