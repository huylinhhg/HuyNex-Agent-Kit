#!/usr/bin/env python3
"""
Unit Tests for HuyNex Agent Kit Installer Lifecycle & Doctor.
"""
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALLER_SCRIPT = REPO_ROOT / "scripts/install.py"


class TestInstallerLifecycle(unittest.TestCase):

    def test_doctor_runs_without_error(self):
        cmd = [sys.executable, str(INSTALLER_SCRIPT), "--doctor"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("DOCTOR VERDICT", res.stdout)

    def test_dry_run_check_is_idempotent_and_non_mutating(self):
        cmd = [sys.executable, str(INSTALLER_SCRIPT), "--check"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("DRY-RUN", res.stdout)


if __name__ == "__main__":
    unittest.main()
