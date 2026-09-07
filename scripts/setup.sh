#!/usr/bin/env bash
set -e

echo "=========================================="
echo "  Setting up ProofChain Environment"
echo "=========================================="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "1. Checking Python environment..."
python3 -m pip install -r backend/requirements.txt

echo "2. Checking Frontend dependencies..."
cd frontend
npm install
cd "$ROOT_DIR"

echo "3. Initializing demo environment..."
python3 -c "
import sys
sys.path.insert(0, '$ROOT_DIR/backend')
from app.services.workspace_service import workspace_store
ws = workspace_store.load_demo_data('demo-workspace')
print(f'Successfully initialized demo workspace with {len(ws.documents)} documents.')
"

echo "=========================================="
echo "  ProofChain Setup Complete! 🚀"
echo "  Run ./scripts/run_demo.sh to launch"
echo "=========================================="
