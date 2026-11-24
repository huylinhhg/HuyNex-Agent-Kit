#!/usr/bin/env python3
"""
Fault-Injection, Crash Consistency, Integrity & Concurrency Test Suite
----------------------------------------------------------------------
Directly tests the Stable Release Quality Gates:
1. P0: Corrupt or schema-invalid manifest blocks install/uninstall/doctor without deleting manifest.
2. P1: Tampered/corrupted .bak file triggers SHA-256 integrity failure and refuses restore.
3. P1: Mid-install crash (fault injection) preserves Write-Ahead manifest checkpoints for clean recovery.
4. P1: Concurrent lifecycle lock blocks parallel install/uninstall races cleanly.
5. P1: Symlink safety ensures user symlinks are never silently overwritten or unlinked.
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import install
from install import (
    LifecycleLock,
    ManifestCorruptError,
    cmd_doctor,
    cmd_install,
    cmd_uninstall,
    load_manifest,
)


class TestFaultInjectionAndDataSafety(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="huynex_fault_inj_")
        self.home = Path(self.tmp_dir)
        self.orig_env = os.environ.copy()
        os.environ["HOME"] = str(self.home)
        os.environ["USERPROFILE"] = str(self.home)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.orig_env)
        # Ensure read-only .bak files can be cleaned up on Windows & POSIX
        for root, _, files in os.walk(self.tmp_dir):
            for name in files:
                p = Path(root) / name
                try:
                    os.chmod(p, 0o644)
                except OSError:
                    pass
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _seed_user_environment(self):
        claude_dir = self.home / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        claude_file = claude_dir / "CLAUDE.md"
        claude_orig = b"# User Prompt\r\nKeep it strict.\r\n"
        claude_file.write_bytes(claude_orig)

        skill_dir = self.home / ".agents/skills/data-conservation-gate"
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        skill_orig = b"---\nname: data-conservation-gate\n---\n# Original User Skill A\n"
        skill_file.write_bytes(skill_orig)

        return claude_file, claude_orig, skill_file, skill_orig

    def test_p0_corrupt_manifest_blocks_install_uninstall_and_doctor(self):
        """P0: Corrupt manifest must fail-closed across install, uninstall, and doctor without deleting manifest."""
        claude_file, _, skill_file, _ = self._seed_user_environment()
        self.assertTrue(cmd_install(is_all=True, dry_run=False))

        manifest_file = self.home / ".huynex/installed_manifest.json"
        self.assertTrue(manifest_file.is_file())

        # Snapshot files after install
        claude_before = claude_file.read_bytes()
        skill_before = skill_file.read_bytes()

        # Corrupt manifest with invalid JSON
        corrupt_payload = b'{"version": "0.3.6", "entries": {BROKEN_JSON'
        manifest_file.write_bytes(corrupt_payload)

        # 1. load_manifest must raise ManifestCorruptError
        with self.assertRaises(ManifestCorruptError):
            load_manifest(manifest_file)

        # 2. cmd_uninstall must fail-closed, NOT delete manifest, NOT mutate files
        self.assertFalse(cmd_uninstall())
        self.assertTrue(manifest_file.is_file())
        self.assertEqual(manifest_file.read_bytes(), corrupt_payload)
        self.assertEqual(claude_file.read_bytes(), claude_before)
        self.assertEqual(skill_file.read_bytes(), skill_before)

        # 3. cmd_install must fail-closed, NOT overwrite corrupt manifest
        self.assertFalse(cmd_install(is_all=True, dry_run=False))
        self.assertEqual(manifest_file.read_bytes(), corrupt_payload)

        # 4. cmd_doctor must fail
        self.assertFalse(cmd_doctor())

        # 5. Schema-invalid JSON structures must also raise ManifestCorruptError
        manifest_file.write_text(json.dumps({"version": "0.3.6", "wrong": []}), encoding="utf-8")
        with self.assertRaises(ManifestCorruptError):
            load_manifest(manifest_file)

        manifest_file.write_text(json.dumps(["not_a_dict"]), encoding="utf-8")
        with self.assertRaises(ManifestCorruptError):
            load_manifest(manifest_file)

    def test_p1_backup_sha256_tampering_refuses_restore(self):
        """P1: Tampered .bak file must fail SHA-256 verification and never overwrite target file."""
        claude_file, claude_orig, skill_file, _ = self._seed_user_environment()
        self.assertTrue(cmd_install(is_all=True, dry_run=False))

        manifest_file = self.home / ".huynex/installed_manifest.json"
        manifest = load_manifest(manifest_file)
        skill_meta = manifest["entries"][str(skill_file)]
        bk_path = Path(skill_meta["backup_file"])
        self.assertTrue(bk_path.is_file())

        # Record skill content currently on disk before uninstall
        skill_before_uninstall = skill_file.read_bytes()

        # Simulate storage corruption / external tamper on .bak
        os.chmod(bk_path, 0o644)
        tampered_bytes = b"# CORRUPTED BACKUP CONTENT B\n"
        bk_path.write_bytes(tampered_bytes)

        # Uninstall must refuse to restore tampered backup and return False
        self.assertFalse(cmd_uninstall())

        # Target skill MUST NOT be overwritten with tampered_bytes
        self.assertEqual(skill_file.read_bytes(), skill_before_uninstall)
        self.assertNotEqual(skill_file.read_bytes(), tampered_bytes)

        # Manifest must be retained with UNINSTALL_INCOMPLETE containing the failed skill entry
        self.assertTrue(manifest_file.is_file())
        retained = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(retained.get("status"), "UNINSTALL_INCOMPLETE")
        self.assertIn(str(skill_file), retained.get("entries", {}))

        # Meanwhile, intact CLAUDE.md backup must have restored byte-for-byte
        self.assertEqual(claude_file.read_bytes(), claude_orig)

    def test_p1_crash_mid_install_wal_recovery(self):
        """P1: Simulated crash mid-install leaves Write-Ahead manifest checkpoints allowing clean rollback via uninstall."""
        claude_file, claude_orig, skill_file, skill_orig = self._seed_user_environment()

        real_atomic_write = install.atomic_write
        non_manifest_writes = 0

        def crashing_atomic_write(target_path: Path, content: bytes, mode: int = None):
            nonlocal non_manifest_writes
            if target_path.name != "installed_manifest.json":
                non_manifest_writes += 1
                if non_manifest_writes == 6:
                    raise OSError("Simulated mid-install disk full / crash")
            return real_atomic_write(target_path, content, mode=mode)

        with mock.patch.object(install, "atomic_write", side_effect=crashing_atomic_write):
            with self.assertRaises(OSError):
                cmd_install(is_all=True, dry_run=False)

        # Lock file MUST have been released cleanly even after crash
        lock_file = self.home / ".huynex/.lifecycle.lock"
        self.assertFalse(lock_file.exists(), "Lifecycle lock must be released on crash")

        # Manifest MUST already exist on disk with WAL checkpoint status
        manifest_file = self.home / ".huynex/installed_manifest.json"
        self.assertTrue(manifest_file.is_file(), "WAL manifest must exist after mid-install crash")
        wal_manifest = load_manifest(manifest_file)
        self.assertEqual(wal_manifest.get("status"), "INSTALL_IN_PROGRESS")
        self.assertGreaterEqual(len(wal_manifest.get("entries", {})), 5)

        # Doctor must flag incomplete install transaction
        self.assertFalse(cmd_doctor())

        # Recovery via cmd_uninstall must cleanly restore all pre-existing files byte-for-byte
        self.assertTrue(cmd_uninstall())
        self.assertEqual(claude_file.read_bytes(), claude_orig)
        self.assertEqual(skill_file.read_bytes(), skill_orig)
        self.assertFalse(manifest_file.exists())

    def test_p1_concurrent_lifecycle_lock_blocks_second_process(self):
        """P1: Active LifecycleLock must block concurrent install/uninstall without mutating state."""
        self._seed_user_environment()

        with LifecycleLock(self.home):
            self.assertFalse(cmd_install(is_all=True, dry_run=False))
            self.assertFalse(cmd_uninstall())

        # Once lock is released, install and uninstall succeed normally
        self.assertTrue(cmd_install(is_all=True, dry_run=False))
        self.assertTrue(cmd_uninstall())

    def test_p1_symlink_safety_never_overwrites_user_symlink(self):
        """P1: User symlinks must never be silently overwritten or unlinked during install/uninstall."""
        external_target = self.home / "external_user_skill.md"
        external_bytes = b"---\nname: data-conservation-gate\n---\n# Symlinked User Skill\n"
        external_target.write_bytes(external_bytes)

        skill_dir = self.home / ".agents/skills/data-conservation-gate"
        skill_dir.mkdir(parents=True, exist_ok=True)
        symlink_skill = skill_dir / "SKILL.md"
        try:
            os.symlink(external_target, symlink_skill)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation requires elevated privileges on this Windows host")

        self.assertTrue(cmd_install(is_all=True, dry_run=False))
        self.assertTrue(symlink_skill.is_symlink(), "Symlink must remain a symlink after install")
        self.assertEqual(external_target.read_bytes(), external_bytes)

        self.assertTrue(cmd_uninstall())
        self.assertTrue(symlink_skill.is_symlink(), "Symlink must remain intact after uninstall")
        self.assertEqual(external_target.read_bytes(), external_bytes)


if __name__ == "__main__":
    unittest.main()
