# ESM Containerlab Infrastructure

This directory contains the implemented ESM topology derived from Lab 12, not the original `clab-lab12` deployment. The topology file retains its historical filename `lab12.clab.yml`, but its declared lab name is `esm`.

## Actual topology

18 Linux containers and six external OVS bridges, with 23 point-to-point links:

```text
internet01 -> isp01 -> edge-r01 -> firewall01 -> esm-dmz-sw -> web01 (FastAPI HTTPS)
                                          |
                                      core-r01
                                          |
                           HQ VLANs + three routed branches
```

HQ networks: USERS `10.70.10.0/24`, SERVERS `10.70.20.0/24`, ADMIN `10.70.30.0/24`, MANAGEMENT `10.70.99.0/24`, DMZ `10.70.50.0/24`. OSPF connects `core-r01` to the three branch routers. Corporate networks are fictitious; public-facing topology interfaces use TEST-NET address space.

`firewall01` performs nftables forwarding/filtering and DNAT from `203.0.113.2:443` to `web01:10.70.50.10:443`. The portal uses FastAPI with a self-signed certificate. Corporate test hosts continue to simulate some services using Netcat.

## Reproduce and validate

Follow [the complete ESC-001 reproduction procedure](../../scenarios/esc-001/REPRODUCE.md). On a clean supported host:

```bash
sudo -v
./scripts/deploy-lab.sh
```

The script runs the preflight, builds both `esm-frr-nft:10.6.1` and `esm-web-portal:0.2`, creates only `esm-*` OVS bridges, deploys, configures VLANs, waits for OSPF, and runs 12 live policy checks.

After deployment, `python3 validation/test_policy.py` runs live checks. The standard `tests/` and GitHub Actions workflow provide separate offline/static checks.

## Safety

Do not run scripts from the original Lab 12 directory against ESM. `preflight.sh` intentionally refuses to deploy if prior ESM resources remain or original Lab 12 containers are active. Do not rerun deployment on an active lab.

To tear down ESM: `sudo containerlab destroy -t lab12.clab.yml`, then `./scripts/cleanup-ovs.sh` **after checking no ESM containers remain**. The cleanup script removes only named ESM OVS bridges and never deletes arbitrary interfaces by name. It deliberately does not touch the original `clab-lab12` environment.

Virtualization, Docker kernel/network permissions and host resources vary. A green offline CI run cannot substitute for clean-host deployment validation.
