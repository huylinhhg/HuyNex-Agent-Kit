#!/usr/bin/env python3
"""
Unit Tests for HuyNex Spec-Driven Pre-Flight Gate V2.
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
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode, res.stdout + res.stderr

    def test_fails_closed_when_spec_missing(self):
        code, out = self.run_spec_gate("/tmp/definitely_missing_spec_file.md", ["--skip-tests"])
        self.assertEqual(code, 1)
        self.assertIn("BLOCKED", out)

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

    def test_json_flag_outputs_pure_valid_json(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".md", delete=False) as f:
            f.write("# Task\n- [x] Item A\n")
            f_path = f.name
        try:
            cmd = [sys.executable, str(SPEC_GATE_SCRIPT), f_path, "--skip-tests", "--json"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            # Must parse without JSONDecodeError
            data = json.loads(res.stdout)
            self.assertEqual(data["status"], "PASS")
            self.assertEqual(data["checklist"]["total"], 1)
            self.assertEqual(data["checklist"]["completed"], 1)
        finally:
            Path(f_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
