#!/usr/bin/env python3
"""
Fault-Injection, Crash Consistency, Integrity & Concurrency Test Suite
----------------------------------------------------------------------
Directly tests the Stable Release Quality Gates:
1. P0: Corrupt or schema-invalid manifest blocks install/uninstall/doctor without deleting manifest.
2. P0: Parent directory symlink boundary protection prevents escapes and outside mutations.
3. P0: Crash gap after file write preserves user modifications via double-hash expected_after checks.
4. P1: Tampered/corrupted .bak file triggers SHA-256 integrity failure and refuses restore.
5. P1: Missing sha256_before refuses unverified restore and marks transaction incomplete.
6. P1: Mid-install crash (fault injection) preserves Write-Ahead manifest checkpoints for clean recovery.
7. P1: Concurrent lifecycle lock blocks parallel install/uninstall races cleanly.
8. P1: Dead process stale lock recovery automatically reclaims orphaned locks.
9. P1: Symlink safety ensures direct and parent user symlinks are never overwritten or unlinked.
10. P1: Strict manifest schema validation validates all metadata types, modes, and ownership values.
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
    is_path_or_parent_symlink,
    is_pid_alive,
    load_manifest,
    validate_manifest_schema,
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

        claude_before = claude_file.read_bytes()
        skill_before = skill_file.read_bytes()

        corrupt_payload = b'{"version": "0.3.7", "entries": {BROKEN_JSON'
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

    def test_p0_strict_manifest_entry_schema_validation(self):
        """P0: Schema validation rejects unknown types, invalid modes, and bad ownership without guessing."""
        manifest_file = self.home / "schema_manifest.json"

        # Invalid type
        bad_type = {"version": "0.3.7", "entries": {"/test": {"type": "MALICIOUS", "managed_mode": "managed_file", "existed_prior": False, "ownership": "HUYNEX_CREATED"}}}
        manifest_file.write_text(json.dumps(bad_type), encoding="utf-8")
        with self.assertRaises(ManifestCorruptError):
            load_manifest(manifest_file)

        # Invalid mode
        bad_mode = {"version": "0.3.7", "entries": {"/test": {"type": "SKILL", "managed_mode": "overwrite_all", "existed_prior": False, "ownership": "HUYNEX_CREATED"}}}
        manifest_file.write_text(json.dumps(bad_mode), encoding="utf-8")
        with self.assertRaises(ManifestCorruptError):
            load_manifest(manifest_file)

        # Invalid ownership
        bad_owner = {"version": "0.3.7", "entries": {"/test": {"type": "SKILL", "managed_mode": "managed_file", "existed_prior": False, "ownership": "ROOT_ADMIN"}}}
        manifest_file.write_text(json.dumps(bad_owner), encoding="utf-8")
        with self.assertRaises(ManifestCorruptError):
            load_manifest(manifest_file)

        # Invalid existed_prior
        bad_prior = {"version": "0.3.7", "entries": {"/test": {"type": "SKILL", "managed_mode": "managed_file", "existed_prior": "MAYBE", "ownership": "UNKNOWN"}}}
        manifest_file.write_text(json.dumps(bad_prior), encoding="utf-8")
        with self.assertRaises(ManifestCorruptError):
            load_manifest(manifest_file)

    def test_p0_parent_directory_symlink_boundary_protection(self):
        """P0: Ancestor directory symlinks pointing outside home must be detected and protected."""
        outside_dir = Path(tempfile.mkdtemp(prefix="huynex_outside_"))
        outside_skill_file = outside_dir / "SKILL.md"
        outside_content = b"---\nname: data-conservation-gate\n---\n# Outside Work Never Mutate\n"
        outside_skill_file.write_bytes(outside_content)

        skills_parent = self.home / ".agents/skills"
        skills_parent.mkdir(parents=True, exist_ok=True)
        symlinked_skill_dir = skills_parent / "data-conservation-gate"

        try:
            os.symlink(outside_dir, symlinked_skill_dir)
        except (OSError, NotImplementedError):
            shutil.rmtree(outside_dir, ignore_errors=True)
            self.skipTest("Symlinks not supported on this host environment")

        try:
            # 1. is_path_or_parent_symlink must return True for any file inside symlinked_skill_dir
            target_dst = symlinked_skill_dir / "SKILL.md"
            self.assertTrue(is_path_or_parent_symlink(target_dst, boundary=self.home))

            # 2. cmd_install must NOT mutate outside_skill_file
            self.assertTrue(cmd_install(is_all=True, dry_run=False))
            self.assertEqual(outside_skill_file.read_bytes(), outside_content)

            # 3. cmd_uninstall must NOT delete or unlink outside_skill_file
            self.assertTrue(cmd_uninstall())
            self.assertEqual(outside_skill_file.read_bytes(), outside_content)
        finally:
            shutil.rmtree(outside_dir, ignore_errors=True)

    def test_p0_crash_gap_after_write_preserves_user_modifications(self):
        """P0: Crash gap after file write preserves user modifications via double-hash expected_after checks."""
        claude_file, claude_orig, skill_file, skill_orig = self._seed_user_environment()
        self.assertTrue(cmd_install(is_all=True, dry_run=False))

        manifest_file = self.home / ".huynex/installed_manifest.json"
        manifest_data = load_manifest(manifest_file)

        # Simulate crash gap: file was written, sha256_expected_after was recorded,
        # but sha256_installed was NOT updated yet (remains None or old hash)
        skill_meta = manifest_data["entries"][str(skill_file)]
        expected_after = skill_meta.get("sha256_installed")
        self.assertIsNotNone(expected_after)
        skill_meta["sha256_expected_after"] = expected_after
        skill_meta["sha256_installed"] = None
        skill_meta["status"] = "IN_PROGRESS"
        manifest_data["status"] = "INSTALL_IN_PROGRESS"
        install.save_manifest(manifest_file, manifest_data)

        # Now simulate user editing this file during the crash recovery window
        user_edit = skill_file.read_bytes() + b"\n# User Edit Post-Crash\n"
        skill_file.write_bytes(user_edit)

        # cmd_uninstall MUST recognize that current file differs from expected_after AND before
        # and safely archive user edit before restoring original backup
        self.assertTrue(cmd_uninstall())

        # Original backup must be restored
        self.assertEqual(skill_file.read_bytes(), skill_orig)

        # User's post-crash edit must be preserved in archive
        preserved_dir = self.home / ".huynex/preserved_user_modified"
        self.assertTrue(preserved_dir.is_dir())
        preserved_texts = [p.read_text(encoding="utf-8", errors="ignore") for p in preserved_dir.glob("*")]
        self.assertTrue(any("User Edit Post-Crash" in t for t in preserved_texts))

    def test_p1_backup_sha256_tampering_refuses_restore(self):
        """P1: Tampered .bak file must fail SHA-256 verification and never overwrite target file."""
        claude_file, claude_orig, skill_file, _ = self._seed_user_environment()
        self.assertTrue(cmd_install(is_all=True, dry_run=False))

        manifest_file = self.home / ".huynex/installed_manifest.json"
        manifest = load_manifest(manifest_file)
        skill_meta = manifest["entries"][str(skill_file)]
        bk_path = Path(skill_meta["backup_file"])
        self.assertTrue(bk_path.is_file())

        skill_before_uninstall = skill_file.read_bytes()

        os.chmod(bk_path, 0o644)
        tampered_bytes = b"# CORRUPTED BACKUP CONTENT B\n"
        bk_path.write_bytes(tampered_bytes)

        self.assertFalse(cmd_uninstall())
        self.assertEqual(skill_file.read_bytes(), skill_before_uninstall)
        self.assertNotEqual(skill_file.read_bytes(), tampered_bytes)

        self.assertTrue(manifest_file.is_file())
        retained = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(retained.get("status"), "UNINSTALL_INCOMPLETE")
        self.assertIn(str(skill_file), retained.get("entries", {}))
        self.assertEqual(claude_file.read_bytes(), claude_orig)

    def test_p1_missing_sha256_before_refuses_unverified_restore(self):
        """P1: Pre-existing file missing sha256_before refuses unverified restore and retains manifest."""
        claude_file, _, skill_file, _ = self._seed_user_environment()
        self.assertTrue(cmd_install(is_all=True, dry_run=False))

        manifest_file = self.home / ".huynex/installed_manifest.json"
        manifest = load_manifest(manifest_file)
        skill_meta = manifest["entries"][str(skill_file)]
        # Strip sha256_before
        skill_meta["sha256_before"] = ""
        install.save_manifest(manifest_file, manifest)

        skill_before = skill_file.read_bytes()
        self.assertFalse(cmd_uninstall())

        # Target file must be retained safely, NOT overwritten blindly
        self.assertEqual(skill_file.read_bytes(), skill_before)
        retained = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(retained.get("status"), "UNINSTALL_INCOMPLETE")

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

        lock_file = self.home / ".huynex/.lifecycle.lock"
        self.assertTrue(lock_file.exists(), "Lifecycle lockfile must remain stable on disk")
        with LifecycleLock(self.home) as test_lock:
            self.assertTrue(test_lock._acquired, "Lifecycle lock must be released and re-acquirable after crash")

        manifest_file = self.home / ".huynex/installed_manifest.json"
        self.assertTrue(manifest_file.is_file(), "WAL manifest must exist after mid-install crash")
        wal_manifest = load_manifest(manifest_file)
        self.assertEqual(wal_manifest.get("status"), "INSTALL_IN_PROGRESS")
        self.assertGreaterEqual(len(wal_manifest.get("entries", {})), 5)

        self.assertFalse(cmd_doctor())
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

        self.assertTrue(cmd_install(is_all=True, dry_run=False))
        self.assertTrue(cmd_uninstall())

    def test_p1_dead_process_stale_lock_recovery(self):
        """P1: Dead PID orphaned lock file is automatically detected and reclaimed cleanly."""
        self._seed_user_environment()
        lock_file = self.home / ".huynex/.lifecycle.lock"
        lock_file.parent.mkdir(parents=True, exist_ok=True)

        # Write a lock pointing to a dead PID (PID 99999999 is guaranteed non-existent)
        dead_pid = 99999999
        self.assertFalse(is_pid_alive(dead_pid))
        lock_payload = {"pid": dead_pid, "acquired_at": "2026-11-20T00:00:00Z"}
        lock_file.write_text(json.dumps(lock_payload), encoding="utf-8")

        # LifecycleLock must acquire successfully even if lockfile was left on disk, and keep inode stable
        with LifecycleLock(self.home) as l:
            self.assertTrue(l._acquired)

        self.assertTrue(lock_file.exists(), "Lockfile must remain stable on disk and not be unlinked")
        with LifecycleLock(self.home) as l2:
            self.assertTrue(l2._acquired, "Subsequent process must immediately acquire lock on existing lockfile")

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
