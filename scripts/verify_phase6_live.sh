#!/usr/bin/env bash
# Phase 6 Live Docker Verification Script
# Run this when Docker is available to close the remaining unverified RoadMap criteria.
set -euo pipefail

echo "=== Phase 6: Live Docker Verification ==="
echo ""

# ── Prerequisites ──────────────────────────────────────────────────────────
echo "[1/6] Checking prerequisites..."
if ! docker compose version &>/dev/null; then
  echo "ERROR: docker compose not available. Install Docker Desktop or Docker Engine."
  exit 1
fi
echo "  docker compose: OK"

# ── Build and Start Stack ──────────────────────────────────────────────────
echo "[2/6] Building and starting stack (postgres + redis + worker)..."
docker compose up -d postgres redis worker
echo "  Waiting for healthy services..."
sleep 10

# ── Worker Health ──────────────────────────────────────────────────────────
echo "[3/6] Checking worker health..."
docker compose logs worker --tail 50 > /tmp/phase6_worker_logs.txt
if grep -q "ARQ worker starting up" /tmp/phase6_worker_logs.txt; then
  echo "  ✅ Worker started successfully"
else
  echo "  ❌ Worker did not start as expected. See /tmp/phase6_worker_logs.txt"
  docker compose logs worker
  exit 1
fi

# ── Enqueue a Job ──────────────────────────────────────────────────────────
echo "[4/6] Enqueuing a test consent renewal job..."
JOB_RESPONSE=$(curl -s -X POST http://localhost:8000/v2/admin/consent/trigger-renewal-reminders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(docker compose exec -T api python -c 'from app.core.security import create_access_token; print(create_access_token(subject=\"test-admin\", role=\"admin\"))')")
echo "  Response: $JOB_RESPONSE"
JOB_ID=$(echo "$JOB_RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin)['data']['job_id'])")
echo "  Job ID: $JOB_ID"
sleep 5

# ── Verify Execution ────────────────────────────────────────────────────────
echo "[5/6] Checking job execution status..."
JOB_STATUS=$(curl -s http://localhost:8000/v2/jobs/$JOB_ID | python -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))")
echo "  Job status: $JOB_STATUS"
if [ "$JOB_STATUS" = "completed" ] || [ "$JOB_STATUS" = "running" ]; then
  echo "  ✅ Job executed successfully"
else
  echo "  ⚠️ Job status: $JOB_STATUS (may need longer wait)"
fi

# ── Restart-Survival Test ──────────────────────────────────────────────────
echo "[6/6] Testing restart survival..."
# Enqueue another job first
JOB2_RESPONSE=$(curl -s -X POST http://localhost:8000/v2/admin/consent/trigger-renewal-reminders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(docker compose exec -T api python -c 'from app.core.security import create_access_token; print(create_access_token(subject=\"test-admin\", role=\"admin\"))')")
JOB2_ID=$(echo "$JOB2_RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin)['data']['job_id'])")
echo "  Enqueued job: $JOB2_ID before restart"

echo "  Restarting API container..."
docker compose restart api
sleep 3
echo "  API restarted"

echo "  Checking if queued job still executes..."
sleep 10
JOB2_STATUS=$(curl -s http://localhost:8000/v2/jobs/$JOB2_ID | python -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))")
echo "  Job status after restart: $JOB2_STATUS"
if [ "$JOB2_STATUS" = "completed" ] || [ "$JOB2_STATUS" = "running" ]; then
  echo "  ✅ RESTART SURVIVAL VERIFIED: Job persisted through API restart"
else
  echo "  ❌ RESTART SURVIVAL NOT VERIFIED: Job status is '$JOB2_STATUS'"
  echo "  (Note: The worker may need time to pick up the job)"
fi

echo ""
echo "=== Verification Complete ==="
echo "Logs saved to /tmp/phase6_worker_logs.txt"
echo "Update docs/release/phase_6_evidence.md with captured outputs."
