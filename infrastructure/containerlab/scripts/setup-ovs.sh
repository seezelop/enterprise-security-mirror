#!/usr/bin/env bash

set -euo pipefail

sudo ovs-vsctl --may-exist add-br core-sw
sudo ovs-vsctl --may-exist add-br users-sw
sudo ovs-vsctl --may-exist add-br servers-sw
sudo ovs-vsctl --may-exist add-br mgmt-sw
sudo ovs-vsctl --may-exist add-br dmz-sw
sudo ovs-vsctl --may-exist add-br branch-sw1

sudo ip link set core-sw up
sudo ip link set users-sw up
sudo ip link set servers-sw up
sudo ip link set mgmt-sw up
sudo ip link set dmz-sw up
sudo ip link set branch-sw1 up

echo "[+] LAB 12 Open vSwitch bridges are ready."
