#!/usr/bin/env python3
"""Wait until all expected ESM OSPF neighbors reach FULL state."""

import argparse
import re
import subprocess
import sys
import time

ROUTER = "clab-esm-core-r01"

EXPECTED_NEIGHBORS = {
    "10.255.255.11",
    "10.255.255.12",
    "10.255.255.13",
}

NEIGHBOR_PATTERN = re.compile(
    r"^\s*(\d{1,3}(?:\.\d{1,3}){3})\s+"
    r"\d+\s+(\S+)"
)


def get_full_neighbors():
    """Query FRRouting and return the expected neighbors in FULL state."""
    result = subprocess.run(
        [
            "docker", "exec", ROUTER,
            "vtysh", "-c", "show ip ospf neighbor",
        ],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )

    full_neighbors = set()

    for line in result.stdout.splitlines():
        match = NEIGHBOR_PATTERN.match(line)

        if not match:
            continue

        router_id, state = match.groups()

        if router_id in EXPECTED_NEIGHBORS and state.split("/")[0].upper() == "FULL":
            full_neighbors.add(router_id)

    return full_neighbors


def wait_for_ospf(timeout, interval):
    """Poll OSPF neighbors until convergence or timeout."""
    deadline = time.monotonic() + timeout

    while True:
        try:
            full_neighbors = get_full_neighbors()
        except (subprocess.SubprocessError, OSError) as exc:
            print(f"[WARN] No se pudo consultar OSPF: {exc}", flush=True)
            full_neighbors = set()

        missing = EXPECTED_NEIGHBORS - full_neighbors

        print(
            f"[INFO] OSPF FULL: "
            f"{len(full_neighbors)}/{len(EXPECTED_NEIGHBORS)} "
            f"| Pendientes: {', '.join(sorted(missing)) or 'ninguno'}",
            flush=True,
        )

        if not missing:
            print("[PASS] OSPF convergió: 3/3 vecinos FULL.")
            return True

        remaining = deadline - time.monotonic()

        if remaining <= 0:
            print("[FAIL] OSPF no convergió dentro del tiempo establecido.")
            return False

        time.sleep(min(interval, remaining))


def main():
    parser = argparse.ArgumentParser(
        description="Wait for ESM OSPF convergence."
    )

    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--interval", type=int, default=5)

    args = parser.parse_args()

    if args.timeout <= 0 or args.interval <= 0:
        parser.error("timeout e interval deben ser mayores que cero")

    return 0 if wait_for_ospf(args.timeout, args.interval) else 1


if __name__ == "__main__":
    sys.exit(main())
