# HuyNex Agent Kit — Data Safety Contract & System Invariants

This contract defines the immutable safety invariants that govern the lifecycle engine of **HuyNex Agent Kit** (`scripts/install.py`). These invariants serve as the formal specification and quality gate for all releases.

---

## 🛡️ Core Safety Invariants

### INV-01: Ownership Immutability
- **Rule**: Any file existing before kit installation is classified as `EXISTED_PRIOR_USER`. This ownership classification is immutable and MUST NOT transition to `HUYNEX_CREATED` during upgrades, re-installations, or crash recovery.
- **Fail-Safe**: If ownership metadata is missing or ambiguous (such as in legacy migrations), it MUST default to `UNKNOWN`. Files with `UNKNOWN` ownership are NEVER unlinked or deleted by the uninstaller.
- **Verification**: `test_complete_state_machine_lifecycle`, `test_v031_legacy_manifest_migration`.

### INV-02: No Silent Overwrite & Pre-Mutation Verification
- **Rule**: No file on disk may be overwritten unless:
  1. A verified, immutable backup has been captured and fsynced.
  2. The file on disk immediately prior to write matches the expected content hash observed during planning.
- **Fail-Safe**: If a file was absent during planning but appears before write (`absent -> present`), or if its content changes (`present -> modified`), the installer MUST abort or update the snapshot without data loss.
- **Verification**: `test_p0_unexpected_file_appearance_aborts_or_backs_up`.

### INV-03: Cryptographic Recovery Integrity
- **Rule**: Restoring a file from backup (`.bak`) strictly requires a valid, non-empty `sha256_before` digest in the manifest.
- **Fail-Safe**: If `sha256_before` is missing, or if the actual SHA-256 of the backup file differs from `sha256_before` by even a single bit, restoration is REFUSED. The target file is left untouched, and the manifest is retained with `status: "UNINSTALL_INCOMPLETE"`.
- **Verification**: `test_p1_backup_sha256_tampering_refuses_restore`, `test_p1_missing_sha256_before_refuses_unverified_restore`.

### INV-04: Crash Consistency & Write-Ahead Checkpointing
- **Rule**: Manifest state is checkpointed atomically BEFORE and AFTER every file mutation:
  - **Pre-Mutation**: Manifest records `status: "IN_PROGRESS"` and `sha256_expected_after`.
  - **Mutation**: Target file written atomically via temporary file and replace.
  - **Post-Mutation**: Manifest records `status: "INSTALLED"` and `sha256_installed`.
- **Fail-Safe**: If execution terminates at any point, uninstaller can determine whether the file was written, partially written, or post-modified by comparing disk content with both `sha256_expected_after` and `sha256_before`.
- **Verification**: `test_p0_crash_gap_after_write_preserves_user_modifications`, `test_p1_crash_mid_install_wal_recovery`.

### INV-05: OS-Level Kernel Lock Exclusivity
- **Rule**: At most one process may hold mutation rights across the `.huynex` lifecycle at any given instant.
- **Mechanism**: Locking MUST be anchored to operating system kernel primitives (`fcntl.flock` on POSIX, `msvcrt.locking` on Windows) bound to an open file descriptor.
- **Fail-Safe**: If a process crashes or is killed via `SIGKILL`, the kernel automatically releases the lock descriptor. Stale lock recovery does not rely on fragile JSON parsing or race-prone PID heuristics.
- **Verification**: `test_p0_real_subprocess_lock_contention`, `test_p0_subprocess_killed_lock_auto_released`.

### INV-06: Filesystem Boundary & Symlink Defense
- **Rule**: The kit must never read from or write to arbitrary external paths via symbolic links.
- **Inspection**: The path and every ancestor directory up to the user home root (`~`) are checked with `is_symlink()`. Furthermore, `path.resolve()` must reside strictly within `home.resolve()`.
- **Fail-Safe**: Any destination file or ancestor directory that is a symlink, or resolves outside the managed root, is completely bypassed during install, update, and uninstall.
- **Verification**: `test_p0_parent_directory_symlink_boundary_protection`, `test_p1_symlink_safety_never_overwrites_user_symlink`.

### INV-07: Honest Exit Status
- **Rule**: Any operation that cannot complete with 100% data preservation and integrity MUST return a non-zero exit code (`exit 1` or `exit 2`).
- **Fail-Safe**: No command wrapper (`install.sh`, `install.ps1`) or CLI command may output a success banner or exit 0 if any sub-task, validator, doctor check, or manifest entry failed.
- **Verification**: `test_p1_corrupt_manifest_blocks_install_uninstall_and_doctor`, wrapper script exit code assertions.

### INV-08: Idempotency
- **Rule**: Repeated invocations of `install.py --all`, `install.py --check`, `install.py --doctor`, or `install.py --uninstall` on the same environment must produce deterministic, identical end states without corrupting manifests or leaking backup files.
- **Verification**: `test_complete_state_machine_lifecycle`, `test_dry_run_check_is_idempotent_and_non_mutating`.

### INV-09: User Mutation Preservation
- **Rule**: If a user modifies any file previously installed by HuyNex (or modifies a pre-existing file post-installation), the uninstaller MUST NEVER overwrite or delete that file without first archiving a full copy to `.huynex/preserved_user_modified/`.
- **Verification**: `test_complete_state_machine_lifecycle`, `test_p0_crash_gap_after_write_preserves_user_modifications`.

---

## 📋 Invariant-to-Test Traceability Matrix

| Invariant | Primary Test Case | Test File |
|---|---|---|
| **INV-01** | `test_complete_state_machine_lifecycle` | `tests/test_state_machine_lifecycle.py` |
| **INV-02** | `test_p0_unexpected_file_appearance_aborts_or_backs_up` | `tests/test_fault_injection.py` |
| **INV-03** | `test_p1_backup_sha256_tampering_refuses_restore` | `tests/test_fault_injection.py` |
| **INV-04** | `test_p0_crash_gap_after_write_preserves_user_modifications` | `tests/test_fault_injection.py` |
| **INV-05** | `test_p0_real_subprocess_lock_contention` | `tests/test_concurrency_subprocess.py` |
| **INV-06** | `test_p0_parent_directory_symlink_boundary_protection` | `tests/test_fault_injection.py` |
| **INV-07** | `test_p0_corrupt_manifest_blocks_install_uninstall_and_doctor` | `tests/test_fault_injection.py` |
| **INV-08** | `test_dry_run_check_is_idempotent_and_non_mutating` | `tests/test_installer.py` |
| **INV-09** | `test_user_modifications_across_multiple_upgrades` | `tests/test_state_machine_lifecycle.py` |
