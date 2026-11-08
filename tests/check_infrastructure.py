#!/usr/bin/env python3
"""Validaciones estáticas de Enterprise Security Mirror."""

import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "infrastructure/containerlab"

BRIDGES = {
    "esm-core-sw", "esm-users-sw", "esm-servers-sw",
    "esm-mgmt-sw", "esm-dmz-sw", "esm-branch-sw1"
}

def read(path):
    return (BASE / path).read_text(encoding="utf-8")

def check(condition, message):
    if not condition:
        raise AssertionError(message)

topology = read("lab12.clab.yml")

# Identidad del nuevo laboratorio
check(topology.startswith("name: esm\n"), "Topología incorrecta")
check("network: esm-mgmt" in topology, "Red de gestión incorrecta")
check("172.20.20.1" not in topology, "Ruta de gestión anterior")

# Nodos
nodes = set(re.findall(r"^    ([\w-]+):\s*$", topology, re.M))

check(len(nodes) == 24, "Cantidad inesperada de nodos")
check(BRIDGES.issubset(nodes), "Faltan bridges ESM")

# Enlaces
links = re.findall(
    r'- endpoints:\s*\["([^"]+)",\s*"([^"]+)"\]',
    topology
)

check(len(links) == 23, "Cantidad inesperada de enlaces")

ovs_ports = set()

for link in links:
    for endpoint in link:
        node, port = endpoint.split(":")

        check(node in nodes, f"Nodo inexistente: {node}")

        if node in BRIDGES:
            check(port.startswith("e-"), f"Puerto incorrecto: {port}")
            check(len(port) <= 15, f"Puerto demasiado largo: {port}")
            check(port not in ovs_ports, f"Puerto duplicado: {port}")
            ovs_ports.add(port)

# Scripts OVS
setup = read("scripts/setup-ovs.sh")
cleanup = read("scripts/cleanup-ovs.sh")
switching = read("scripts/configure-switching.sh")

for bridge in BRIDGES:
    check(bridge in setup, f"Bridge ausente en setup: {bridge}")
    check(bridge in cleanup, f"Bridge ausente en cleanup: {bridge}")

for port in re.findall(r"set port ([\w-]+)", switching):
    check(port in ovs_ports, f"Puerto inexistente: {port}")

# Evitar operaciones OVS sobre bridges del Lab 12
for script in (setup, cleanup, switching):

    # Ignorar comentarios y líneas vacías.
    active_lines = [
        line.split("#", 1)[0].strip()
        for line in script.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    active_content = "\n".join(active_lines)

    for bridge in BRIDGES:
        original = bridge.removeprefix("esm-")
        pattern = rf"(?<![\w-]){re.escape(original)}(?![\w-])"

        check(
            not re.search(pattern, active_content),
            f"Referencia activa al bridge original: {original}"
        )


# Protección del despliegue
deploy = read("scripts/deploy-lab.sh")

check(
    "./scripts/preflight.sh" in deploy,
    "El despliegue no ejecuta el preflight"
)

check(
    "clab-lab12-" in deploy and "exit 1" in deploy,
    "Falta protección del Lab 12"
)

check(
    "containerlab deploy -t lab12.clab.yml" in deploy,
    "Falta el despliegue de la topología ESM"
)

check(
    "containerlab destroy" not in deploy,
    "El despliegue contiene una operación destructiva"
)

check(
    "cleanup-ovs.sh" not in deploy,
    "El despliegue ejecuta limpieza automática de OVS"
)

check(
    "rm -rf" not in deploy,
    "El despliegue contiene una eliminación recursiva"
)



# Pruebas funcionales definidas
policy = json.loads(read("validation/policy.yaml"))

check(len(policy["tests"]) == 12, "Cantidad incorrecta de pruebas")

for test in policy["tests"]:
    for field in ("source", "container"):
        if field in test:
            name = test[field]
            check(name.startswith("clab-esm-"),
                  f"Referencia incorrecta: {name}")
            check(name.removeprefix("clab-esm-") in nodes,
                  f"Contenedor inexistente: {name}")

print("PASS: Topología ESM")
print("PASS: 24 nodos y 23 enlaces")
print("PASS: Bridges e interfaces OVS")
print("PASS: Scripts de infraestructura")
print("PASS: Protección del Lab 12 original")
print("PASS: 12 definiciones de pruebas")

# Validaciones del procedimiento de despliegue seguro
preflight = read("scripts/preflight.sh")

check(
    deploy.index("./scripts/preflight.sh")
    < deploy.index("docker build")
    < deploy.index("./scripts/setup-ovs.sh")
    < deploy.index("containerlab deploy"),
    "El orden de despliegue es incorrecto"
)

for required in (
    "docker ps -a",
    "docker network inspect esm-mgmt",
    "ovs-vsctl br-exists",
    "ip link show dev",
    "clab-esm",
):
    check(
        required in preflight,
        f"Falta comprobación en preflight: {required}"
    )

for forbidden in (
    "containerlab destroy",
    "cleanup-ovs.sh",
    "rm -rf",
):
    check(
        forbidden not in deploy,
        f"Operación no permitida en deploy: {forbidden}"
    )

print("PASS: Preflight y orden de despliegue seguro")
