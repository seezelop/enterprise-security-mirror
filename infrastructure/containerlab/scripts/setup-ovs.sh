#!/usr/bin/env bash

set -euo pipefail

sudo ovs-vsctl --may-exist add-br esm-core-sw
sudo ovs-vsctl --may-exist add-br esm-users-sw
sudo ovs-vsctl --may-exist add-br esm-servers-sw
sudo ovs-vsctl --may-exist add-br esm-mgmt-sw
sudo ovs-vsctl --may-exist add-br esm-dmz-sw
sudo ovs-vsctl --may-exist add-br esm-branch-sw1

sudo ip link set esm-core-sw up
sudo ip link set esm-users-sw up
sudo ip link set esm-servers-sw up
sudo ip link set esm-mgmt-sw up
sudo ip link set esm-dmz-sw up
sudo ip link set esm-branch-sw1 up

echo "[+] LAB 12 Open vSwitch bridges are ready."
