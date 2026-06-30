#!/usr/bin/env python3
"""Domain 09 evidence wrapper for billing, subscriptions, payments, and monetization."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_billing_monetization_production_readiness import main

if __name__ == "__main__":
    raise SystemExit(main())
