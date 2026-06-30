#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

fail() {
  echo "[FAIL] $1" >&2
  exit 1
}

[[ -f docker-compose.prod.yml ]] || fail "docker-compose.prod.yml missing"
[[ -f docker/nginx.prod.conf ]] || fail "docker/nginx.prod.conf missing"

grep -q './docker/nginx.prod.conf:/etc/nginx/nginx.conf:ro' docker-compose.prod.yml || fail "compose must mount docker/nginx.prod.conf"
grep -q 'frontend:' docker-compose.prod.yml || fail "frontend service missing in compose"
grep -q 'server frontend:3050;' docker/nginx.prod.conf || fail "nginx frontend upstream mismatch"
grep -q 'server api:8000;' docker/nginx.prod.conf || fail "nginx api upstream mismatch"

echo "[OK] Static production compose/nginx contract checks passed"

if command -v docker >/dev/null 2>&1; then
  docker compose -f docker-compose.prod.yml config >/tmp/eduboost-prod-compose-config.yml
  echo "[OK] docker compose config validation passed"
else
  echo "[WARN] docker not installed; skipped docker compose config validation"
fi
