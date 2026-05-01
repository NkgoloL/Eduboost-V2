#!/usr/bin/env bash
set -euo pipefail

# Setup Python virtualenv and install core backend dependencies (non-ML)
PYTHON=${PYTHON:-python3}
VENV_DIR=${VENV_DIR:-.venv}

echo "Creating virtualenv in $VENV_DIR using $PYTHON"
$PYTHON -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip

echo "Installing backend requirements (core)"
pip install -r requirements.txt

echo "Dev environment ready. Activate with: source $VENV_DIR/bin/activate"
