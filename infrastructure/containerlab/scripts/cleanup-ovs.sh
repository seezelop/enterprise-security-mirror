#!/usr/bin/env bash

set -euo pipefail

# Remove possible leftover Containerlab host-side interfaces.
for iface in \
  core-r01 \
  users-trunk core-trunk user01 \
  servers-trunk servers-core dns01 app01 \
  mgmt-trunk mgmt-core admin01 \
  firewall-dmz web01
do
  sudo ip link delete "$iface" 2>/dev/null || true
done

# Remove external OVS bridges.
for bridge in core-sw users-sw servers-sw mgmt-sw dmz-sw branch-sw1 br1-router br1-user01 br1-admin01 mgmt01
do
  sudo ovs-vsctl --if-exists del-br "$bridge"
done

echo "[+] LAB 12 OVS bridges and residual interfaces removed."
