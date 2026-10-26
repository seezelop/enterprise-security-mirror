#!/usr/bin/env bash

set -euo pipefail

# core-r01 <-> core-sw
sudo ovs-vsctl set port core-r01 vlan_mode=trunk trunks=10,20,30,99

# USERS distribution
sudo ovs-vsctl set port users-trunk vlan_mode=trunk trunks=10
sudo ovs-vsctl set port core-trunk vlan_mode=trunk trunks=10
sudo ovs-vsctl set port user01 tag=10

# SERVERS distribution
sudo ovs-vsctl set port servers-trunk vlan_mode=trunk trunks=20
sudo ovs-vsctl set port servers-core vlan_mode=trunk trunks=20
sudo ovs-vsctl set port dns01 tag=20
sudo ovs-vsctl set port app01 tag=20

# ADMIN / MANAGEMENT distribution
sudo ovs-vsctl set port mgmt-trunk vlan_mode=trunk trunks=30,99
sudo ovs-vsctl set port mgmt-core vlan_mode=trunk trunks=30,99
sudo ovs-vsctl set port admin01 tag=30
sudo ovs-vsctl set port mgmt01 tag=99

# BRANCH 1
sudo ovs-vsctl set port br1-router vlan_mode=trunk trunks=10,30,99
sudo ovs-vsctl set port br1-user01 tag=10
sudo ovs-vsctl set port br1-admin01 tag=30

echo "[+] HQ VLAN switching configured."
