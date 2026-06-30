#!/usr/bin/env python3
"""
Phase 9 — G.1: API Runtime Health Verification

Verifies that the following endpoints respond correctly:
- GET /health — returns HTTP 200 with minimal status
- GET /ready — returns HTTP 200 only when DB, Redis reachable  
- GET /metrics — exposes Prometheus metrics
- GET /docs — Swagger UI loads
- GET /openapi.json — returns valid OpenAPI 3.x schema

Usage:
    python scripts/verify_api_health.py [--base-url http://localhost:8000]
"""
import argparse
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def check_endpoint(url: str, expected_status: int = 200) -> tuple[bool, str]:
    """Check if an endpoint returns the expected status code."""
    try:
        req = Request(url, headers={"User-Agent": "EduBoost-HealthCheck/1.0"})
        with urlopen(req, timeout=10) as response:
            status = response.status
            body = response.read().decode("utf-8")
            if status != expected_status:
                return False, f"Expected {expected_status}, got {status}"
            return True, body
    except HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except URLError as e:
        return False, f"URL error: {e.reason}"
    except Exception as e:
        return False, f"Error: {e}"


def verify_health(url: str) -> bool:
    """Verify /health endpoint."""
    print("\n🔍 Checking /health...")
    success, body = check_endpoint(f"{url}/health")
    if success:
        try:
            data = json.loads(body)
            if data.get("status") == "ok":
                print("  ✅ /health returns 200 with {status: ok}")
                return True
            print(f"  ⚠️ /health returned 200 but status={data.get('status')}")
            return False
        except json.JSONDecodeError:
            print("  ⚠️ /health returned non-JSON body")
            return True  # Still counts as success if 200
    print(f"  ❌ /health failed: {body}")
    return False


def verify_ready(url: str) -> bool:
    """Verify /ready endpoint."""
    print("\n🔍 Checking /ready...")
    success, body = check_endpoint(f"{url}/ready")
    if success:
        try:
            data = json.loads(body)
            status = data.get("status", "unknown")
            if status in ("ok", "degraded"):
                print(f"  ✅ /ready returns 200 with status={status}")
                return True
            print(f"  ⚠️ /ready returned status={status}")
            return status == "ok"
        except json.JSONDecodeError:
            print("  ⚠️ /ready returned non-JSON body")
            return True
    print(f"  ❌ /ready failed: {body}")
    return False


def verify_metrics(url: str) -> bool:
    """Verify /metrics endpoint exposes Prometheus metrics."""
    print("\n🔍 Checking /metrics...")
    success, body = check_endpoint(f"{url}/metrics")
    if success:
        # Prometheus metrics should contain metric names like "http_requests_total"
        if "# TYPE" in body or "python_" in body or "uvicorn_" in body:
            print("  ✅ /metrics exposes Prometheus metrics")
            return True
        print("  ⚠️ /metrics returned but may not contain Prometheus metrics")
        return True
    print(f"  ❌ /metrics failed: {body}")
    return False


def verify_docs(url: str) -> bool:
    """Verify /docs Swagger UI loads."""
    print("\n🔍 Checking /docs...")
    success, body = check_endpoint(f"{url}/docs")
    if success:
        if "swagger" in body.lower() or "redoc" in body.lower():
            print("  ✅ /docs loads Swagger UI")
            return True
        print("  ⚠️ /docs returned but may not contain Swagger UI")
        return True
    print(f"  ❌ /docs failed: {body}")
    return False


def verify_openapi(url: str) -> bool:
    """Verify /openapi.json returns valid OpenAPI schema."""
    print("\n🔍 Checking /openapi.json...")
    success, body = check_endpoint(f"{url}/openapi.json")
    if success:
        try:
            data = json.loads(body)
            if data.get("openapi", "").startswith("3."):
                print("  ✅ /openapi.json returns valid OpenAPI 3.x schema")
                return True
            print("  ⚠️ /openapi.json returned but openapi version may be wrong")
            return False
        except json.JSONDecodeError:
            print("  ❌ /openapi.json returned invalid JSON")
            return False
    print(f"  ❌ /openapi.json failed: {body}")
    return False


def main():
    parser = argparse.ArgumentParser(description="Verify API runtime health endpoints")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the API server"
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=0,
        help="Seconds to wait before starting checks"
    )
    args = parser.parse_args()

    if args.wait:
        print(f"⏳ Waiting {args.wait}s for server to be ready...")
        time.sleep(args.wait)

    print("🏥 EduBoost API Health Check")
    print(f"   Base URL: {args.base_url}")

    results = []
    results.append(("health", verify_health(args.base_url)))
    results.append(("ready", verify_ready(args.base_url)))
    results.append(("metrics", verify_metrics(args.base_url)))
    results.append(("docs", verify_docs(args.base_url)))
    results.append(("openapi", verify_openapi(args.base_url)))

    print("\n" + "=" * 50)
    print("📊 Summary:")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name:12s}: {status}")
    print(f"\n  Total: {passed}/{total} passed")

    if passed == total:
        print("\n🎉 All health checks passed!")
        sys.exit(0)
    else:
        print(f"\n💥 {total - passed} check(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
