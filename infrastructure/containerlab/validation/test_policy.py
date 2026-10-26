#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path


POLICY_FILE = Path(__file__).with_name("policy.yaml")


def load_policy():
    try:
        with POLICY_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print(f"[ERROR] POLICY FILE NOT FOUND: {POLICY_FILE}")
        raise

    except json.JSONDecodeError as exc:
        print(f"[ERROR] INVALID POLICY FILE: {exc}")
        raise


def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        return result.returncode, result.stdout.strip(), result.stderr.strip()

    except subprocess.TimeoutExpired:
        return 124, "", "COMMAND TIMEOUT"

    except Exception as exc:
        return 1, "", str(exc)


def test_tcp(test):
    try:
        command = [
            "docker",
            "exec",
            test["source"],
            "sh",
            "-c",
            f'nc -w 2 {test["destination"]} {test["port"]}',
        ]

        returncode, stdout, stderr = run_command(command)

        expected = test["expected"]

        if expected == "allow":
            expected_banner = test.get("banner", "")

            passed = (
                returncode == 0
                and expected_banner in stdout
            )

        elif expected == "deny":
            passed = returncode != 0

        else:
            return False, f'UNKNOWN EXPECTED RESULT: {expected}'

        details = stdout or stderr or f"EXIT={returncode}"

        return passed, details

    except Exception as exc:
        return False, str(exc)


def test_ospf_neighbors(test):
    try:
        command = [
            "docker",
            "exec",
            test["container"],
            "vtysh",
            "-c",
            "show ip ospf neighbor",
        ]

        returncode, stdout, stderr = run_command(command)

        full_neighbors = stdout.count("Full/")

        passed = (
            returncode == 0
            and full_neighbors == test["expected_full"]
        )

        details = (
            f"FULL_NEIGHBORS={full_neighbors}/"
            f'{test["expected_full"]}'
        )

        return passed, details

    except Exception as exc:
        return False, str(exc)


def run_test(test):
    try:
        test_type = test["type"]

        if test_type == "tcp":
            return test_tcp(test)

        if test_type == "ospf_neighbors":
            return test_ospf_neighbors(test)

        return False, f"UNSUPPORTED TEST TYPE: {test_type}"

    except Exception as exc:
        return False, str(exc)


def main():
    passed_count = 0
    failed_count = 0

    try:
        policy = load_policy()

        print()
        print("LAB 12 - ENTERPRISE NETWORK SECURITY VALIDATION")
        print("=" * 58)

        for test in policy["tests"]:
            passed, details = run_test(test)

            if passed:
                passed_count += 1
                status = "PASS"
            else:
                failed_count += 1
                status = "FAIL"

            print(f"[{status}] {test['name']}")
            print(f"       {details}")

        total = passed_count + failed_count

        print()
        print("=" * 58)
        print(
            f"RESULT: {passed_count}/{total} PASSED "
            f"| {failed_count} FAILED"
        )

        if failed_count == 0:
            print("[PASS] LAB 12 SECURITY POLICY VALIDATION SUCCESSFUL")
            return 0

        print("[FAIL] LAB 12 SECURITY POLICY VALIDATION FAILED")
        return 1

    except Exception as exc:
        print(f"[ERROR] VALIDATION ABORTED: {exc}")
        return 1

    finally:
        print("=" * 58)


if __name__ == "__main__":
    sys.exit(main())
