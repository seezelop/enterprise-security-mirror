# ESC-001: Reproduce the Enterprise Security Mirror Lab

This guide covers a **fresh, isolated Linux host**, not an existing working deployment. Follow it only on your own authorized machine. The project has been exercised on Ubuntu, but successful deployment on every Linux distribution or hardware configuration is **not guaranteed**.

## 1. Prerequisites

- Linux host with a running Docker Engine and permission to issue `docker` commands.
- Containerlab CLI (`containerlab`), Open vSwitch (`ovs-vsctl`), `iproute2` (`ip`), Git, Python 3 and `sudo`.
- Working Internet access for pulling base images and installing image dependencies on first build.
- Sufficient resources for **18 Linux containers**, six OVS bridges and 23 links. Actual RAM/CPU requirements depend on the host; monitor `free -h` and `docker stats`.
- `sudo -v` before running the deployment, because Containerlab and OVS create privileged network resources.
- No running original `clab-lab12-*` deployment; no existing ESM containers, bridges, management network or runtime directory. The preflight refuses conflicts rather than deleting them.

Check tools:

```bash
docker info >/dev/null
containerlab version
sudo ovs-vsctl show
ip -V
python3 --version
```

For Docker/Containerlab/Open vSwitch installation, follow their official OS-specific installation instructions. The scripts do not install host prerequisites.

## 2. Clone and deploy

```bash
git clone https://github.com/seezelop/enterprise-security-mirror.git
cd enterprise-security-mirror
sudo -v
cd infrastructure/containerlab
./scripts/preflight.sh
./scripts/deploy-lab.sh
```

This builds `esm-frr-nft:10.6.1` and `esm-web-portal:0.2` locally, creates the six ESM-specific OVS bridges, deploys `lab12.clab.yml` (lab name `esm`), configures VLANs, waits for OSPF and runs the live policy tests. The expected result on a successfully deployed lab is:

```text
RESULT: 12/12 PASSED | 0 FAILED
```

**Do not run the deployment script twice**. It intentionally refuses existing ESM resources. If it fails partway through, inspect the state and use the scoped cleanup procedure below after confirming ownership.

## 3. Validate the live topology

From `infrastructure/containerlab/`:

```bash
sudo containerlab inspect -t lab12.clab.yml
docker exec clab-esm-core-r01 vtysh -c 'show ip ospf neighbor'
python3 validation/test_policy.py
docker exec clab-esm-web01 ip addr show dev eth1
```

`web01` should have `10.70.50.10/24` on `eth1`. The policy suite verifies three OSPF neighbors, allowed and denied flows, DMZ isolation, and the portal's HTTPS `/health` endpoint through DNAT.

From the simulated external client:

```bash
docker exec clab-esm-internet01 wget --no-check-certificate -qO- https://203.0.113.2/health
```

Expected JSON contains `"status":"ok"`. Certificate validation is deliberately disabled **only inside this isolated demo**, because `web01` generates its own self-signed certificate.

## 4. Reproduce authorized and denied application access

The current deployed application has the authorization **fix enabled**. Use synthetic credentials only.

From the repository root:

```bash
TOKEN=$(docker exec clab-esm-internet01 \
  wget --no-check-certificate -qO- \
  --header='Content-Type: application/json' \
  --post-data='{"username":"cliente1","password":"Cliente123!"}' \
  https://203.0.113.2/login | \
  python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')

docker exec clab-esm-internet01 \
  wget --no-check-certificate -qO- \
  --header="Authorization: Bearer $TOKEN" \
  https://203.0.113.2/customers/1

docker exec clab-esm-internet01 \
  wget --no-check-certificate -S -O /dev/null \
  --header="Authorization: Bearer $TOKEN" \
  https://203.0.113.2/customers/2

unset TOKEN
```

The first GET should succeed (HTTP 200). The second is correctly rejected (HTTP 403). Do not print, screenshot or commit the bearer token.

Review the actual application's JSONL audit log:

```bash
docker exec clab-esm-web01 sh -c 'tail -n 5 /app/logs/events.jsonl'
docker exec clab-esm-web01 python /app/detect_bola.py
```

The detector only alerts on **successful** cross-customer accesses. A blocked attempt yields an audit record with `result=denied`; it does not meet this detector's alert condition. The demo intentionally has no central SIEM or separate IDS.

## 5. Reproduce a BOLA detection with isolated synthetic events

The repository contains the **remediated** application; it does not automatically turn authorization off. The historical vulnerable HTTP 200 result is documented in [the experiment report](README.md), not implemented as a separate vulnerable container.

To exercise detection safely **without changing application authorization or persistent logs**, run the original detector against synthetic JSONL events in a temporary folder:

```bash
cd "$(git rev-parse --show-toplevel)"
python3 - <<'PY'
import json
import subprocess
import tempfile
from pathlib import Path
from shutil import copyfile

source = Path("scenarios/esc-001/portal/detect_bola.py")
base = {
    "event": "customer_access",
    "username": "cliente1",
    "result": "allowed",
    "role": "cliente",
    "customer_id": 2,
    "timestamp": "2026-11-09T12:00:00Z",
}
with tempfile.TemporaryDirectory() as directory:
    dest = Path(directory)
    (dest / "logs").mkdir()
    copyfile(source, dest / "detect_bola.py")
    complete = {**base, "assigned_customer": 1}
    incomplete = {**base, "timestamp": "2026-11-09T12:01:00Z"}
    (dest / "logs/events.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in (complete, incomplete)),
        encoding="utf-8",
    )
    subprocess.run(["python3", str(dest / "detect_bola.py")], check=True)
PY
```

Expected: **one** BOLA alert from the complete event; the event missing `assigned_customer` does not trigger this detector. This tests an **observability blind spot**, not evasion of the application's authorization check.

## 6. Teardown, only for your ESM lab

From `infrastructure/containerlab/`:

```bash
sudo containerlab destroy -t lab12.clab.yml
docker ps -a --format '{{.Names}}' | grep '^clab-esm-' || true
./scripts/cleanup-ovs.sh
```

Only run cleanup after confirming the ESM containers are gone. The cleanup script removes exclusively the six named `esm-*` bridges; it does **not** clean up arbitrary interfaces. If stale ESM interfaces, Docker management networks or generated directories remain, inspect them manually before taking any destructive action; the next preflight will flag conflicts. **Do not run `docker system prune` or clean original Lab 12 bridges.**

Containerlab-managed topology links may need a fresh deploy after restarting the Docker daemon/host; `docker ps` showing containers as running alone does not prove the topology dataplane is intact.

## 7. Reproducibility limitations

- GitHub Actions covers static/offline validations, not a 24-node live network integration test.
- Host kernel modules, Docker permissions, OVS state, package repositories and available resources can alter deployment outcomes.
- Demo HTTPS has a short-lived self-signed certificate.
- Some other TCP listeners remain intentionally synthetic (Netcat).
- The historical *vulnerable HTTP 200* BOLA step is documented rather than shipped as an enabled vulnerable runtime. The current exercises reproduce the remediation and detector behavior safely.
- The real source of truth is the versioned topology, code, policies and application logs; images and screenshots alone are not verification.
