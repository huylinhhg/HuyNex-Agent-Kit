#!/usr/bin/env python3
"""
Unit Tests for HuyNex Spec-Driven Pre-Flight Gate V3.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_GATE_SCRIPT = REPO_ROOT / "scripts/spec_gate.py"


class TestSpecGate(unittest.TestCase):

    def run_spec_gate(self, spec_path: str, flags: list[str] = None) -> tuple[int, str]:
        cmd = [sys.executable, str(SPEC_GATE_SCRIPT), spec_path] + (flags or [])
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return res.returncode, res.stdout + res.stderr

    def test_fails_closed_when_spec_missing(self):
        code, out = self.run_spec_gate("/tmp/definitely_missing_spec_file.md", ["--skip-tests"])
        self.assertEqual(code, 1)
        self.assertIn("BLOCKED", out)

    def test_fails_closed_when_spec_has_zero_checklist_items(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
            f.write("# Empty Spec\nJust plain prose without any checklist boxes.\n")
            f_path = f.name
        try:
            code, out = self.run_spec_gate(f_path, ["--skip-tests"])
            self.assertEqual(code, 1)
            self.assertIn("BLOCKED", out)
            self.assertIn("0 checklist items", out)
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_passes_when_all_checklist_items_checked(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
            f.write("# Task\n- [x] Item 1\n- [X] Item 2\n")
            f_path = f.name
        try:
            code, out = self.run_spec_gate(f_path, ["--skip-tests"])
            self.assertEqual(code, 0)
            self.assertIn("PASSED", out)
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_blocks_when_checklist_items_incomplete(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
            f.write("# Task\n- [x] Finished item\n- [ ] Pending item\n")
            f_path = f.name
        try:
            code, out = self.run_spec_gate(f_path, ["--skip-tests"])
            self.assertEqual(code, 1)
            self.assertIn("BLOCKED", out)
            self.assertIn("Pending item", out)
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_allow_unverified_cannot_bypass_explicit_failure(self):
        """P1 Test: Incomplete checklist is an explicit failure that CANNOT be bypassed by --allow-unverified."""
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
            f.write("# Incomplete Task\n- [ ] Unfinished deliverable\n")
            f_path = f.name
        try:
            cmd = [sys.executable, str(SPEC_GATE_SCRIPT), f_path, "--skip-tests", "--allow-unverified", "--json"]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            # Must remain BLOCKED with exit code 1!
            self.assertEqual(res.returncode, 1)
            data = json.loads(res.stdout)
            self.assertEqual(data["status"], "BLOCKED")
            self.assertIn("1 pending checklist items", data["failures"])
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_allow_unverified_permits_missing_evidence_as_not_verified(self):
        """P1 Test: Missing spec file is missing evidence and yields NOT_VERIFIED with exit code 0 when permitted."""
        cmd = [sys.executable, str(SPEC_GATE_SCRIPT), "/tmp/definitely_missing_spec.md", "--skip-tests", "--allow-unverified", "--json"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data["status"], "NOT_VERIFIED")

    def test_json_flag_outputs_pure_valid_json(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
            f.write("# Task\n- [x] Item A\n")
            f_path = f.name
        try:
            cmd = [sys.executable, str(SPEC_GATE_SCRIPT), f_path, "--skip-tests", "--json"]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            data = json.loads(res.stdout)
            self.assertEqual(data["status"], "PASS")
            self.assertEqual(data["checklist"]["total"], 1)
            self.assertEqual(data["checklist"]["completed"], 1)
        finally:
            Path(f_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
