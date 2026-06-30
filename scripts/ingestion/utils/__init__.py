"""
EduBoost SA — Ingestion Utilities
===================================
Shared helpers: async rate limiting and robots.txt compliance.
"""
from scripts.ingestion.utils.rate_limiter import RateLimiter, throttle
from scripts.ingestion.utils.robots_checker import can_fetch, extract_crawl_delay

__all__ = [
    "RateLimiter",
    "throttle",
    "can_fetch",
    "extract_crawl_delay",
]
