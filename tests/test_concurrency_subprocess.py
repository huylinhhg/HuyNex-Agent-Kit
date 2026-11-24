#!/usr/bin/env python3
# ==============================================================================
# HuyNex Agent Kit — Subprocess Concurrency & Crash Recovery Tests
# ==============================================================================
"""Tests verifying OS-level kernel file locking under real subprocess concurrency,
process crashes (SIGKILL / TerminateProcess), and unexpected pre-mutation state changes."""

import os
import sys
import json
import time
import shutil
import hashlib
import tempfile
import unittest
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
INSTALL_PY = SCRIPTS_DIR / "install.py"

sys.path.insert(0, str(REPO_ROOT))
from scripts.install import (
    LifecycleLock,
    LifecycleLockError,
    load_manifest,
    sha256_file,
    cmd_install,
    cmd_uninstall,
)


class TestConcurrencySubprocess(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.home = Path(self.temp_dir.name)

        # Build clean environment with mock client
        (self.home / ".claude").mkdir(parents=True, exist_ok=True)
        (self.home / ".claude/CLAUDE.md").write_text("# User Original Instructions\n", encoding="utf-8")

        self.orig_env = os.environ.copy()
        os.environ["HOME"] = str(self.home)
        os.environ["USERPROFILE"] = str(self.home)

        self.env = os.environ.copy()
        self.env["HOME"] = str(self.home)
        self.env["USERPROFILE"] = str(self.home)
        self.env["PYTHONPATH"] = str(REPO_ROOT)
        self.env["PYTHONIOENCODING"] = "utf-8"

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.orig_env)
        # Ensure read-only .bak files can be cleaned up on Windows & POSIX
        for root, _, files in os.walk(str(self.home)):
            for name in files:
                p = Path(root) / name
                try:
                    p.chmod(0o666)
                except Exception:
                    pass
        self.temp_dir.cleanup()

    def test_concurrent_subprocess_install_exactly_one_wins(self):
        """Two independent OS processes trying to install concurrently:
        exactly one acquires the kernel lock, the other safely fails with code 1."""
        cmd = [sys.executable, str(INSTALL_PY), "--all"]

        # Launch two processes as close in time as possible
        p1 = subprocess.Popen(cmd, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        p2 = subprocess.Popen(cmd, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        out1, err1 = p1.communicate(timeout=30)
        out2, err2 = p2.communicate(timeout=30)

        codes = sorted([p1.returncode, p2.returncode])
        self.assertEqual(codes, [0, 1], f"Expected one 0 and one 1 exit code. Got {codes}. out1: {out1}, out2: {out2}")

        combined_out = out1 + out2
        self.assertIn("CONCURRENT LIFECYCLE", combined_out, "Blocked process must report concurrent lock error")

        # Verify manifest is valid and healthy
        manifest_file = self.home / ".huynex/installed_manifest.json"
        self.assertTrue(manifest_file.is_file(), "Manifest must exist and be valid")
        manifest = load_manifest(manifest_file)
        self.assertEqual(manifest.get("status"), "INSTALLED")

    def test_concurrent_subprocess_uninstall_locked(self):
        """Two independent processes running uninstall concurrently:
        exactly one acquires the lock."""
        # First install cleanly
        install_res = subprocess.run(
            [sys.executable, str(INSTALL_PY), "--all"],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(install_res.returncode, 0)

        cmd = [sys.executable, str(INSTALL_PY), "--uninstall"]
        p1 = subprocess.Popen(cmd, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        p2 = subprocess.Popen(cmd, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        out1, err1 = p1.communicate(timeout=30)
        out2, err2 = p2.communicate(timeout=30)

        codes = sorted([p1.returncode, p2.returncode])
        self.assertEqual(codes, [0, 1], f"Expected [0, 1]. Got {codes}. out1: {out1}, out2: {out2}")

    def test_subprocess_sigkill_lock_immediately_reclaimed_by_os(self):
        """When a child process holding LifecycleLock is terminated via SIGKILL,
        the OS kernel immediately frees the lock descriptor so another process can acquire it."""
        child_code = f"""
import sys, time, pathlib
sys.path.insert(0, r"{REPO_ROOT}")
from scripts.install import LifecycleLock
home = pathlib.Path(r"{self.home}")
with LifecycleLock(home):
    sys.stdout.write("LOCK_ACQUIRED\\n")
    sys.stdout.flush()
    time.sleep(30) # Wait until killed
"""
        proc = subprocess.Popen(
            [sys.executable, "-c", child_code],
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait until child has acquired the lock
        line = proc.stdout.readline().strip()
        self.assertEqual(line, "LOCK_ACQUIRED")

        # Abruptly kill the child process (SIGKILL / TerminateProcess)
        proc.kill()
        proc.stdout.close()
        proc.stderr.close()
        proc.wait(timeout=5)

        # The parent process (or a new installer process) MUST immediately acquire the lock!
        with LifecycleLock(self.home) as lock:
            self.assertTrue(lock._acquired, "Must immediately acquire lock after dead process")

        # Running install immediately afterwards must succeed
        res = subprocess.run(
            [sys.executable, str(INSTALL_PY), "--all"],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(res.returncode, 0, f"Install failed after SIGKILL: {res.stdout}\n{res.stderr}")

    def test_pre_mutation_toctou_absent_to_present_surprise(self):
        """TEST-01: True TOCTOU synchronization test:
        1. Target file does NOT exist during planning.
        2. A controlled hook injects user file between planning and mutation.
        3. Installer detects unexpected disk presence, captures immutable backup,
           and marks ownership as EXISTED_PRIOR_USER.
        4. Uninstall restores user's surprise file 100% byte-for-byte."""
        surprise_file = self.home / ".claude/skills/data-conservation-gate/SKILL.md"
        surprise_content = b"---\nname: surprise\n---\n# User Surprise File Created Between Plan And Write\n"

        # 1. Target file MUST NOT exist during planning
        self.assertFalse(surprise_file.exists(), "Target file must not exist before planning")

        # 2. Synchronization hook fires between planning and mutation loop
        hook_fired = False

        def inject_user_file_after_planning():
            nonlocal hook_fired
            surprise_file.parent.mkdir(parents=True, exist_ok=True)
            surprise_file.write_bytes(surprise_content)
            hook_fired = True

        # 3. Execute install with synchronization hook
        success = cmd_install(is_all=True, dry_run=False, pre_mutation_hook=inject_user_file_after_planning)
        self.assertTrue(success, "Install must succeed and handle pre-mutation surprise file")
        self.assertTrue(hook_fired, "Hook must execute between plan and write")

        # 4. Verify manifest records EXISTED_PRIOR_USER and captures immutable backup
        manifest_file = self.home / ".huynex/installed_manifest.json"
        self.assertTrue(manifest_file.is_file())
        manifest = load_manifest(manifest_file)
        entry = manifest["entries"].get(str(surprise_file))
        self.assertIsNotNone(entry, "Surprise file must be recorded in manifest")
        self.assertTrue(entry.get("existed_prior"), "Must be marked existed_prior=True")
        self.assertEqual(entry.get("ownership"), "EXISTED_PRIOR_USER")
        self.assertIsNotNone(entry.get("backup_file"), "Must have captured backup file")
        self.assertEqual(entry.get("sha256_before"), hashlib.sha256(surprise_content).hexdigest())

        # Backup file on disk must match surprise content byte-for-byte
        bk_path = Path(entry["backup_file"])
        self.assertTrue(bk_path.is_file())
        self.assertEqual(bk_path.read_bytes(), surprise_content)

        # 5. Uninstall must restore surprise file byte-for-byte
        self.assertTrue(cmd_uninstall())
        self.assertEqual(surprise_file.read_bytes(), surprise_content, "User file must be restored byte-for-byte")

    def test_kernel_lock_inode_stability_and_no_unlink(self):
        """TEST-02: Lockfile inode remains permanent on disk across acquisitions;
        lockfile is never unlinked, avoiding inode recycling race."""
        lock_file = self.home / ".huynex/.lifecycle.lock"

        # 1. First acquisition
        with LifecycleLock(self.home) as lock1:
            self.assertTrue(lock1._acquired)
            stat1 = lock_file.stat()
            ino1 = stat1.st_ino

        # 2. After release, lockfile MUST persist on disk
        self.assertTrue(lock_file.exists(), "Lockfile must NOT be unlinked upon release")
        stat_after = lock_file.stat()
        self.assertEqual(stat_after.st_ino, ino1, "Lockfile inode must remain identical after release")

        # Payload indicates released status, not active lock
        payload = json.loads(lock_file.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("status"), "released")

        # 3. Second acquisition on same path must use the exact same inode
        with LifecycleLock(self.home) as lock2:
            self.assertTrue(lock2._acquired)
            stat2 = lock_file.stat()
            self.assertEqual(stat2.st_ino, ino1, "Lockfile inode must remain identical across sessions")

        self.assertTrue(lock_file.exists())

    def test_kernel_lock_sequential_handoff_and_contention(self):
        """TEST-02: Real independent subprocesses demonstrate mutual exclusion,
        clean handoff after release, and rejection during hold."""
        lock_file = self.home / ".huynex/.lifecycle.lock"

        child_code = f"""
import sys, time, pathlib
sys.path.insert(0, r"{REPO_ROOT}")
from scripts.install import LifecycleLock
home = pathlib.Path(r"{self.home}")
with LifecycleLock(home):
    sys.stdout.write("READY\\n")
    sys.stdout.flush()
    sys.stdin.readline()
sys.stdout.write("RELEASED\\n")
sys.stdout.flush()
"""
        proc = subprocess.Popen(
            [sys.executable, "-c", child_code],
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        ready_line = proc.stdout.readline().strip()
        self.assertEqual(ready_line, "READY", "Child process must acquire lock")

        # Attempt to acquire lock in parent: MUST FAIL immediately
        with self.assertRaises(LifecycleLockError):
            with LifecycleLock(self.home):
                pass

        # Attempt to run install in another subprocess: MUST FAIL with exit code 1
        res = subprocess.run(
            [sys.executable, str(INSTALL_PY), "--all"],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(res.returncode, 1, "Concurrent install process must be blocked with exit code 1")

        # Tell child to release lock
        proc.stdin.write("GO\n")
        proc.stdin.flush()
        released_line = proc.stdout.readline().strip()
        self.assertEqual(released_line, "RELEASED")
        proc.wait(timeout=5)

        # Now parent must acquire lock immediately and smoothly
        with LifecycleLock(self.home) as parent_lock:
            self.assertTrue(parent_lock._acquired, "Parent must acquire lock after child release")

        # Lockfile exists but is not misidentified as active
        self.assertTrue(lock_file.exists())
        self.assertTrue(cmd_install(is_all=True, dry_run=False))

    def test_kernel_lock_rejects_concurrent_locks_on_replaced_inode(self):
        """TEST-02: Prove that two processes CANNOT create or hold two valid locks
        on two different inodes simultaneously (Không thể tạo hai lock hợp lệ trên hai inode khác nhau).
        When inode A is replaced by inode B while a process has opened a descriptor,
        post-flock verification detects the detached inode, retries on inode B,
        and is blocked by contention because another process holds inode B."""
        lock_file = self.home / ".huynex/.lifecycle.lock"
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text("initial_inode_a")

        # Child process will acquire lock on current inode B and hold it
        child_code = f"""
import sys, time, pathlib
sys.path.insert(0, r"{REPO_ROOT}")
from scripts.install import LifecycleLock
home = pathlib.Path(r"{self.home}")
with LifecycleLock(home):
    sys.stdout.write("READY\\n")
    sys.stdout.flush()
    sys.stdin.readline()
sys.stdout.write("RELEASED\\n")
sys.stdout.flush()
"""
        # Open descriptor fd1 on inode A before replacement
        fd1 = os.open(str(lock_file), os.O_RDWR)
        ino1 = os.fstat(fd1).st_ino

        # Rename lock_file to .bak and create new file with inode B
        bak_file = self.home / ".huynex/.lifecycle.lock.bak"
        os.rename(str(lock_file), str(bak_file))
        lock_file.write_text("new_inode_b")
        ino2 = lock_file.stat().st_ino
        self.assertNotEqual(ino1, ino2, "Inodes must be different")

        # Child process acquires lock on inode B
        proc = subprocess.Popen(
            [sys.executable, "-c", child_code],
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        ready_line = proc.stdout.readline().strip()
        self.assertEqual(ready_line, "READY", "Child must acquire lock on inode B")

        # 1. Parent process attempts to acquire lock via LifecycleLock:
        # It must NOT acquire a lock on inode A; it must target inode B and fail with LifecycleLockError!
        with self.assertRaises(LifecycleLockError):
            with LifecycleLock(self.home):
                pass

        # 2. Also verify that install CLI fails with returncode 1 (blocked by child)
        res = subprocess.run(
            [sys.executable, str(INSTALL_PY), "--all"],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(res.returncode, 1, "Concurrent install CLI must be blocked")

        # 3. Release child
        proc.stdin.write("GO\n")
        proc.stdin.flush()
        self.assertEqual(proc.stdout.readline().strip(), "RELEASED")
        proc.wait(timeout=5)

        # Cleanup
        os.close(fd1)
        bak_file.unlink(missing_ok=True)

    def test_lockfile_direct_symlink_corruption_prevented(self):
        """TEST-03: Direct symlink at .lifecycle.lock pointing to external file:
        Installer rejects operation, external file is untouched byte-for-byte,
        no invalid manifest/backup written, exit code != 0."""
        victim_dir = Path(tempfile.mkdtemp(prefix="huynex_victim_"))
        try:
            victim_file = victim_dir / "victim_data.db"
            victim_content = b"CRITICAL_USER_DATABASE_DO_NOT_CORRUPT_OR_TRUNCATE_9876543210"
            victim_file.write_bytes(victim_content)

            lock_dir = self.home / ".huynex"
            lock_dir.mkdir(parents=True, exist_ok=True)
            lock_symlink = lock_dir / ".lifecycle.lock"

            try:
                os.symlink(str(victim_file), str(lock_symlink))
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks not supported on this platform/configuration")

            # 1. Attempt LifecycleLock directly
            with self.assertRaises(LifecycleLockError):
                with LifecycleLock(self.home):
                    pass

            # 2. Attempt install.py via subprocess CLI
            res = subprocess.run(
                [sys.executable, str(INSTALL_PY), "--all"],
                env=self.env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            # Exit code must be non-zero
            self.assertNotEqual(res.returncode, 0, f"Installer must fail when lock is a symlink: {res.stdout}")
            self.assertIn("Security violation", res.stdout + res.stderr)

            # 3. External victim file MUST NOT be modified by a single byte!
            self.assertEqual(victim_file.read_bytes(), victim_content, "External file must be completely untouched")
            self.assertEqual(victim_file.stat().st_size, len(victim_content), "External file size must not change")

            # 4. No manifest or backup file written
            manifest_file = self.home / ".huynex/installed_manifest.json"
            self.assertFalse(manifest_file.exists(), "No manifest must be written when lock fails")
            backup_dir = self.home / ".huynex/backups"
            self.assertFalse(backup_dir.exists(), "No backup directory must be created")
        finally:
            shutil.rmtree(str(victim_dir), ignore_errors=True)

    def test_lockfile_ancestor_symlink_corruption_prevented(self):
        """TEST-03: Ancestor symlink (.huynex pointing to external directory):
        Installer rejects operation, external directory untouched, exit code != 0."""
        external_dir = Path(tempfile.mkdtemp(prefix="huynex_ext_ancestor_"))
        try:
            canary_file = external_dir / "external_canary.txt"
            canary_content = b"CANARY_SECRET_DATA_DO_NOT_TOUCH"
            canary_file.write_bytes(canary_content)

            huynex_dir = self.home / ".huynex"
            try:
                os.symlink(str(external_dir), str(huynex_dir))
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks not supported on this platform/configuration")

            # Attempt LifecycleLock
            with self.assertRaises(LifecycleLockError):
                with LifecycleLock(self.home):
                    pass

            # Attempt install via subprocess
            res = subprocess.run(
                [sys.executable, str(INSTALL_PY), "--all"],
                env=self.env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertNotEqual(res.returncode, 0, "Installer must reject ancestor symlink")
            self.assertIn("Security violation", res.stdout + res.stderr)

            # Canary file must remain untouched
            self.assertEqual(canary_file.read_bytes(), canary_content)
            # No files installed inside external directory
            self.assertFalse((external_dir / "installed_manifest.json").exists())
            self.assertFalse((external_dir / ".lifecycle.lock").exists())
        finally:
            shutil.rmtree(str(external_dir), ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
