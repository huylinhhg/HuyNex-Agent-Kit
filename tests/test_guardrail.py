#!/usr/bin/env python3
"""
Unit and Adversarial Tests for HuyNex Security Guardrails V3.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUARDRAIL_SCRIPT = REPO_ROOT / "scripts/guardrail.py"


class TestSecurityGuardrails(unittest.TestCase):

    def run_guardrail(self, command: str) -> tuple[int, str]:
        p = subprocess.Popen(
            [sys.executable, str(GUARDRAIL_SCRIPT)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        payload = json.dumps({"tool_input": {"command": command}})
        out, err = p.communicate(payload)
        return p.returncode, err

    def test_blocks_direct_force_push(self):
        code, err = self.run_guardrail("git push --force origin main")
        self.assertEqual(code, 2)
        self.assertIn("BLOCKED", err)

        code, err = self.run_guardrail("git push -f origin main")
        self.assertEqual(code, 2)

    def test_blocks_refspec_force_push(self):
        code, err = self.run_guardrail("git push origin +main")
        self.assertEqual(code, 2)

    def test_blocks_force_with_lease(self):
        code, err = self.run_guardrail("git push --force-with-lease origin main")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("git push --force-with-lease=origin/main")
        self.assertEqual(code, 2)

    def test_blocks_eval_and_subshell_bypass(self):
        code, err = self.run_guardrail('eval "git push --force"')
        self.assertEqual(code, 2)

        # Compound commands inside eval separated by semicolon or &&
        code, err = self.run_guardrail('eval "git status ; git push --force"')
        self.assertEqual(code, 2)

        code, err = self.run_guardrail('eval "echo safe && git reset --hard"')
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("sh -c 'git reset --hard'")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("sh -c 'git status ; git clean -fd'")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("bash -c 'git clean -fd'")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail('python3 -c "import os; os.system(\x27git push --force\x27)"')
        self.assertEqual(code, 2)

    def test_blocks_command_substitution(self):
        code, err = self.run_guardrail("echo $(git push origin +main)")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("echo `git reset --hard`")
        self.assertEqual(code, 2)

    def test_blocks_git_global_flags_bypass(self):
        code, err = self.run_guardrail("git -C . push --force")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("git --git-dir=.git push -f")
        self.assertEqual(code, 2)

    def test_blocks_hard_reset(self):
        code, err = self.run_guardrail("git reset --hard HEAD~1")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("git reset --hard=HEAD~1")
        self.assertEqual(code, 2)

    def test_blocks_destructive_clean(self):
        code, err = self.run_guardrail("git clean -fd")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("git clean -f")
        self.assertEqual(code, 2)

    def test_blocks_force_branch_delete(self):
        code, err = self.run_guardrail("git branch -D feature/test")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("git branch --delete-force=feature/test")
        self.assertEqual(code, 2)

    def test_blocks_root_destruction(self):
        code, err = self.run_guardrail("rm -rf /")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("rm -rf ~")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("rm -rf .")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("rm -rf *")
        self.assertEqual(code, 2)

    def test_blocks_compound_destructive_commands(self):
        code, err = self.run_guardrail("git status && git push --force")
        self.assertEqual(code, 2)

        code, err = self.run_guardrail("npm test || rm -rf /")
        self.assertEqual(code, 2)

    def test_allows_safe_operations(self):
        safe_commands = [
            "git status",
            "git pull --ff-only origin main",
            "git push origin main",
            "git branch -d merged-feature",
            'echo "hello && world"',
            'echo "safe || safe"',
            "npm test",
            "pytest tests/",
            "rm -rf work/temp_scratch",
            "python3 -m unittest"
        ]
        for cmd in safe_commands:
            code, err = self.run_guardrail(cmd)
            self.assertEqual(code, 0, f"Expected safe command to pass, but got code {code}: {cmd}")


if __name__ == "__main__":
    unittest.main()
