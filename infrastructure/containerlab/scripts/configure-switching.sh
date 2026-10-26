#!/usr/bin/env bash

set -euo pipefail

# core-r01 <-> core-sw
sudo ovs-vsctl set port e-core-r01 vlan_mode=trunk trunks=10,20,30,99

# USERS distribution
sudo ovs-vsctl set port e-users-trunk vlan_mode=trunk trunks=10
sudo ovs-vsctl set port e-core-trunk vlan_mode=trunk trunks=10
sudo ovs-vsctl set port e-user01 tag=10

# SERVERS distribution
sudo ovs-vsctl set port e-servers-trunk vlan_mode=trunk trunks=20
sudo ovs-vsctl set port e-servers-core vlan_mode=trunk trunks=20
sudo ovs-vsctl set port e-dns01 tag=20
sudo ovs-vsctl set port e-app01 tag=20

# ADMIN / MANAGEMENT distribution
sudo ovs-vsctl set port e-mgmt-trunk vlan_mode=trunk trunks=30,99
sudo ovs-vsctl set port e-mgmt-core vlan_mode=trunk trunks=30,99
sudo ovs-vsctl set port e-admin01 tag=30
sudo ovs-vsctl set port e-mgmt01 tag=99

# BRANCH 1
sudo ovs-vsctl set port e-br1-router vlan_mode=trunk trunks=10,30,99
sudo ovs-vsctl set port e-br1-user01 tag=10
sudo ovs-vsctl set port e-br1-admin01 tag=30

echo "[+] HQ VLAN switching configured."
