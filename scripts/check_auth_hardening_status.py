#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/security/auth_hardening_status.md"

def main() -> int:
    files = [p for p in (ROOT / "app").rglob("*.py") if "auth" in str(p).lower()] if (ROOT / "app").exists() else []
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore").lower() for path in files)
    checks = {
        "rate_limit": any(token in text for token in ["limiter.limit", "slowapi", "rate limit", "rate_limit"]),
        "account_lockout": any(token in text for token in ["lockout", "login_failures", "failed_attempt", "too many failed"]),
        "refresh_rotation": any(token in text for token in ["refresh", "rotation", "reuse"]),
        "redis_revocation": any(token in text for token in ["revocation", "blacklist", "redis"]),
    }
    lines = ["# Auth Hardening Status", "", "| Check | Detected |", "|---|---:|"]
    lines.extend(f"| {key} | {str(value).lower()} |" for key, value in checks.items())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
