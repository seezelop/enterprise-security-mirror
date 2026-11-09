# ESC-001: Web Application Security

## Case 01: Broken Object Level Authorization (BOLA)

**Status:** Local laboratory completed. DMZ integration pending.

### 1. Objective

Simulate an authorization vulnerability in a fictional enterprise API,
detect unauthorized access, remediate the weakness, and document the
incident response process.

### 2. Environment

- Python and FastAPI
- REST API with Bearer authentication
- Fictional customers and role-based access
- JSONL application security logs
- Python detection script

The application currently runs locally on Ubuntu.

### 3. Attack scenario

Two fictional customers have separate records:

| User | Authorized customer ID |
|------|------------------------|
| cliente1 | 1 |
| cliente2 | 2 |

The object-level authorization check was intentionally disabled.

An authenticated user, cliente1, requested:

GET /customers/2

The application returned HTTP 200 and disclosed fictional information
belonging to cliente2.

**OWASP classification:** API1:2023 Broken Object Level Authorization.

### 4. Incident Response

Methodology: NIST SP 800-61 Rev. 3.

#### Preparation

- Defined fictional users and access permissions.
- Implemented authentication and application audit logging.
- Established expected authorization behavior.

#### Detection and Analysis

- Reproduced an unauthorized customer record access.
- Observed an HTTP 200 response.
- Analyzed JSONL application events.
- Executed detect_bola.py.
- Correlated the authenticated identity, assigned customer and
  requested customer ID.

**Finding:** The application recorded the unauthorized request as
successful, but the detection script identified the authorization
violation.

#### Response: Containment and Eradication

- Restored server-side object-level authorization.
- Removed the intentionally introduced vulnerable behavior.
- Preserved the laboratory evidence.

No account isolation, credential revocation or production incident
containment was performed.

#### Recovery and Validation

- Restarted the corrected application.
- Repeated the unauthorized request as cliente1.
- Verified that GET /customers/2 returned HTTP 403.
- Confirmed the expected access control behavior.

#### Lessons Learned

- Successful HTTP responses do not necessarily represent legitimate
  activity.
- Authentication alone does not establish authorization.
- Identity and object ownership context improve detection.
- Authorization must be enforced server-side.

### 5. MITRE ATT&CK Assessment

No specific MITRE ATT&CK technique is claimed as demonstrated.

This local exercise reproduces unauthorized object access through a
web API, not initial compromise of an Internet-facing application.

T1190 (Exploit Public-Facing Application) may be evaluated in a future
DMZ scenario if the simulated activity satisfies its definition.

### 6. Detection Logic

File: portal/detect_bola.py

Alert conditions:

- Event: customer_access
- Result: allowed
- Role: cliente
- Requested customer differs from assigned customer

The detector processes JSONL events on demand.

**Limitation:** Detection depends on trustworthy application audit
fields. It is not an independent SIEM or network-level detection.

### 7. Evidence

| File | Description |
|------|-------------|
| 01-unauthorized-access.png | Unauthorized HTTP 200 |
| 02-bola-detection.png | BOLA detection alert |
| 03-bola-remediation.png | HTTP 403 after remediation |

All screenshots must be sanitized before publication.

### 8. Next Stage

Deploy the enterprise portal in the Containerlab DMZ and investigate
the relationship between application activity, firewall policies,
network telemetry and security detection.

### 9. References

- OWASP API Security Top 10, API1:2023
- NIST SP 800-61 Rev. 3
- MITRE ATT&CK Enterprise

### 10. Scope and Limitations

This exercise uses fictional data and simplified authentication.

The application is not production-ready.

The initial exercise was performed locally, not against a publicly
accessible service. No real-world incident occurred.

## DMZ Integration

The FastAPI portal was deployed as `web01` inside the
Enterprise Security Mirror Containerlab topology.

### Architecture

internet01 -> isp01 -> edge-r01 -> firewall01 -> web01

- Application: FastAPI
- DMZ address: 10.70.50.10
- Published address: 203.0.113.2
- Protocol: HTTPS/TCP 443
- Firewall: nftables with DNAT
- TLS: self-signed certificate for laboratory use

### Validation Results

- Containerlab baseline: 12/12 PASS
- OSPF: 3/3 FULL neighbors
- HTTPS /health: successful
- Authentication through DNAT: successful
- Unauthorized customer access: HTTP 403
- Application audit event: customer_access / denied

### Defensive Findings

The firewall validates network-level access using addresses,
protocols, ports and connection states.

The application provides the identity and authorization context
needed to distinguish legitimate customer access from BOLA.

Because TLS terminates at web01, the firewall does not inspect
the encrypted HTTP request contents.

### Limitations

The application uses simplified authentication and a
self-signed certificate.

The deployment is intended exclusively for an isolated laboratory.
