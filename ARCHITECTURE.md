# HuyNex Agent Kit — System Architecture & Core Freeze Policy

```
+-------------------------------------------------------------------------+
|                  TIER 1: HUYNEX CORE (STABLE FROZEN CORE)               |
|   (Installer, OS Kernel Locking, Double-Hash WAL, Atomic Write,        |
|    Cryptographic Backup, Recovery Engine, Doctor Integrity Auditor)      |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  TIER 2: AGENT ADAPTERS & CLIENT BOUNDARIES             |
|    (Claude Code @import, Codex AGENTS.md, Antigravity, Cursor .mdc)     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  TIER 3: RULES & SKILLS (EXTENSIBLE CONTENT)            |
|       (9 Modular Rules in rules/modules/, Agent Skills in .agents/)     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|             TIER 4: DETERMINISTIC RUNTIME DEFENSES                      |
|  (PreToolUse Guardrails, huynex-distill Token Distiller, Spec Gate)    |
+-------------------------------------------------------------------------+
```

---

## 🛡️ Long-Term Development Governance

### 1. Conditional Frozen Core (Bảo vệ Lõi ổn định v0.4.1)
- **Scope of Core**: `scripts/install.py`, `install.sh`, `install.ps1`, và `docs/DATA_SAFETY_CONTRACT.md`.
- **Policy**: Core v0.4.1 được **đóng băng có điều kiện**. Khi bổ sung Skills, Rules mới hoặc tinh chỉnh prompt, **TUYỆT ĐỐI KHÔNG sửa Core**.
- **Exception Rule**: Chỉ sửa Core khi phát hiện lỗ hổng an toàn dữ liệu thực tế (P0/P1) hoặc khi thêm một Agent Adapter mới có yêu cầu cấu trúc tệp mà Core hiện tại chưa hỗ trợ. Mọi thay đổi đối với Core bắt buộc phải vượt qua 100% bộ kiểm thử 65 tests trên cả 3 hệ điều hành.

### 2. Extensible Content Tier (Phát triển liên tục)
- **Thêm Skills**: Chỉ cần tạo thư mục mới trong `.agents/skills/<skill-name>/` với tệp `SKILL.md` hợp lệ. Installer v0.4.1 tự động quét và phân phối.
- **Cải tiến Rules**: Chỉ cần cập nhật hoặc thêm tệp `.md` trong `rules/modules/`. Installer tự động định dạng sang `.mdc` cho Cursor và `@rules/` cho Claude Code.

---

## 🏗️ Architectural Invariants

1. **Separation of Policy and Execution**:
   - Instructions are declarations of intent (Soft Policy).
   - Shell hooks and filters are deterministic barriers (Hard Guards).
   - Never conflate prompt instructions with operating system isolation.

2. **The Conservation Gate**:
   - Any transformation, compression, or distillation step must verify its input against output (`sourceHash` or error indicator preservation).
   - If a failure indicator is present in raw input but missing in distilled output, the system fails closed and falls back to raw data.

3. **YAGNI & Zero External Dependencies**:
   - Built 100% on standard library Python, POSIX shell, and PowerShell. No third-party pip dependencies required.
   - Idempotent lifecycle management: install, doctor, verify, and transactional uninstall with byte-for-byte fidelity.
