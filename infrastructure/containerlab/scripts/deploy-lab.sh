#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[INFO] Checking original Lab 12 deployment..."

if docker ps --filter 'name=clab-lab12-' --format '{{.Names}}' | grep -q .; then
    echo "[ERROR] Lab 12 original sigue activo. No desplegar ESM." >&2
    exit 1
fi

echo "[INFO] Running ESM preflight..."
./scripts/preflight.sh

echo "[INFO] Building ESM FRR + nftables image..."
docker build \
    -t esm-frr-nft:10.6.1 \
    -f containers/frr-nft/Dockerfile .

echo "[INFO] Creating ESM Open vSwitch bridges..."
./scripts/setup-ovs.sh

echo "[INFO] Deploying ESM Containerlab topology..."
sudo containerlab deploy -t lab12.clab.yml

echo "[INFO] Configuring ESM VLANs..."
./scripts/configure-switching.sh

echo "[INFO] Running baseline security policy tests..."
python3 validation/test_policy.py

echo "[INFO] ESM deployment completed."
