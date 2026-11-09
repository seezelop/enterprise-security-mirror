#!/usr/bin/env bash
set -euo pipefail

# Only ESM-owned OVS bridges. This script deliberately does not delete
# Linux interfaces by name: their ownership cannot be inferred safely.
if docker ps -a --format '{{.Names}}' | grep -q '^clab-esm-'; then
  echo "[ERROR] ESM containers still exist. Destroy the ESM topology first." >&2
  exit 1
fi

for bridge in esm-core-sw esm-users-sw esm-servers-sw esm-mgmt-sw esm-dmz-sw esm-branch-sw1; do
  sudo ovs-vsctl --if-exists del-br "$bridge"
done

echo "[PASS] Removed only ESM Open vSwitch bridges."
