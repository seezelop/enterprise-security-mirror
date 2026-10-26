#!/usr/bin/env python3

from pathlib import Path
import json
import re
import subprocess

ROOT = Path.home() / "Projects/enterprise-security-mirror"
BASE = ROOT / "infrastructure/containerlab"
SHA = "1635767a152fcd9c20e4a78eef9bb5968cb44d7e"

BRIDGES = (
    "core-sw", "users-sw", "servers-sw",
    "mgmt-sw", "dmz-sw", "branch-sw1"
)

NAMES = {name: "esm-" + name for name in BRIDGES}


def read(path):
    return path.read_text(encoding="utf-8")


def write(path, content):
    path.write_text(content, encoding="utf-8")


# Verificaciones de seguridad
assert BASE.joinpath("SOURCE_COMMIT.txt").read_text().strip() == SHA

repo = subprocess.check_output(
    ["git", "-C", str(ROOT), "rev-parse", "--show-toplevel"],
    text=True
).strip()

assert repo == str(ROOT), "Repositorio incorrecto"

branch = subprocess.check_output(
    ["git", "-C", str(ROOT), "branch", "--show-current"],
    text=True
).strip()

assert branch.startswith("feat/"), "Usar una rama feat/"

topology = BASE / "lab12.clab.yml"
content = read(topology)

assert content.startswith("name: lab12\n"), "Topologia inesperada"

# Cambiar nombre de topologia y de imagen propia
content = content.replace("name: lab12\n", "name: esm\n", 1)
content = content.replace(
    "image: lab12-frr-nft:10.6.1",
    "image: esm-frr-nft:10.6.1"
)

# Renombrar switches OVS
for old, new in NAMES.items():
    content = content.replace(f"    {old}:\n", f"    {new}:\n")

# Renombrar interfaces del lado OVS
ports = {}

def replace_endpoint(match):
    node, port = match.groups()

    if node not in NAMES:
        return match.group(0)

    new_port = "e-" + port
    assert len(new_port) <= 15, f"Interfaz demasiado larga: {new_port}"

    ports[port] = new_port
    return f'"{NAMES[node]}:{new_port}"'

content = re.sub(
    r'"([^":]+):([^":]+)"',
    replace_endpoint,
    content
)

assert len(ports) >= 16, "Cantidad inesperada de interfaces OVS"

# Preparar todos los cambios antes de escribir
changes = {topology: content}

scripts = BASE / "scripts"

setup = read(scripts / "setup-ovs.sh")
for old, new in NAMES.items():
    setup = re.sub(r"\b" + re.escape(old) + r"\b", new, setup)

changes[scripts / "setup-ovs.sh"] = setup

switching = read(scripts / "configure-switching.sh")

for old, new in ports.items():
    switching = re.sub(
        r"(\bset port\s+)" + re.escape(old) + r"(?=\s)",
        lambda m: m.group(1) + new,
        switching
    )

changes[scripts / "configure-switching.sh"] = switching

# Limpieza exclusiva de los recursos ESM
cleanup = """#!/usr/bin/env bash
set -euo pipefail

for bridge in """ + " ".join(NAMES.values()) + """; do
  sudo ovs-vsctl --if-exists del-br "$bridge"
done

for iface in """ + " ".join(sorted(set(ports.values()))) + """; do
  sudo ip link delete "$iface" 2>/dev/null || true
done
"""

changes[scripts / "cleanup-ovs.sh"] = cleanup

# Despliegue con proteccion del Lab 12 original
deploy = read(scripts / "deploy-lab.sh")
deploy = deploy.replace("lab12-frr-nft:10.6.1", "esm-frr-nft:10.6.1")
deploy = deploy.replace("clab-lab12", "clab-esm")

guard = """
if docker ps --filter 'name=clab-lab12-' --format '{{.Names}}' | grep -q .; then
    echo "ERROR: Lab 12 original sigue activo. No desplegar ESM." >&2
    exit 1
fi
"""

assert "set -euo pipefail\n" in deploy

deploy = deploy.replace(
    "set -euo pipefail\n",
    "set -euo pipefail\n" + guard,
    1
)

changes[scripts / "deploy-lab.sh"] = deploy

# Adaptar nombres de contenedores en las pruebas
policy = BASE / "validation/policy.yaml"
updated_policy = read(policy).replace("clab-lab12-", "clab-esm-")

assert len(json.loads(updated_policy)["tests"]) == 12
changes[policy] = updated_policy

# Identificadores de eventos propios del proyecto
for relative in (
    "configs/core-r01/internal-policy.nft",
    "configs/firewall01/nftables.conf"
):
    path = BASE / relative
    changes[path] = read(path).replace("LAB12-", "ESM-")

# Anotaciones de la topologia
annotations = BASE / "lab12.clab.yml.annotations.json"
data = json.loads(read(annotations))

for node in data.get("nodeAnnotations", []):
    if node.get("id") in NAMES:
        node["id"] = NAMES[node["id"]]

changes[annotations] = json.dumps(data, indent=2) + "\n"

# Escribir cambios solo en el nuevo repositorio
for path, new_content in changes.items():
    assert path.resolve().is_relative_to(ROOT.resolve())
    write(path, new_content)

print("PASS: topologia esm preparada")
print("PASS: 6 bridges OVS renombrados")
print("PASS: interfaces OVS independientes")
print("PASS: 12 pruebas reasignadas")
print("PASS: scripts adaptados")
print("NO se modificaron contenedores ni redes en ejecucion")
