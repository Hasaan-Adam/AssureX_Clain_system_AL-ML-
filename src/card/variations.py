"""AssureX Claim Summary Card Variations & Augmentations.

Generates visually distinct variations of Claim Summary Cards for computer vision
data augmentation. Variations alter color palettes, background tints, font styling,
and visual contrast while strictly preserving the underlying factual claim data.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image

from src.card.renderer import DEFAULT_HEIGHT, DEFAULT_WIDTH, render_claim_card

# Predefined high-quality visual style themes for variations
VARIATION_THEMES: List[Dict[str, Any]] = [
    # Theme 1: Cool Indigo / Azure
    {
        "name": "cool_indigo",
        "canvas_bg": (238, 242, 255),       # indigo-50
        "card_bg": (255, 255, 255),         # white
        "card_border": (199, 210, 254),     # indigo-200
        "header_bg": (30, 27, 75),          # indigo-950
        "header_title": (238, 242, 255),    # indigo-50
        "header_sub": (165, 180, 252),      # indigo-300
        "section_bg": (245, 247, 255),      # indigo-50/white
        "section_border": (224, 231, 255),  # indigo-100
        "section_title": (49, 46, 129),      # indigo-900
        "text_primary": (30, 27, 75),       # indigo-950
        "text_secondary": (67, 56, 202),    # indigo-700
        "text_muted": (99, 102, 241),       # indigo-500
        "badge_yes_bg": (209, 250, 229),    # emerald-100
        "badge_yes_fg": (6, 95, 70),        # emerald-800
        "badge_no_bg": (255, 228, 230),     # rose-100
        "badge_no_fg": (159, 18, 57),       # rose-800
        "badge_neutral_bg": (224, 231, 255),# indigo-100
        "badge_neutral_fg": (55, 48, 163),  # indigo-800
        "badge_warn_bg": (254, 243, 199),   # amber-100
        "badge_warn_fg": (146, 64, 14),     # amber-800
        "footer_text": (129, 140, 248),     # indigo-400
        "font_family": "segoeui.ttf",
    },
    # Theme 2: Warm Amber / Sand
    {
        "name": "warm_amber",
        "canvas_bg": (254, 243, 199),       # amber-100
        "card_bg": (255, 253, 247),         # warm white
        "card_border": (253, 230, 138),     # amber-200
        "header_bg": (69, 26, 3),           # amber-950
        "header_title": (254, 243, 199),    # amber-100
        "header_sub": (252, 211, 77),       # amber-300
        "section_bg": (255, 251, 235),      # amber-50
        "section_border": (253, 230, 138),  # amber-200
        "section_title": (120, 53, 15),     # amber-900
        "text_primary": (69, 26, 3),        # amber-950
        "text_secondary": (146, 64, 14),    # amber-800
        "text_muted": (180, 83, 9),         # amber-700
        "badge_yes_bg": (220, 252, 231),    # green-100
        "badge_yes_fg": (20, 83, 45),       # green-900
        "badge_no_bg": (254, 226, 226),     # red-100
        "badge_no_fg": (127, 29, 29),       # red-900
        "badge_neutral_bg": (254, 243, 199),# amber-100
        "badge_neutral_fg": (146, 64, 14),  # amber-800
        "badge_warn_bg": (254, 240, 138),   # yellow-200
        "badge_warn_fg": (133, 77, 14),     # yellow-800
        "footer_text": (180, 83, 9),        # amber-700
        "font_family": "calibri.ttf",
    },
    # Theme 3: Emerald Sage
    {
        "name": "emerald_sage",
        "canvas_bg": (236, 253, 245),       # emerald-50
        "card_bg": (255, 255, 255),         # white
        "card_border": (167, 243, 208),     # emerald-200
        "header_bg": (6, 78, 59),           # emerald-900
        "header_title": (240, 253, 244),    # emerald-50
        "header_sub": (110, 231, 183),      # emerald-300
        "section_bg": (240, 253, 244),      # emerald-50
        "section_border": (187, 247, 208),  # emerald-100
        "section_title": (4, 120, 87),       # emerald-700
        "text_primary": (6, 78, 59),        # emerald-900
        "text_secondary": (4, 120, 87),      # emerald-700
        "text_muted": (16, 185, 129),       # emerald-500
        "badge_yes_bg": (209, 250, 229),    # emerald-100
        "badge_yes_fg": (6, 95, 70),        # emerald-800
        "badge_no_bg": (254, 226, 226),     # red-100
        "badge_no_fg": (153, 27, 27),       # red-800
        "badge_neutral_bg": (209, 250, 229),# emerald-100
        "badge_neutral_fg": (6, 95, 70),    # emerald-800
        "badge_warn_bg": (254, 240, 138),   # yellow-200
        "badge_warn_fg": (133, 77, 14),     # yellow-800
        "footer_text": (52, 211, 153),      # emerald-400
        "font_family": "arial.ttf",
    },
    # Theme 4: High Contrast Graphite
    {
        "name": "graphite_contrast",
        "canvas_bg": (229, 231, 235),       # gray-200
        "card_bg": (255, 255, 255),         # white
        "card_border": (156, 163, 175),     # gray-400
        "header_bg": (24, 24, 27),          # zinc-900
        "header_title": (250, 250, 250),    # zinc-50
        "header_sub": (161, 161, 170),      # zinc-400
        "section_bg": (244, 244, 245),      # zinc-100
        "section_border": (212, 212, 216),  # zinc-300
        "section_title": (9, 9, 11),        # zinc-950
        "text_primary": (9, 9, 11),         # zinc-950
        "text_secondary": (39, 39, 42),     # zinc-800
        "text_muted": (82, 82, 91),         # zinc-600
        "badge_yes_bg": (187, 247, 208),    # green-200
        "badge_yes_fg": (20, 83, 45),       # green-900
        "badge_no_bg": (254, 202, 202),     # red-200
        "badge_no_fg": (136, 19, 55),       # rose-900
        "badge_neutral_bg": (228, 228, 231),# zinc-200
        "badge_neutral_fg": (39, 39, 42),   # zinc-800
        "badge_warn_bg": (254, 240, 138),   # yellow-200
        "badge_warn_fg": (133, 77, 14),     # yellow-800
        "footer_text": (113, 113, 122),     # zinc-500
        "font_family": "arial.ttf",
    },
]


def get_variation_theme(variation_index: int) -> Dict[str, Any]:
    """Retrieve theme dictionary for a given variation index."""
    idx = (variation_index - 1) % len(VARIATION_THEMES)
    return VARIATION_THEMES[idx]


def render_card_variation(
    claim: Dict[str, Any],
    variation_index: int = 1,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> Image.Image:
    """Render a styled variation of a Claim Summary Card."""
    theme = get_variation_theme(variation_index)
    font_fam = theme.get("font_family")
    return render_claim_card(claim, theme=theme, width=width, height=height, font_family=font_fam)


def generate_card_variations(
    claim: Dict[str, Any],
    n_variations: int = 2,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> List[Image.Image]:
    """Generate n variations for a single claim record."""
    return [
        render_card_variation(claim, variation_index=i + 1, width=width, height=height)
        for i in range(n_variations)
    ]


def save_card_variations(
    claim: Dict[str, Any],
    target_dir: str | Path,
    claim_id: str,
    n_variations: int = 2,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> List[Path]:
    """Render and save multiple variations of a claim card to the target directory."""
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    saved_paths: List[Path] = []
    for i in range(1, n_variations + 1):
        out_file = target_path / f"{claim_id}_var{i}.png"
        theme = get_variation_theme(i)
        font_fam = theme.get("font_family")
        img = render_claim_card(claim, theme=theme, width=width, height=height, font_family=font_fam)
        img.save(out_file, format="PNG", optimize=True)
        saved_paths.append(out_file)

    return saved_paths