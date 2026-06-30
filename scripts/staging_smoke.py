#!/usr/bin/env python3
"""HTTP smoke checks for staging/production endpoints."""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass(frozen=True)
class Check:
    path: str
    expect_status: int
    contains: str | None = None


CHECKS = [
    Check("/health", 200, '"status"'),
    Check("/ready", 200, '"status"'),
    Check("/metrics", 200, "eduboost_http_requests_total"),
    Check("/docs", 200, "Swagger UI"),
    Check("/openapi.json", 200, '"openapi"'),
]


def fetch(url: str, timeout: float) -> tuple[int, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "eduboost-staging-smoke/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - operator-provided URL
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--json-output", default="")
    args = parser.parse_args()

    results: list[dict[str, object]] = []
    ok = True
    for check in CHECKS:
        url = urljoin(args.base_url.rstrip("/") + "/", check.path.lstrip("/"))
        status = 0
        body = ""
        for attempt in range(1, args.retries + 1):
            status, body = fetch(url, args.timeout)
            if status == check.expect_status and (check.contains is None or check.contains in body):
                break
            time.sleep(min(attempt, 3))
        passed = status == check.expect_status and (check.contains is None or check.contains in body)
        ok = ok and passed
        results.append({"path": check.path, "status": status, "passed": passed})
        print(f"{check.path}: status={status} passed={passed}")

    if args.json_output:
        with open(args.json_output, "w", encoding="utf-8") as handle:
            json.dump({"base_url": args.base_url, "results": results, "passed": ok}, handle, indent=2)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
