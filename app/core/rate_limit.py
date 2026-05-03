"""
EduBoost V2 — Rate Limiting Configuration
Protect high-cost LLM endpoints and resource-intensive operations.
"""
from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter instance (uses Redis backend if available)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",  # In production, use Redis: "redis://localhost:6379"
    default_limits=["200 per day", "50 per hour"],  # Global defaults
    swallow_errors=True,  # Don't crash if rate limiter is down
)

# ── Specific rate limits ──────────────────────────────────────────────────────
# These are high-cost operations that should be rate-limited per user

LESSON_GENERATION_LIMIT = "10 per day"        # Free tier: 10 lessons/day
LESSON_GENERATION_PREMIUM_LIMIT = "unlimited"  # Premium tier: unlimited
STUDY_PLAN_GENERATION_LIMIT = "5 per day"     # Free tier: 5 per day
STUDY_PLAN_PREMIUM_LIMIT = "50 per day"       # Premium tier: 50 per day
DIAGNOSTIC_SESSION_LIMIT = "20 per day"       # Unlimited diagnostics (cheap)
PARENT_REPORT_LIMIT = "10 per day"            # Reports limited


def get_rate_limit_for_tier(tier: str, endpoint: str) -> str:
    """
    Get appropriate rate limit based on subscription tier and endpoint.
    
    Args:
        tier: "free" or "premium"
        endpoint: "lessons", "study_plans", "parent_reports", etc.
    
    Returns:
        Rate limit string for slowapi (e.g., "10 per day")
    """
    limits = {
        "free": {
            "lessons": LESSON_GENERATION_LIMIT,
            "study_plans": STUDY_PLAN_GENERATION_LIMIT,
            "parent_reports": PARENT_REPORT_LIMIT,
        },
        "premium": {
            "lessons": LESSON_GENERATION_PREMIUM_LIMIT,
            "study_plans": STUDY_PLAN_PREMIUM_LIMIT,
            "parent_reports": "100 per day",  # Premium gets more reports
        },
    }
    return limits.get(tier, {}).get(endpoint, "10 per hour")


def is_rate_limited(user_tier: str, endpoint: str) -> bool:
    """Check if an endpoint is rate-limited for a given tier."""
    limit_str = get_rate_limit_for_tier(user_tier, endpoint)
    return limit_str != "unlimited"
