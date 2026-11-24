# Changelog

Tất cả các thay đổi đáng chú ý của dự án **HuyNex Agent Kit** sẽ được ghi lại trong tệp này.
Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/) và tuân thủ [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2026-11-24

### 🛡️ Critical P0 Inode Stability, Symlink Isolation & TOCTOU Verification Gate
- **Permanent Lockfile Inode Stability (P0-01)**: `LifecycleLock` maintains a permanent, stable lockfile/inode across all lifecycle operations. Eliminated `self.lock_path.unlink()` in `__exit__()`, preventing race conditions where unlinked inodes allowed concurrent processes to obtain conflicting exclusive locks on different inodes. On clean exit, payload is reset to `{"status": "released"}` while OS kernel lock is relinquished.
- **Lockfile & Boundary Symlink Protection (P0-02)**: Implemented strict fail-closed symlink rejection on `.lifecycle.lock` and all ancestor directories (`.huynex` up to user home). On POSIX, `os.open` utilizes `O_NOFOLLOW` and compares `fstat` descriptor inode against `lstat` path inode, completely preventing traversal, file truncation, or corruption of external files.
- **Controlled TOCTOU Pre-Mutation Synchronization (TEST-01)**: Rewrote `test_pre_mutation_toctou_absent_to_present_surprise` with deterministic pre-mutation synchronization hook (`pre_mutation_hook`). Proves that when user files appear between planning and mutation, the installer detects them, captures immutable backups, marks ownership as `EXISTED_PRIOR_USER`, and guarantees byte-for-byte restoration upon uninstall without using arbitrary sleeps.
- **Subprocess Kernel Lock Regression Suite (TEST-02)**: Added adversarial multiprocessing tests verifying that lockfile inodes remain identical across sessions, sequential process handoff succeeds cleanly, `proc.kill()` automatically releases locks via OS kernel, and existing released lockfiles are never misidentified as active locks.
- **Lockfile Symlink Regression Suite (TEST-03)**: Added adversarial regression tests proving that direct symlinks at `.lifecycle.lock` and ancestor symlinks at `.huynex` are immediately rejected with non-zero exit codes, leaving external files byte-for-byte unmodified (0 bytes changed/truncated) and writing zero manifests/backups.
- **Data Safety Contract Traceability Synchronization**: Synchronized all invariant verification references and traceability table in `docs/DATA_SAFETY_CONTRACT.md` with runnable test suite names. Clarified benchmark character stream reduction vs. estimated tokens and aligned closed-source agent verification tiers with CI filesystem testing.

## [0.4.0] - 2026-11-24

### 🛡️ Production Hardening & Verified Stable Release Gate
- **OS-Level Kernel File Locking (`fcntl.flock` / `msvcrt.locking`)**: Completely replaced user-space PID checking with kernel file descriptor locking bound to open file descriptors (`fcntl.flock` on POSIX, `msvcrt.locking` on Windows). Guarantees that any process termination (SIGKILL, panic, power failure) immediately releases the lock with zero race conditions and zero stale lock files.
- **Pre-Mutation State Verification & TOCTOU Elimination**: Added immediate pre-mutation disk state verification. Detects surprise files (`absent -> present`), taking immutable backups and assigning `EXISTED_PRIOR_USER` ownership without silent overwrite, and detects mid-operation user modifications (`present -> modified`).
- **Multi-Upgrade Lifecycle Preservation (INV-03)**: Validated data preservation across multi-version upgrades (`pre-existing A -> install v1 -> edit C -> upgrade v2 -> uninstall`). Original user content A is restored byte-for-byte, while interim user modification C is preserved in `.huynex/preserved_user_modified/`.
- **Universal Symlink Protection**: Extended boundary symlink protection to cover all mutation paths, including `configure_claude_guardrail`, `unconfigure_claude_guardrail`, settings files, and parent directories.
- **Semantic Cross-Field Manifest Validation**: Enforced logical consistency checks in `validate_manifest_schema` between `existed_prior`, `ownership`, `managed_mode`, and entry types.
- **Bootstrap Script Fail-Fast Hardening (`install.ps1` & `install.sh`)**: Enforced strict `$LASTEXITCODE` checks after every native command in `install.ps1` and post-checkout revision SHA verification in both bootstrap scripts.
- **Subprocess Concurrency & Crash Regression Suite (`tests/test_concurrency_subprocess.py`)**: 4 new tests verifying real OS subprocess concurrency, SIGKILL termination recovery, and TOCTOU surprise recovery (60/60 passing tests).
- **Formal Data Safety Contract (`docs/DATA_SAFETY_CONTRACT.md`)**: Formalized Safety Invariants INV-01 through INV-09 with full test traceability matrix.

## [0.3.7] - 2026-11-24

### 🛡️ Security, Data Safety & Filesystem Boundaries (Audit #5 Hardening)
- **Ancestor Symlink Boundary Protection (`is_path_or_parent_symlink`)**: Replaced shallow file-only symlink check with full recursive ancestor inspection and boundary escape verification (`resolve()`), guaranteeing that writing through symlinked parent directories never escapes or mutates outside user trees.
- **Double-Hash Write-Ahead Crash Consistency (`sha256_expected_after`)**: Eliminated the crash window between file write and post-mutation manifest update by pre-recording `sha256_expected_after` in the pre-write checkpoint. If a crash occurs and the user edits the file before recovery, `cmd_uninstall()` detects that current file differs from both installed and expected hashes, safely archiving user modifications before restoring backups.
- **Full Planning Lock Scope (TOCTOU Mitigation)**: `LifecycleLock` is now acquired before client discovery, manifest loading, and plan generation, with immediate pre-write disk verification.
- **Dead-Process Stale Lock Reclamation**: `LifecycleLock` inspects the PID in orphaned lock files; if the process died (SIGKILL, power loss, crash), the lock is safely reclaimed without manual user intervention.
- **Strict Manifest Schema Validation (`validate_manifest_schema`)**: Enforced strict runtime type and enum checks for all entry types, modes, ownerships, and backup file references to eliminate invalid state interpretation.
- **Mandatory Backup Verification**: `verify_backup_integrity()` requires a non-empty `expected_sha`; missing metadata refuses restore and flags `UNINSTALL_INCOMPLETE`.
- **PowerShell Wrapper Strict Exit Code Handling (`install.ps1`)**: Added explicit `$LASTEXITCODE` checks after every command execution to guarantee non-zero exit propagation on Windows.
- **Expanded Fault-Injection Regression Suite (`tests/test_fault_injection.py`)**: 10 adversarial tests covering parent symlinks, crash gaps, dead locks, and schema corruption (55/55 total test suite).

## [0.3.6] - 2026-11-24

### 🛡️ Security & Data Safety (Stable Release Gate Hardening)
- **Fail-Closed Corrupt Manifest Handling (`ManifestCorruptError`)**: `load_manifest()` no longer swallows JSON/IO/schema errors into an empty manifest. Any unreadable or corrupt `installed_manifest.json` immediately blocks `install`, `uninstall`, and `doctor` (non-zero exit) while preserving the manifest and all user files intact.
- **Cryptographic SHA-256 Backup Verification (`verify_backup_integrity`)**: `cmd_uninstall()` verifies the SHA-256 digest of every `.bak` file against `sha256_before` prior to restoration. Any hash mismatch refuses overwrite, records `UNINSTALL_INCOMPLETE`, and exits non-zero.
- **Write-Ahead Manifest Checkpointing (Crash Consistency)**: `cmd_install()` checkpoints the manifest atomically BEFORE and AFTER every file mutation (`status: "INSTALL_IN_PROGRESS"` -> `"INSTALLED"`), enabling full byte-for-byte rollback via `cmd_uninstall()` even after mid-install crashes.
- **Cross-Process Lifecycle Locking (`LifecycleLock`)**: Exclusive atomic lock (`O_CREAT | O_EXCL`) at `~/.huynex/.lifecycle.lock` prevents concurrent `install`/`uninstall` processes from racing on manifests or backups.
- **Symlink Safety**: `install.py` skips user symbolic links instead of silently overwriting or unlinking them.
- **Fault-Injection & Concurrency Test Suite (`tests/test_fault_injection.py`)**: 5 new adversarial tests covering corrupt manifests, tampered backups, mid-install crashes, lock contention, and symlinks (50/50 total tests).
- **Release Integrity**: Synchronized `VERSION`, `README.md`, `BENCHMARKS.md`, `CHANGELOG.md`, and added `HUYNEX_REF` pinned ref support to `install.sh` and `install.ps1`.

## [0.3.5] - 2026-11-24

### 🔧 Fixed
- **Legacy v0.3.1 Manifest Ownership**: Migrated v0.3.1 entries are strictly tagged `existed_prior: "UNKNOWN"` / `ownership: "UNKNOWN_LEGACY_V031"` and are never deleted on uninstall.
- **Collision-Free Immutable Backups**: Microsecond backup directory timestamps, 8-char path hashes, exclusive `xb` creation, `fsync`, and read-only `0o444` permissions.
- **Byte-for-Byte Fidelity & Transactional Uninstall**: Preserved `CRLF`/`LF` line endings and trailing whitespace; retained manifest with `UNINSTALL_INCOMPLETE` on partial uninstall failure.
- **State Machine Lifecycle Regression Suite (`tests/test_state_machine_lifecycle.py`)** and explicit 3-tier verification taxonomy in `COMPATIBILITY.md`.

## [0.3.4] - 2026-11-24

### 🔧 Fixed
- Preserved post-install user modifications before restoring backups; collision-free archiving; dynamic acceptance criteria in `huynex-distill --benchmark`; mandatory multi-agent smoke test in CI.

## [0.3.3] - 2026-11-24

### 🔧 Fixed
- Full UTF-8 subprocess encoding fixes across Windows CI; achieved first 9/9 green GitHub Actions matrix (Ubuntu, macOS, Windows x Python 3.10–3.12).

## [0.3.2] - 2026-11-24

### 🔧 Fixed
- Eliminated destructive root file deletion on uninstall; fail-closed guardrail parsing; modularized 9 rules with Claude Code `paths:` scoping and valid Cursor `.mdc` YAML frontmatter.

## [0.3.1] - 2026-11-23

### 🚀 Added
- Added `distill/` engine, `bin/huynex-distill` CLI, unit/adversarial test suite, cross-platform GitHub Actions CI, and security documentation.

## [0.3.0] - 2026-11-18

### 🚀 Added
- **7 Quy tắc Vận hành Đột phá cho AI Coding Agents (rules/)**:
  - `milestone-git-sync.md`: Giao thức tự động đồng bộ Git đơn tầng tinh gọn & Cổng bàn giao mốc hoàn chỉnh (Milestone Mutation Gate — chống Micro-Push Spam và bảo vệ hạn ngạch CI/CD).
  - `proactive-skill-routing.md`: Cơ chế nhận diện ý định & chủ động đề xuất quy trình (Zero-Memorization Standard — người dùng không cần nhớ lệnh slash hay tên thư viện).
  - `goal-ancestry-anti-drift.md`: Phả hệ mục tiêu & Chống lệch hướng trong hệ thống đa Agent (Multi-Agent Workflows — ràng buộc `root_goal`, `scope`, `acceptance_criteria`).
  - `zero-friction-design-contract.md`: Hợp đồng thiết kế giao diện tự động (`DESIGN.md`), triệt tiêu 100% "AI Slop" trong phát triển Frontend.
  - `project-scoped-skills.md`: Quy chuẩn phân tách kỹ năng chuyên biệt theo dự án (Two-Tier Skill Architecture — chống quá tải Context Window và token drain).
  - `conservation-gate.md`: Cổng bảo toàn dữ liệu tuyệt đối (Nothing Vanishes Silently — kiểm toán 2 lớp qua mã băm và số lượng thực thể).
  - `brutal-honesty.md`: Tính trung thực kỹ thuật khách quan (Anti-Sycophancy Standard — triệt tiêu hội chứng nịnh hót, dám cảnh báo rủi ro kiến trúc).

## [0.2.0] - 2026-11-03

### 🚀 Added
- **Tổng quát hóa 4 Kỹ năng Nhóm B (Generalization)**:
  - `shortform-production`: Sản xuất video ngắn 9:16 Top 1 (Hook 3s, CapCut dynamic kinetic motion, Anti-UI clipping safe zone, multi-layer ducking).
  - `shortform-editor`: Biên tập video ngắn 9:16, kịch bản Semantic Beats, căn khớp phụ đề Forced Alignment, nhạc nền Instrumental bản quyền.
  - `brandkit-system`: Hệ thống thiết kế nhận diện thương hiệu cao cấp (Brand Guidelines, editorial grid, logo system).
  - `stitch-design`: Hợp đồng thiết kế giao diện ngữ nghĩa (`DESIGN.md`), triệt tiêu AI Slop.
- **Đóng gói 3 Kỹ năng mới từ Bài học Nhóm D (Group D Lessons)**:
  - `proactive-agent-routing`: Tự động nhận diện bối cảnh và chủ động đề xuất quy trình (Zero-Memorization Standard).
  - `data-conservation-gate`: Cổng bảo toàn dữ liệu tuyệt đối qua mã băm và số lượng thực thể (Nothing Vanishes Silently).
  - `media-audio-gate`: Chốt chặn chuẩn hóa âm thanh số 48kHz, -14.5 dB LUFS và khử rè clipping.
- **Mở rộng kho bài học thực chiến (lessons/)**: Xuất khẩu 9 bài học kỹ thuật chuyên sâu đã khử trùng an toàn 100%.

## [0.1.0] - 2026-11-03

### 🚀 Added
- **5 Kỹ năng AI chuẩn Agent Skills (.agents/skills/)**:
  - `skill-creator`: Framework thiết kế, xây dựng và sinh kiểm thử tự động cho skill mới.
  - `skill-reviewer`: Tiêu chuẩn thẩm định 100 điểm, bảo mật và token economy.
  - `agent-rule-creator`: Phân cấp 3 tầng quy tắc và chống phình to context.
  - `office-openxml-guard`: Xử lý tài liệu Office ECMA-376 chống lỗi hỏng file và tối ưu cuộn bảng biểu.
  - `diagnosing-bugs`: Vòng lặp phản hồi chặt chẽ cho các lỗi khó và sụt giảm hiệu năng.
- **5 Quy tắc vận hành Agent cốt lõi (rules/)**:
  - `ladder-of-laziness.md`: Thang 7 nấc kỹ sư tối giản (Ponytail standard).
  - `verification-gate.md`: Cổng kiểm chứng thực tế & chống lệch hướng (Anti-Drift).
  - `single-root-safety.md`: Bảo vệ cội nguồn workspace và cấm lệnh xóa đệ quy.
  - `board-approval-gate.md`: Cơ chế phân định 3 cấp độ phê duyệt hệ thống.
  - `anti-context-dump.md`: Chưng cất ngữ nghĩa cục bộ tiết kiệm 10x–80x token.
- **Bộ công cụ dòng lệnh (scripts/)**:
  - `install.py`: Trình cài đặt đa nền tảng (macOS, Windows, Linux) hỗ trợ dry-run và backup an toàn.
  - `validate.py`: Bộ kiểm toán tĩnh và quét sạch PII/Secrets.
- **Adapters**: Cấu hình tương thích cho Codex, Claude Code, Antigravity và Cursor.
