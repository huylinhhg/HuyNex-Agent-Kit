#!/usr/bin/env python3
"""
Unit Tests for HuyNex Agent Kit Installer Lifecycle, Data Safety & Doctor.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALLER_SCRIPT = REPO_ROOT / "scripts/install.py"

# Add script path for direct unit testing of helper functions
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from install import (
    atomic_write,
    inject_rules_block_safely,
    strip_rules_block_safely,
    configure_claude_guardrail,
    unconfigure_claude_guardrail,
    load_manifest,
    BEGIN_TAG,
    END_TAG,
)


class TestInstallerLifecycle(unittest.TestCase):

    def test_doctor_runs_without_error(self):
        cmd = [sys.executable, str(INSTALLER_SCRIPT), "--doctor"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertIn("DOCTOR VERDICT", res.stdout)

    def test_dry_run_check_is_idempotent_and_non_mutating(self):
        cmd = [sys.executable, str(INSTALLER_SCRIPT), "--check"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(res.returncode, 0)
        self.assertIn("DRY-RUN", res.stdout)


class TestDataSafetyAndNonDestructiveUninstall(unittest.TestCase):

    def test_atomic_write_preserves_content_and_mode(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "test_file.txt"
            atomic_write(target, b"Hello Safe World", mode=0o644)
            self.assertTrue(target.is_file())
            self.assertEqual(target.read_bytes(), b"Hello Safe World")

    def test_atomic_write_preserves_existing_file_mode(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "custom_script.sh"
            target.write_bytes(b"#!/bin/sh\necho 1\n")
            if sys.platform != "win32":
                target.chmod(0o750)

            # Atomic write without specifying mode should preserve permissions
            atomic_write(target, b"#!/bin/sh\necho 2\n")
            self.assertEqual(target.read_bytes(), b"#!/bin/sh\necho 2\n")
            if sys.platform != "win32":
                current_mode = target.stat().st_mode & 0o777
                self.assertEqual(current_mode, 0o750)

    def test_inject_and_strip_preserves_user_customizations(self):
        """P0 Test: Verifies that pre-existing user content is NEVER lost during install or uninstall."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            user_file = Path(tmp_dir) / "CLAUDE.md"
            original_user_content = (
                "# User Personal System Prompt\n\n"
                "You are an assistant specialized in Rust and Linux.\n"
                "Never do force pushes.\n"
            )
            user_file.write_text(original_user_content, encoding="utf-8")

            # 1. Simulate install: inject managed block
            managed_block = f"{BEGIN_TAG}\n# Managed Governance Block\n{END_TAG}\n"
            injected_content, changed = inject_rules_block_safely(user_file, managed_block)
            self.assertTrue(changed)
            user_file.write_text(injected_content, encoding="utf-8")

            # Ensure both user content and managed block exist
            self.assertIn("User Personal System Prompt", user_file.read_text())
            self.assertIn("Managed Governance Block", user_file.read_text())

            # 2. Simulate uninstall: strip managed block
            cleaned_text, was_stripped = strip_rules_block_safely(user_file)
            self.assertTrue(was_stripped)
            user_file.write_text(cleaned_text, encoding="utf-8")

            # P0 Assertion: User's original content must be identical!
            self.assertEqual(user_file.read_text().strip(), original_user_content.strip())
            self.assertNotIn("Managed Governance Block", user_file.read_text())
            self.assertNotIn(BEGIN_TAG, user_file.read_text())

    def test_v031_legacy_manifest_migration(self):
        """P0 Test: Migrates v0.3.1 JSON array manifest into v0.3.3 dict manifest without crash."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_file = Path(tmp_dir) / "installed_manifest.json"
            legacy_data = [
                {
                    "path": "/home/user/.claude/rules/01-communication.md",
                    "type": "RULE_MODULE",
                    "installed_at": "2026-11-23T17:00:00Z",
                    "sha256": "abc12345"
                },
                {
                    "path": "/home/user/.claude/CLAUDE.md",
                    "type": "ROOT_INSTRUCTION",
                    "installed_at": "2026-11-23T17:00:00Z",
                    "sha256": "def67890"
                }
            ]
            manifest_file.write_text(json.dumps(legacy_data), encoding="utf-8")

            # Load must automatically migrate from list to dict with 'entries'
            loaded = load_manifest(manifest_file)
            self.assertIsInstance(loaded, dict)
            self.assertIn("entries", loaded)
            self.assertEqual(len(loaded["entries"]), 2)
            self.assertIn("/home/user/.claude/CLAUDE.md", loaded["entries"])
            self.assertEqual(loaded["entries"]["/home/user/.claude/CLAUDE.md"]["managed_mode"], "injected_block")

    def test_guardrail_hook_lifecycle_in_settings_json(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_file = Path(tmp_dir) / "settings.json"
            hook_script = Path(tmp_dir) / "guardrail.py"
            hook_script.write_text("#!/usr/bin/env python3\n")

            # 1. Register hook
            registered = configure_claude_guardrail(settings_file, hook_script, dry_run=False)
            self.assertTrue(registered)
            data = json.loads(settings_file.read_text())
            self.assertTrue(any("guardrail.py" in str(h) for h in data["hooks"]["PreToolUse"]))

            # 2. Unregister hook
            unregistered = unconfigure_claude_guardrail(settings_file)
            self.assertTrue(unregistered)
            data_after = json.loads(settings_file.read_text())
            self.assertFalse(any("guardrail.py" in str(h) for h in data_after.get("hooks", {}).get("PreToolUse", [])))

    def test_corrupt_settings_json_not_overwritten(self):
        """P0 Test: Verifies that corrupt JSON settings are NOT replaced with empty {}."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_file = Path(tmp_dir) / "settings.json"
            corrupt_content = "{ this is invalid json ;;"
            settings_file.write_text(corrupt_content, encoding="utf-8")

            hook_script = Path(tmp_dir) / "guardrail.py"
            hook_script.write_text("#!/usr/bin/env python3\n")

            # Should fail gracefully and NOT overwrite corrupt settings
            registered = configure_claude_guardrail(settings_file, hook_script, dry_run=False)
            self.assertFalse(registered)
            self.assertEqual(settings_file.read_text(), corrupt_content)


if __name__ == "__main__":
    unittest.main()
