#!/usr/bin/env bash
# cleanup-next-artifacts.sh
# Detects and removes root-owned .next artifacts from Docker build bleed-through.
# Run this before local pnpm build, or in CI after Docker steps.
#
# Usage:
#   bash scripts/cleanup-next-artifacts.sh [frontend-dir]
#
# Example:
#   bash scripts/cleanup-next-artifacts.sh app/frontend

set -euo pipefail

FRONTEND_DIR="${1:-app/frontend}"
NEXT_DIR="${FRONTEND_DIR}/.next"

if [ ! -d "${NEXT_DIR}" ]; then
  echo "[cleanup-next] .next directory not found at ${NEXT_DIR} — nothing to do."
  exit 0
fi

OWNER="$(stat -c '%U' "${NEXT_DIR}" 2>/dev/null || stat -f '%Su' "${NEXT_DIR}" 2>/dev/null)"
CURRENT_USER="$(id -un)"

if [ "${OWNER}" = "root" ] && [ "${CURRENT_USER}" != "root" ]; then
  echo "[cleanup-next] WARNING: ${NEXT_DIR} is owned by root (Docker artifact)."
  echo "[cleanup-next] Attempting removal with sudo..."
  sudo rm -rf "${NEXT_DIR}"
  echo "[cleanup-next] Removed root-owned .next at ${NEXT_DIR}."
elif [ "${OWNER}" = "${CURRENT_USER}" ]; then
  echo "[cleanup-next] ${NEXT_DIR} is owned by ${CURRENT_USER} — safe to remove."
  rm -rf "${NEXT_DIR}"
  echo "[cleanup-next] Removed ${NEXT_DIR}."
else
  echo "[cleanup-next] ${NEXT_DIR} is owned by '${OWNER}'. Cannot remove automatically."
  echo "[cleanup-next] Run: sudo rm -rf ${NEXT_DIR}"
  exit 1
fi
