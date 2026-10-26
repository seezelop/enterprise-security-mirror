#!/usr/bin/env bash

set -euo pipefail

echo "[INFO] BUILDING CUSTOM FRR + NFTABLES IMAGE..."
docker build \
    -t lab12-frr-nft:10.6.1 \
    -f containers/frr-nft/Dockerfile .

echo "[INFO] REMOVING PREVIOUS CONTAINERLAB DEPLOYMENT..."
sudo containerlab destroy -t lab12.clab.yml 2>/dev/null || true

echo "[INFO] CLEANING LAB 12 OVS STATE..."
./scripts/cleanup-ovs.sh

echo "[INFO] REMOVING GENERATED CONTAINERLAB STATE..."
sudo rm -rf clab-lab12

echo "[INFO] CREATING OVS BRIDGES..."
./scripts/setup-ovs.sh

echo "[INFO] DEPLOYING LAB 12..."
sudo containerlab deploy -t lab12.clab.yml

echo "[INFO] APPLYING VLAN CONFIGURATION..."
./scripts/configure-switching.sh

echo "[INFO] RUNNING SECURITY POLICY VALIDATION..."
python3 validation/test_policy.py

echo "[INFO] LAB 12 DEPLOYMENT COMPLETE."
