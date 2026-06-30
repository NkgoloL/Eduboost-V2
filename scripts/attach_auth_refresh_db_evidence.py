#!/usr/bin/env python3
from __future__ import annotations

from scripts.auth_refresh_db_evidence_gate import attach_from_env

if __name__ == "__main__":
    status = attach_from_env()
    print(status.status)
