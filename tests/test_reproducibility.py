"""Offline regression checks for the ESC-001 reproduction workflow."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from shutil import copyfile

ROOT = Path(__file__).resolve().parents[1]
INFRA = ROOT / "infrastructure/containerlab"
PORTAL = ROOT / "scenarios/esc-001/portal"


class ReproducibilityTests(unittest.TestCase):
    def test_deploy_builds_both_topology_images(self):
        deployment = (INFRA / "scripts/deploy-lab.sh").read_text(encoding="utf-8")
        topology = (INFRA / "lab12.clab.yml").read_text(encoding="utf-8")
        self.assertIn("-t esm-frr-nft:10.6.1", deployment)
        self.assertIn("-t esm-web-portal:0.2", deployment)
        self.assertIn("image: esm-frr-nft:10.6.1", topology)
        self.assertIn("image: esm-web-portal:0.2", topology)
        self.assertLess(
            deployment.index("esm-web-portal:0.2"),
            deployment.index("./scripts/setup-ovs.sh"),
        )

    def test_cleanup_does_not_delete_interfaces_by_name(self):
        cleanup = (INFRA / "scripts/cleanup-ovs.sh").read_text(encoding="utf-8")
        self.assertNotIn("ip link delete", cleanup)
        self.assertIn("clab-esm-", cleanup)
        self.assertIn("ovs-vsctl --if-exists del-br", cleanup)

    def test_detection_complete_and_incomplete_events(self):
        source = PORTAL / "detect_bola.py"
        base = dict(
            event="customer_access",
            username="cliente1",
            result="allowed",
            role="cliente",
            customer_id=2,
            timestamp="2026-11-09T12:00:00Z",
        )
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            (temporary / "logs").mkdir()
            copyfile(source, temporary / "detect_bola.py")
            events = [{**base, "assigned_customer": 1}, base]
            (temporary / "logs/events.jsonl").write_text(
                "".join(json.dumps(e) + "\n" for e in events),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(temporary / "detect_bola.py")],
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(result.stdout.count("[ALERT]"), 1)
            self.assertIn("[RESULT] 1 suspicious access events detected", result.stdout)


if __name__ == "__main__":
    unittest.main()
