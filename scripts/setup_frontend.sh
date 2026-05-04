#!/usr/bin/env bash
set -euo pipefail

echo "Installing frontend dependencies and building"
cd app/frontend
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi
echo "Frontend dependencies installed. Run 'npm run dev' or 'npm run build' as needed."
