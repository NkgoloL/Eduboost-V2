"""
app/modules/diagnostics/irt_params.py
─────────────────────────────────────────────────────────────────────────────
Phase 3: IRT Parameter Assignment (P3-09, P3-10)

Provides logic for assigning initial IRT parameters (a, b, c) to items
based on their difficulty band and type.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

# Difficulty band → b-parameter midpoint
BAND_MIDPOINTS = {
    "easy":        -1.5,
    "moderate":    -0.5,
    "on_level":     0.5,
    "challenging":  1.5,
}

# Difficulty band → b bounds (for clamping)
BAND_BOUNDS = {
    "easy":        (-3.0, -1.0),
    "moderate":    (-1.0,  0.0),
    "on_level":    ( 0.0,  1.0),
    "challenging": ( 1.0,  3.0),
    "mixed":       (-3.0,  3.0),
}

def assign_irt_params(item: dict) -> dict:
    """
    Assigns/confirms IRT parameters for a single item.
    Preserves existing b-param if it's already within band bounds.
    """
    updated = dict(item)

    # a-parameter: set to 1.0 if not already set (pre-calibration default)
    if not updated.get("discrimination_a"):
        updated["discrimination_a"] = 1.0

    # c-parameter: 0.25 for MCQ (4 options), 0.0 for non-MCQ
    if updated.get("item_type") == "mcq":
        if not updated.get("guessing_c"):
            updated["guessing_c"] = 0.25
    else:
        updated["guessing_c"] = 0.0

    # b-parameter: use existing if within band, else use midpoint
    difficulty_band = updated.get("difficulty_band", "on_level")
    b_min, b_max    = BAND_BOUNDS.get(difficulty_band, (-3.0, 3.0))
    b_midpoint      = BAND_MIDPOINTS.get(difficulty_band, 0.0)

    existing_b = updated.get("difficulty_b")
    if existing_b is not None:
        try:
            b = float(existing_b)
            if b_min <= b <= b_max:
                updated["difficulty_b"] = round(b, 3)
            else:
                logger.warning(
                    "Item %s: difficulty_b=%.2f out of band [%.1f, %.1f] — "
                    "resetting to midpoint %.2f",
                    str(updated.get("item_id", "?"))[:8], b, b_min, b_max, b_midpoint,
                )
                updated["difficulty_b"] = b_midpoint
        except (TypeError, ValueError):
            updated["difficulty_b"] = b_midpoint
    else:
        updated["difficulty_b"] = b_midpoint

    return updated
