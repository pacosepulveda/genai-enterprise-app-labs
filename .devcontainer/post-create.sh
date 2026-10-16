#!/usr/bin/env bash
set -euo pipefail

echo "==> Preparing Enterprise GenAI course environment"
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'

mkdir -p data/vectorstore models/checkpoints outputs
python scripts/init_database.py

python -m ipykernel install --user \
  --name genai-course \
  --display-name 'Python (GenAI Course)' >/dev/null 2>&1 || true

echo
echo "Environment prepared. Next: open docs/PREFLIGHT.md"
