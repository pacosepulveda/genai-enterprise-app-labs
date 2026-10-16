#!/usr/bin/env bash
set -euo pipefail

echo "==> Preparing Enterprise GenAI course environment"
python -m pip install --upgrade pip

# Codespaces for this course run without GPU. Install the CPU wheels explicitly
# so the environment does not download unnecessary CUDA packages.
python -m pip install \
  torch==2.12.0 torchvision==0.27.0 \
  --index-url https://download.pytorch.org/whl/cpu

python -m pip install -e '.[dev]'

mkdir -p data/vectorstore models/checkpoints outputs
python scripts/init_database.py

python -m ipykernel install --user \
  --name genai-course \
  --display-name 'Python (GenAI Course)' >/dev/null 2>&1 || true

echo
echo "Environment prepared. Next: open docs/PREFLIGHT.md"
