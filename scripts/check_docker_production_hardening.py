#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else ""

def main() -> int:
    failures = []
    compose = read("docker-compose.yml")
    prod = read("docker-compose.prod.yml")
    env = read(".env.example")
    checks = [
        ("--reload" not in compose, "docker-compose.yml has no --reload"),
        ("GRAFANA_ADMIN_PASSWORD:?GRAFANA_ADMIN_PASSWORD must be set" in compose, "Grafana password required"),
        ("GRAFANA_ADMIN_PASSWORD=" in env, ".env.example documents Grafana password"),
        ("deploy:" in compose and "resources:" in compose, "base compose has resources"),
        ((not prod) or ("deploy:" in prod and "resources:" in prod), "prod compose has resources or absent"),
        ((ROOT / "nginx/nginx.conf").exists(), "nginx config exists"),
        ((ROOT / "docker-compose.override.example.yml").exists(), "override example exists"),
    ]
    for ok, msg in checks:
        print(("- PASS " if ok else "- FAIL ") + msg)
        if not ok:
            failures.append(msg)
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
