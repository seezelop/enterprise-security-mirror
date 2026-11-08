#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[INFO] Verificando requisitos y conflictos ESM..."

for cmd in docker containerlab ovs-vsctl ip; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "[ERROR] Comando no disponible: $cmd" >&2
        exit 1
    fi
done

if ! docker info >/dev/null 2>&1; then
    echo "[ERROR] Docker no está accesible." >&2
    exit 1
fi

if ! sudo -n ovs-vsctl list-br >/dev/null 2>&1; then
    echo "[ERROR] No se pudo consultar Open vSwitch sin solicitar contraseña." >&2
    echo "[INFO] Ejecutá 'sudo -v' y repetí el preflight." >&2
    exit 1
fi

# No desplegar mientras existan contenedores del Lab 12 activos.
if docker ps --format '{{.Names}}' |
    grep -q '^clab-lab12-'; then
    echo "[ERROR] El Lab 12 original tiene contenedores activos." >&2
    exit 1
fi

# Detenerse ante cualquier contenedor ESM, incluso detenido.
if docker ps -a --format '{{.Names}}' |
    grep -q '^clab-esm-'; then
    echo "[ERROR] Ya existen contenedores ESM." >&2
    exit 1
fi

# No reutilizar una red de gestión preexistente.
if docker network inspect esm-mgmt >/dev/null 2>&1; then
    echo "[ERROR] La red Docker esm-mgmt ya existe." >&2
    exit 1
fi

# No modificar bridges preexistentes.
for bridge in \
    esm-core-sw esm-users-sw esm-servers-sw \
    esm-mgmt-sw esm-dmz-sw esm-branch-sw1
do
    if sudo -n ovs-vsctl br-exists "$bridge"; then
        echo "[ERROR] Ya existe el bridge $bridge." >&2
        exit 1
    fi
done

# No reutilizar interfaces previstas por la topología.
while IFS= read -r iface; do
    if ip link show dev "$iface" >/dev/null 2>&1; then
        echo "[ERROR] Ya existe la interfaz $iface." >&2
        exit 1
    fi
done < <(
    grep -oE 'esm-[a-z0-9-]+:e-[a-z0-9-]+' lab12.clab.yml |
    cut -d: -f2 |
    sort -u
)

if [[ -e clab-esm ]]; then
    echo "[ERROR] Ya existe el directorio clab-esm." >&2
    exit 1
fi

echo "[PASS] No se detectaron conflictos de recursos ESM."
echo "[PASS] El Lab 12 original no tiene contenedores activos."
echo "[PASS] Preflight completado."
