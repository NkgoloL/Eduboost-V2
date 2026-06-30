#!/usr/bin/env python3
from __future__ import annotations

from scripts.auth_route_service_dependency_repair import repair

if __name__ == "__main__":
    status = repair()
    print(status.status)
    for blocker in status.blockers:
        print(f"- {blocker}")
