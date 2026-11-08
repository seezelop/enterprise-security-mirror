#!/usr/bin/env python3
"""Unit tests for ESM OSPF convergence validation."""

import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "infrastructure/containerlab/validation/wait_for_ospf.py"
)

spec = importlib.util.spec_from_file_location("wait_for_ospf", MODULE_PATH)
ospf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ospf)


def ospf_output(neighbors):
    """Generate representative FRRouting neighbor output."""
    header = "Neighbor ID     Pri State           Up Time"
    rows = [
        f"{router_id}  1 {state}  00:01:00"
        for router_id, state in neighbors
    ]
    return "\n".join([header, *rows])


class TestOSPFConvergence(unittest.TestCase):

    @patch.object(ospf.subprocess, "run")
    def test_three_full_neighbors(self, mock_run):
        mock_run.return_value.stdout = ospf_output([
            ("10.255.255.11", "Full/DR"),
            ("10.255.255.12", "Full/DR"),
            ("10.255.255.13", "Full/Backup"),
        ])

        self.assertEqual(
            ospf.get_full_neighbors(),
            ospf.EXPECTED_NEIGHBORS
        )

    @patch.object(ospf.subprocess, "run")
    def test_incomplete_convergence(self, mock_run):
        mock_run.return_value.stdout = ospf_output([
            ("10.255.255.11", "Full/DR"),
            ("10.255.255.12", "Init/DROther"),
            ("10.255.255.13", "Full/Backup"),
        ])

        self.assertEqual(
            ospf.get_full_neighbors(),
            {"10.255.255.11", "10.255.255.13"}
        )

    @patch.object(ospf.subprocess, "run")
    def test_unexpected_neighbor_is_ignored(self, mock_run):
        mock_run.return_value.stdout = ospf_output([
            ("10.255.255.11", "Full/DR"),
            ("10.255.255.12", "Full/DR"),
            ("10.255.255.99", "Full/DR"),
        ])

        self.assertNotEqual(
            ospf.get_full_neighbors(),
            ospf.EXPECTED_NEIGHBORS
        )

    @patch.object(ospf, "get_full_neighbors")
    def test_successful_wait(self, mock_neighbors):
        mock_neighbors.return_value = ospf.EXPECTED_NEIGHBORS

        self.assertTrue(ospf.wait_for_ospf(timeout=1, interval=1))

    @patch.object(ospf.time, "sleep")
    @patch.object(ospf.time, "monotonic")
    @patch.object(ospf, "get_full_neighbors")
    def test_timeout(self, mock_neighbors, mock_clock, mock_sleep):
        mock_neighbors.return_value = set()
        mock_clock.side_effect = [0, 0, 2]

        self.assertFalse(ospf.wait_for_ospf(timeout=1, interval=1))
        mock_sleep.assert_called_once_with(1)

    @patch.object(ospf, "get_full_neighbors")
    def test_frr_query_failure(self, mock_neighbors):
        mock_neighbors.side_effect = subprocess.CalledProcessError(
            1, ["docker", "exec"]
        )

        with patch.object(ospf.time, "monotonic", side_effect=[0, 0, 2]):
            self.assertFalse(ospf.wait_for_ospf(timeout=1, interval=1))


if __name__ == "__main__":
    unittest.main()
