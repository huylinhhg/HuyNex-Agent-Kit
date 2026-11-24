#!/usr/bin/env python3
"""
State Machine Lifecycle & Data Safety Regression Test Suite (test_state_machine_lifecycle.py)
--------------------------------------------------------------------------------------------
Implements a strict State Machine test that transitions through:
  State 0: Pre-existing User Environment (arbitrary bytes, CRLF, custom skills)
  -> Transition 1: Fresh Install (v0.3.5)
  -> Transition 2: Idempotent Re-install (immutable backups & ownership)
  -> Transition 3: Post-Install User Modifications (file mutations)
  -> Transition 4: Legacy Multi-Version Upgrade (v0.3.1 -> v0.3.5 UNKNOWN ownership)
  -> Transition 5: Non-Destructive Transactional Uninstall (Byte-for-byte fidelity)
  -> Transition 6: Partial Failure & Manifest Transaction Preservation
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from install import (
    cmd_install,
    cmd_uninstall,
    load_manifest,
    save_manifest,
    sha256_file,
    atomic_write,
    create_unique_backup_dir,
    write_immutable_backup_file,
    preserve_user_modified_file,
    strip_rules_block_safely,
    inject_rules_block_safely,
)


class TestStateMachineLifecycle(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="huynex_state_machine_")
        self.home = Path(self.tmp_dir)

        # Patch environment
        self.orig_env = os.environ.copy()
        os.environ["HOME"] = str(self.home)
        os.environ["USERPROFILE"] = str(self.home)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.orig_env)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_complete_state_machine_lifecycle(self):
        # =====================================================================
        # STATE 0: Pre-existing User Environment
        # =====================================================================
        claude_dir = self.home / ".claude"
        claude_dir.mkdir(parents=True)
        # CRLF with trailing spaces to test byte-for-byte fidelity
        orig_claude_bytes = b"# Personal System Prompt\r\nBe ultra concise.   \r\n\r\n"
        claude_file = claude_dir / "CLAUDE.md"
        claude_file.write_bytes(orig_claude_bytes)
        claude_sha_orig = hashlib.sha256(orig_claude_bytes).hexdigest()

        # Pre-existing skill with Content A
        skill_dir = self.home / ".agents/skills/data-conservation-gate"
        skill_dir.mkdir(parents=True)
        orig_skill_bytes = b"---\nname: data-conservation-gate\n---\n# User Original Skill A\n"
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_bytes(orig_skill_bytes)
        skill_sha_orig = hashlib.sha256(orig_skill_bytes).hexdigest()

        # Pre-existing cursor custom rule
        cursor_rules = self.home / ".cursor/rules"
        cursor_rules.mkdir(parents=True)
        cursor_custom_bytes = b"---\ndescription: \"Custom\"\nglobs: \"*\"\n---\n# Custom Rule\n"
        cursor_file = cursor_rules / "user_custom.mdc"
        cursor_file.write_bytes(cursor_custom_bytes)

        # =====================================================================
        # TRANSITION 1: Fresh Install (v0.3.5)
        # =====================================================================
        cmd_install(is_all=True, dry_run=False)

        manifest_file = self.home / ".huynex/installed_manifest.json"
        self.assertTrue(manifest_file.is_file(), "Manifest must exist after install")
        manifest = load_manifest(manifest_file)
        entries = manifest.get("entries", {})

        # Verify CLAUDE.md ownership
        claude_entry = entries.get(str(claude_file))
        self.assertIsNotNone(claude_entry)
        self.assertTrue(claude_entry.get("existed_prior"))
        self.assertEqual(claude_entry.get("ownership"), "EXISTED_PRIOR_USER")
        self.assertEqual(claude_entry.get("sha256_before"), claude_sha_orig)

        # Verify Skill ownership
        skill_entry = entries.get(str(skill_file))
        self.assertIsNotNone(skill_entry)
        self.assertTrue(skill_entry.get("existed_prior"))
        self.assertEqual(skill_entry.get("ownership"), "EXISTED_PRIOR_USER")
        initial_skill_backup = skill_entry.get("backup_file")
        self.assertTrue(Path(initial_skill_backup).is_file())
        self.assertEqual(Path(initial_skill_backup).read_bytes(), orig_skill_bytes)

        # =====================================================================
        # TRANSITION 2: Idempotent Re-install (Backup & Ownership Immutability)
        # =====================================================================
        cmd_install(is_all=True, dry_run=False)

        manifest_reinstalled = load_manifest(manifest_file)
        entries_reinstalled = manifest_reinstalled.get("entries", {})

        # Ownership and initial backup MUST be preserved, not overwritten
        re_skill_entry = entries_reinstalled.get(str(skill_file))
        self.assertEqual(re_skill_entry.get("backup_file"), initial_skill_backup)
        self.assertEqual(Path(initial_skill_backup).read_bytes(), orig_skill_bytes)
        self.assertTrue(re_skill_entry.get("existed_prior"))

        # =====================================================================
        # TRANSITION 3: Post-Install User Modifications
        # =====================================================================
        # 1. User modifies pre-existing skill (Content C)
        modified_skill_bytes = orig_skill_bytes + b"\n# User Modification C\n"
        skill_file.write_bytes(modified_skill_bytes)

        # 2. User modifies HuyNex rule module (Note D)
        comm_rule = self.home / ".agents/rules/01-communication.md"
        self.assertTrue(comm_rule.is_file())
        modified_comm_bytes = comm_rule.read_bytes() + b"\n# User Custom Note D\n"
        comm_rule.write_bytes(modified_comm_bytes)

        # =====================================================================
        # TRANSITION 4: Legacy Multi-Version Migration (v0.3.1 -> v0.3.5)
        # =====================================================================
        # Simulate an entry from v0.3.1 legacy manifest with missing ownership
        legacy_skill_file = self.home / ".agents/skills/legacy-preexisting/SKILL.md"
        legacy_skill_file.parent.mkdir(parents=True, exist_ok=True)
        legacy_user_bytes = b"---\nname: legacy-preexisting\n---\n# Legacy Preexisting Skill\n"
        legacy_skill_file.write_bytes(legacy_user_bytes)

        legacy_manifest_data = [
            {
                "path": str(legacy_skill_file),
                "type": "SKILL",
                "sha256": hashlib.sha256(legacy_user_bytes).hexdigest(),
                "installed_at": "2026-11-20T10:00:00Z"
            }
        ]
        manifest_file.write_text(json.dumps(legacy_manifest_data), encoding="utf-8")

        # Load must classify existed_prior as UNKNOWN
        migrated = load_manifest(manifest_file)
        legacy_entry = migrated["entries"].get(str(legacy_skill_file))
        self.assertEqual(legacy_entry["existed_prior"], "UNKNOWN")
        self.assertEqual(legacy_entry["ownership"], "UNKNOWN_LEGACY_V031")

        # Save merged manifest
        migrated["entries"].update(entries_reinstalled)
        save_manifest(manifest_file, migrated)

        # =====================================================================
        # TRANSITION 5: Non-Destructive Transactional Uninstall
        # =====================================================================
        uninstall_ok = cmd_uninstall()
        self.assertTrue(uninstall_ok, "Uninstall should succeed cleanly")

        # 1. CLAUDE.md byte-for-byte fidelity
        self.assertEqual(claude_file.read_bytes(), orig_claude_bytes, "CLAUDE.md must restore byte-for-byte")

        # 2. Skill restored to original Content A
        self.assertEqual(skill_file.read_bytes(), orig_skill_bytes, "Skill must restore to original Content A")

        # 3. User modifications (Content C and Note D) MUST exist in preserved archive
        preserved_dir = self.home / ".huynex/preserved_user_modified"
        self.assertTrue(preserved_dir.is_dir())
        preserved_texts = [p.read_text(encoding="utf-8", errors="ignore") for p in preserved_dir.glob("*")]
        self.assertTrue(any("User Modification C" in t for t in preserved_texts), "Content C must be archived")
        self.assertTrue(any("User Custom Note D" in t for t in preserved_texts), "Note D must be archived")

        # 4. P0-01 TEST: Legacy skill with UNKNOWN ownership must NEVER BE DELETED
        self.assertTrue(legacy_skill_file.is_file(), "Legacy file with UNKNOWN ownership must NEVER be deleted")
        self.assertEqual(legacy_skill_file.read_bytes(), legacy_user_bytes)

        # 5. Cursor custom rule was never touched
        self.assertEqual(cursor_file.read_bytes(), cursor_custom_bytes)

        # 6. Manifest cleanly removed on successful transactional uninstall
        self.assertFalse(manifest_file.is_file(), "Manifest should be removed after clean transactional uninstall")

        # =====================================================================
        # TRANSITION 6: Partial Failure & Manifest Transaction Preservation
        # =====================================================================
        # Simulate uninstall where a file has missing backup
        corrupted_manifest = {
            "version": "0.3.5",
            "entries": {
                str(skill_file): {
                    "type": "SKILL",
                    "managed_mode": "managed_file",
                    "existed_prior": True,
                    "backup_file": str(self.home / "non_existent_backup.bak"),
                    "sha256_installed": "fake_hash"
                }
            }
        }
        save_manifest(manifest_file, corrupted_manifest)

        failed_uninstall = cmd_uninstall()
        self.assertFalse(failed_uninstall, "Uninstall must fail when backup is missing for existed_prior file")
        # Manifest MUST be preserved with UNINSTALL_INCOMPLETE status
        self.assertTrue(manifest_file.is_file(), "Manifest must NOT be deleted when uninstall encounters errors")
        retained_manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(retained_manifest.get("status"), "UNINSTALL_INCOMPLETE")

    def test_user_modifications_across_multiple_upgrades(self):
        """INV-03: Multi-upgrade lifecycle regression test:
        Pre-existing A -> install v1 -> edit C -> upgrade v2 -> uninstall -> restore A and preserve C."""
        skill_dir = self.home / ".agents/skills/data-conservation-gate"
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"

        orig_a = b"---\nname: data-conservation-gate\n---\n# User Original Skill A\n"
        skill_file.write_bytes(orig_a)

        # 1. First install (v1)
        self.assertTrue(cmd_install(is_all=True, dry_run=False))
        manifest_file = self.home / ".huynex/installed_manifest.json"
        m1 = load_manifest(manifest_file)
        e1 = m1["entries"][str(skill_file)]
        self.assertTrue(e1["existed_prior"])
        self.assertEqual(e1["ownership"], "EXISTED_PRIOR_USER")
        initial_bk = e1["backup_file"]
        self.assertEqual(Path(initial_bk).read_bytes(), orig_a)

        # 2. User modifies file to Content C
        edit_c = b"---\nname: data-conservation-gate\n---\n# User Modified Customization C\n"
        skill_file.write_bytes(edit_c)

        # 3. Upgrade to v2 (re-install)
        self.assertTrue(cmd_install(is_all=True, dry_run=False))
        m2 = load_manifest(manifest_file)
        e2 = m2["entries"][str(skill_file)]
        # Ownership and initial backup MUST be preserved
        self.assertTrue(e2["existed_prior"])
        self.assertEqual(e2["ownership"], "EXISTED_PRIOR_USER")
        self.assertEqual(e2["backup_file"], initial_bk)

        # Content C must be preserved in archive
        preserved_dir = self.home / ".huynex/preserved_user_modified"
        self.assertTrue(preserved_dir.is_dir())
        archived_files = list(preserved_dir.glob("*"))
        archived_contents = [p.read_bytes() for p in archived_files]
        self.assertTrue(any(edit_c in c for c in archived_contents), "Content C must be safely archived during upgrade")

        # 4. Uninstall
        self.assertTrue(cmd_uninstall())
        # Original Content A must be restored 100% byte-for-byte!
        self.assertEqual(skill_file.read_bytes(), orig_a, "Original file A must be restored byte-for-byte after uninstall")
        # Content C still exists in preserved archive!
        self.assertTrue(any(edit_c in p.read_bytes() for p in preserved_dir.glob("*")), "Content C must remain archived")


if __name__ == "__main__":
    unittest.main()
