#!/usr/bin/env python3
"""Run EduBoost staging smoke checks against a deployed environment."""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "release" / "staging_smoke_latest.json"
DEFAULT_MARKDOWN = REPO_ROOT / "docs" / "release" / "staging_smoke_latest.md"


@dataclass(frozen=True)
class SmokeCheck:
    name: str
    method: str
    path: str
    expected_statuses: tuple[int, ...]
    required_headers: tuple[str, ...] = ()


@dataclass(frozen=True)
class SmokeResult:
    name: str
    method: str
    path: str
    expected_statuses: list[int]
    actual_status: int | None
    passed: bool
    duration_ms: float
    error: str | None
    headers: dict[str, str]


DEFAULT_CHECKS = [
    SmokeCheck("health_deep", "GET", "/api/v2/health/deep", (200, 503)),
    SmokeCheck("openapi", "GET", "/openapi.json", (200,)),
    SmokeCheck(
        "security_headers",
        "GET",
        "/api/v2/health",
        (200, 404),
        required_headers=("x-content-type-options", "x-frame-options"),
    ),
    SmokeCheck("auth_register_shape", "POST", "/api/v2/auth/register", (201, 400, 409, 422)),
    SmokeCheck("popia_export_requires_auth", "GET", "/api/v2/popia/data-export/smoke-learner", (401, 403, 404)),
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_base_url(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("base URL is empty")
    if not stripped.startswith(("http://", "https://")):
        raise ValueError("base URL must start with http:// or https://")
    return stripped.rstrip("/") + "/"



def _is_placeholder_base_url(base_url: str) -> bool:
    # Return true for placeholder/example staging URLs.
    lowered = base_url.strip().lower().rstrip("/")
    return (
        "example.com" in lowered
        or "example.test" in lowered
        or "staging.example" in lowered
        or lowered.endswith(".invalid")
        or ".invalid/" in lowered
        or lowered.endswith(".test")
        or ".test/" in lowered
    )


def _request(
    base_url: str,
    check: SmokeCheck,
    timeout_seconds: float,
    verify_tls: bool,
) -> SmokeResult:
    url = urljoin(base_url, check.path.lstrip("/"))
    body: bytes | None = None
    headers: dict[str, str] = {"User-Agent": "EduBoost-Staging-Smoke/1.0"}

    if check.method == "POST":
        headers["Content-Type"] = "application/json"
        body = json.dumps(
            {
                "email": f"staging-smoke-{int(time.time())}@example.invalid",
                "display_name": "Staging Smoke",
                "password": "StagingSmoke!12345",
                "role": "parent",
            }
        ).encode("utf-8")

    request = urllib.request.Request(url, data=body, method=check.method, headers=headers)
    context = None if verify_tls else ssl._create_unverified_context()  # noqa: SLF001

    started = time.perf_counter()
    response_headers: dict[str, str] = {}
    status: int | None = None
    error: str | None = None

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds, context=context) as response:
            status = response.status
            response_headers = {key.lower(): value for key, value in response.headers.items()}
            response.read(4096)
    except urllib.error.HTTPError as exc:
        status = exc.code
        response_headers = {key.lower(): value for key, value in exc.headers.items()}
        try:
            exc.read(4096)
        except Exception:
            pass
    except Exception as exc:  # network failure is a smoke failure
        error = f"{type(exc).__name__}: {exc}"

    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    required_header_ok = all(header.lower() in response_headers for header in check.required_headers)
    passed = status in check.expected_statuses and error is None and required_header_ok

    if error is None and not required_header_ok:
        missing = [header for header in check.required_headers if header.lower() not in response_headers]
        error = "missing required headers: " + ", ".join(missing)

    return SmokeResult(
        name=check.name,
        method=check.method,
        path=check.path,
        expected_statuses=list(check.expected_statuses),
        actual_status=status,
        passed=passed,
        duration_ms=duration_ms,
        error=error,
        headers={key: response_headers[key] for key in sorted(response_headers) if key.startswith("x-") or key in {"content-type"}},
    )


def run_smoke(base_url: str, timeout_seconds: float = 10.0, verify_tls: bool = True) -> dict[str, Any]:
    normalized = _normalize_base_url(base_url)
    results = [_request(normalized, check, timeout_seconds, verify_tls) for check in DEFAULT_CHECKS]
    passed = all(result.passed for result in results)
    return {
        "captured_at": _utc_now(),
        "base_url": normalized.rstrip("/"),
        "passed": passed,
        "results": [asdict(result) for result in results],
    }


def write_outputs(payload: dict[str, Any], json_path: Path = DEFAULT_OUTPUT, markdown_path: Path = DEFAULT_MARKDOWN) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    status = "passed" if payload["passed"] else "failed"
    rows = [
        "# Staging Smoke Evidence",
        "",
        f"**Status:** runtime smoke {status}",
        f"<!-- Status: runtime smoke {status} -->",
        "",
        f"- Captured at: `{payload['captured_at']}`",
        f"- Base URL: `{payload['base_url']}`",
        f"- JSON evidence: `{json_path.as_posix()}`",
        "",
        "| Check | Method | Path | Expected | Actual | Passed | Error |",
        "|---|---|---|---|---:|---|---|",
    ]

    for result in payload["results"]:
        rows.append(
            "| {name} | {method} | `{path}` | `{expected}` | {actual} | {passed} | {error} |".format(
                name=result["name"],
                method=result["method"],
                path=result["path"],
                expected=",".join(str(item) for item in result["expected_statuses"]),
                actual="" if result["actual_status"] is None else result["actual_status"],
                passed="yes" if result["passed"] else "no",
                error="" if result["error"] is None else result["error"].replace("|", "\\|"),
            )
        )

    rows.extend(
        [
            "",
            "## Decision",
            "",
            "- [ ] Staging smoke accepted by release owner.",
            "- [ ] Staging smoke rejected and release blocked.",
            "",
        ]
    )
    markdown_path.write_text("\n".join(rows), encoding="utf-8")


def validate_payload(path: Path = DEFAULT_OUTPUT, require_pass: bool = False) -> bool:
    if not path.exists():
        print(f"- FAIL [file] {path}: missing")
        return False

    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {"captured_at", "base_url", "passed", "results"}
    missing = sorted(required - set(payload))
    if missing:
        print(f"- FAIL [json] {path}: missing {missing}")
        return False

    if not isinstance(payload["results"], list) or not payload["results"]:
        print(f"- FAIL [json] {path}: no smoke results")
        return False

    if require_pass and payload.get("passed") is not True:
        print(f"- FAIL [json] {path}: smoke result exists but passed=false")
        return False

    print(f"- PASS [json] {path}: {len(payload['results'])} smoke result(s), passed={payload['passed']}")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("STAGING_BASE_URL", ""), help="Staging base URL. Defaults to STAGING_BASE_URL.")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--insecure", action="store_true", help="Disable TLS certificate verification.")
    parser.add_argument("--validate", action="store_true", help="Validate existing staging_smoke_latest.json.")
    parser.add_argument("--require-pass", action="store_true", help="When validating, fail unless the latest smoke passed.")
    parser.add_argument("--allow-example-url", action="store_true", help="Allow placeholder example.* URLs for local tool testing only.")
    args = parser.parse_args(argv)

    if args.validate:
        return 0 if validate_payload(require_pass=args.require_pass) else 1

    if not args.base_url:
        print("STAGING_BASE_URL or --base-url is required to run staging smoke.", file=sys.stderr)
        return 2

    if _is_placeholder_base_url(args.base_url) and not args.allow_example_url:
        print(
            "Refusing to run staging smoke against placeholder example/test URL. "
            "Set STAGING_BASE_URL to the real staging deployment URL.",
            file=sys.stderr,
        )
        return 2

    payload = run_smoke(args.base_url, timeout_seconds=args.timeout, verify_tls=not args.insecure)
    write_outputs(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
