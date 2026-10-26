# Enterprise Security Mirror

> Status: **architecture and lab baseline imported; scenarios not yet implemented.**

A defensive security portfolio project built on the [network-security-labs Lab 12](https://github.com/seezelop/network-security-labs/tree/main/labs/12-enterprise-network-security) enterprise network topology (HQ, three branches, VLANs, OSPF, firewall and DMZ).

**Goal:** reproduce plausible small-business security problems and validate them end-to-end with observed evidence: legitimate activity, adversary emulation in an isolated lab, detection, response, analysis of blind spots and regression testing.

## Three scenarios

| Scenario | Scope | Status |
|---|---|---|
| ESC-001: DMZ Web Application Compromise | Real HTTPS service, application logs, detection and defensive validation | Planned, first |
| ESC-002: Identity & Privilege Abuse | Roles, permissions, RADIUS/EAP and AD if hardware supports it | Planned |
| ESC-003: Lateral Movement, Segmentation & Resilience | East-west network controls, IPsec, link redundancy and visibility | Planned |

## Technical blocks

- **A. Secure Enterprise Infrastructure:** routing, segmentation, IPsec, redundancy and defense in depth.
- **B. Identity & Access Security:** identities, least privilege, AD, RADIUS, EAP and NAC.
- **C. Threat Detection & Defense Validation:** telemetry, IDS/IPS, investigations, detection engineering and tests.

## Documents

- [Project plan](PROJECT_PLAN.md)
- [Architecture](ARCHITECTURE.md)
- [Lab 12 source commit](infrastructure/containerlab/SOURCE_COMMIT.txt)

## CI/CD

The initial [GitHub Actions workflow](.github/workflows/ci.yml) is a **static/offline check** of the imported baseline. It does **not** deploy Containerlab or run any offensive activity. Future workflows will validate detection rules and synthetic fixtures.

## Safety and limitations

All scenarios must run in an isolated, authorized laboratory using synthetic credentials and data. Findings and screenshots must be sanitized before publication. These are **personal lab projects, not production experience**.
