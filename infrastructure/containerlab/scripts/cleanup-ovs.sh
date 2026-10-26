#!/usr/bin/env bash
set -euo pipefail

for bridge in esm-core-sw esm-users-sw esm-servers-sw esm-mgmt-sw esm-dmz-sw esm-branch-sw1; do
  sudo ovs-vsctl --if-exists del-br "$bridge"
done

for iface in e-admin01 e-app01 e-br1-admin01 e-br1-router e-br1-user01 e-core-r01 e-core-trunk e-dns01 e-firewall-dmz e-mgmt-core e-mgmt-trunk e-mgmt01 e-servers-core e-servers-trunk e-user01 e-users-trunk e-web01; do
  sudo ip link delete "$iface" 2>/dev/null || true
done
