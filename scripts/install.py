#!/usr/bin/env python3
"""
HuyNex Agent Kit — Universal Installer & Lifecycle Engine (install.py)
--------------------------------------------------------------------
Production-grade installer for AI Coding Agents:
- Claude Code (~/.claude)
- OpenAI Codex (~/.codex)
- Antigravity (~/.gemini)
- Cursor (~/.cursor)
- Shared Agent Hub (~/.agents)

Capabilities:
- Idempotent Skills & 9 Modular Rules deployment.
- Non-destructive managed block injection with atomic writes.
- Bulletproof uninstaller: NEVER deletes pre-existing user files, only strips tags.
- PreToolUse security hook registration and clean unregistration.
- Manifest-based backup, restore, verification (--doctor with proper exit codes).
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Ensure UTF-8 output on all platforms (including Windows consoles)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

KIT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_SRC = KIT_ROOT / ".agents/skills"
RULES_SRC = KIT_ROOT / "rules"
RULES_MODULES_SRC = KIT_ROOT / "rules/modules"
SCRIPTS_DIR = KIT_ROOT / "scripts"

BEGIN_TAG = "<!-- HUYNEX_AGENT_KIT_START -->"
END_TAG = "<!-- HUYNEX_AGENT_KIT_END -->"


def sha256_file(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def atomic_write(target_path: Path, content: bytes, mode: int = 0o644):
    """Ghi file an toàn nguyên tử (atomic write) chống corrupt dữ liệu khi bị ngắt."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".huynex-tmp-", dir=target_path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, target_path)
    finally:
        if os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def get_detected_clients(home: Path) -> dict[str, dict]:
    """Phát hiện các AI Agent Clients đang có trên máy."""
    clients = {}

    # 1. Claude Code
    claude_dir = home / ".claude"
    clients["Claude Code"] = {
        "installed": claude_dir.is_dir(),
        "skills_dir": claude_dir / "skills",
        "rules_dir": claude_dir / "rules",
        "root_file": claude_dir / "CLAUDE.md",
        "hooks_dir": claude_dir / "hooks",
        "settings_file": claude_dir / "settings.json",
    }

    # 2. OpenAI Codex
    codex_dir = home / ".codex"
    clients["Codex"] = {
        "installed": codex_dir.is_dir(),
        "skills_dir": codex_dir / "skills",
        "rules_dir": codex_dir / "rules",
        "root_file": codex_dir / "AGENTS.md",
    }

    # 3. Google Antigravity / Gemini
    gemini_dir = home / ".gemini"
    clients["Antigravity"] = {
        "installed": gemini_dir.is_dir(),
        "skills_dir": gemini_dir / "config/skills",
        "root_file": gemini_dir / "GEMINI.md",
    }

    # 4. Cursor
    cursor_dir = home / ".cursor"
    clients["Cursor"] = {
        "installed": cursor_dir.is_dir(),
        "rules_dir": cursor_dir / "rules",
        "root_file": cursor_dir / "AGENTS.md",
    }

    # 5. Central Shared Hub (Fallback & cross-agent hub)
    agents_hub = home / ".agents"
    clients["Shared Hub"] = {
        "installed": True,
        "skills_dir": agents_hub / "skills",
        "rules_dir": agents_hub / "rules",
        "root_file": agents_hub / "AGENTS.md",
    }

    return clients


def generate_modular_rules_block(home: Path) -> str:
    """Tạo khối nội dung quản trị modular cho file chỉ dẫn gốc."""
    template_path = RULES_SRC / "CLAUDE.template.md"
    if template_path.is_file():
        text = template_path.read_text(encoding="utf-8")
        if "<!-- HUY_LOCAL_BRAIN_START -->" in text and "<!-- HUY_LOCAL_BRAIN_END -->" in text:
            match = re.search(r"<!-- HUY_LOCAL_BRAIN_START -->\s*(.*?)\s*<!-- HUY_LOCAL_BRAIN_END -->", text, re.S)
            body = match.group(1) if match else text
        elif BEGIN_TAG in text and END_TAG in text:
            match = re.search(re.escape(BEGIN_TAG) + r"\s*(.*?)\s*" + re.escape(END_TAG), text, re.S)
            body = match.group(1) if match else text
        else:
            body = text
    else:
        body = (
            "# HuyNex Agent Kit — Universal Core Principles\n\n"
            "- **Brutal Honesty**: Objective technical truth, prompt risk escalation.\n"
            "- **Zero-Guessing**: Verify numbers and specifications from ground truth.\n"
            "- **Ladder of Laziness**: Prefer standard library and removal over adding code.\n"
            "- **Conservation Gate**: Audit input/output parity; prevent silent data loss.\n"
        )

    return f"{BEGIN_TAG}\n{body.strip()}\n{END_TAG}\n"


def inject_rules_block_safely(target_file: Path, managed_block: str) -> tuple[str, bool]:
    """Cập nhật hoặc tiêm block quản trị mà bảo toàn 100% nội dung cá nhân khác của người dùng."""
    if not target_file.is_file():
        return managed_block, True

    existing_text = target_file.read_text(encoding="utf-8", errors="ignore")
    if BEGIN_TAG in existing_text and END_TAG in existing_text:
        new_text = re.sub(
            re.escape(BEGIN_TAG) + r".*?" + re.escape(END_TAG) + r"\n?",
            managed_block,
            existing_text,
            flags=re.S,
        )
        changed = new_text != existing_text
        return new_text, changed
    else:
        # Giữ nguyên nội dung cũ và nối thêm block quản trị
        new_text = existing_text.rstrip() + "\n\n" + managed_block
        return new_text, True


def strip_rules_block_safely(target_file: Path) -> tuple[str, bool]:
    """Loại bỏ khối quản trị của HuyNex khỏi file, giữ lại 100% nội dung riêng của người dùng."""
    if not target_file.is_file():
        return "", False

    existing_text = target_file.read_text(encoding="utf-8", errors="ignore")
    if BEGIN_TAG in existing_text and END_TAG in existing_text:
        cleaned = re.sub(
            re.escape(BEGIN_TAG) + r".*?" + re.escape(END_TAG) + r"\n?",
            "",
            existing_text,
            flags=re.S,
        ).strip()
        return cleaned, True
    return existing_text, False


def configure_claude_guardrail(settings_file: Path, hook_script: Path, dry_run: bool = False) -> bool:
    """Đăng ký hook PreToolUse vào ~/.claude/settings.json một cách an toàn."""
    data = {}
    if settings_file.is_file():
        raw = settings_file.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except Exception as e:
            # P0 DATA SAFETY: KHÔNG ghi đè {} lên file hỏng của người dùng
            print(f"  ❌ CẢNH BÁO: Không thể parse {settings_file} ({e}).")
            print("     Để bảo vệ dữ liệu, hủy đăng ký hook tự động cho settings.json này.")
            return False

    if "hooks" not in data:
        data["hooks"] = {}

    pre_hooks = data["hooks"].get("PreToolUse", [])
    hook_cmd = f"python3 \"{hook_script}\"" if sys.platform != "win32" else f"python \"{hook_script}\""

    # Kiểm tra xem hook đã được đăng ký chưa
    already_registered = False
    for item in pre_hooks:
        if item.get("matcher") == "Bash":
            for sub in item.get("hooks", []):
                if "guardrail.py" in sub.get("command", ""):
                    already_registered = True
                    break

    if already_registered:
        return False

    if not dry_run:
        pre_hooks.append({
            "matcher": "Bash",
            "hooks": [
                {
                    "type": "command",
                    "command": hook_cmd
                }
            ]
        })
        data["hooks"]["PreToolUse"] = pre_hooks
        atomic_write(settings_file, json.dumps(data, indent=2).encode("utf-8"))

    return True


def unconfigure_claude_guardrail(settings_file: Path) -> bool:
    """Gỡ bỏ an toàn đăng ký guardrail hook khỏi ~/.claude/settings.json."""
    if not settings_file.is_file():
        return False

    try:
        data = json.loads(settings_file.read_text(encoding="utf-8"))
    except Exception:
        return False

    if "hooks" not in data or "PreToolUse" not in data["hooks"]:
        return False

    pre_hooks = data["hooks"]["PreToolUse"]
    new_pre_hooks = []
    removed = False

    for item in pre_hooks:
        sub_hooks = item.get("hooks", [])
        filtered_sub = [h for h in sub_hooks if "guardrail.py" not in h.get("command", "")]
        if len(filtered_sub) != len(sub_hooks):
            removed = True
        if filtered_sub:
            item["hooks"] = filtered_sub
            new_pre_hooks.append(item)

    if removed:
        data["hooks"]["PreToolUse"] = new_pre_hooks
        atomic_write(settings_file, json.dumps(data, indent=2).encode("utf-8"))
        return True
    return False


def load_manifest(manifest_file: Path) -> dict:
    if manifest_file.is_file():
        try:
            return json.loads(manifest_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"version": "0.3.2", "entries": {}}


def save_manifest(manifest_file: Path, manifest_data: dict):
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(manifest_file, json.dumps(manifest_data, indent=2).encode("utf-8"))


def cmd_install(is_all: bool, dry_run: bool):
    home = Path.home()
    clients = get_detected_clients(home)
    backup_dir = home / ".huynex/backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest_file = home / ".huynex/installed_manifest.json"
    manifest_data = load_manifest(manifest_file)
    active_entries = manifest_data.get("entries", {})

    print("=" * 65)
    print(f"HUYNEX AGENT KIT — INSTALLER ({'DRY-RUN' if dry_run else 'APPLY'})")
    print("=" * 65)

    detected_names = [k for k, v in clients.items() if v["installed"]]
    print(f"Clients phát hiện: {', '.join(detected_names) if detected_names else 'Shared Hub'}")

    plan = []  # list of (action_type, desc, target_path, new_bytes, old_bytes, existed_before)

    # 1. Cài đặt Skills (.agents/skills)
    if SKILLS_SRC.is_dir():
        for skill_dir in sorted(SKILLS_SRC.iterdir()):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file():
                for src_file in skill_dir.rglob("*"):
                    if not src_file.is_file() or "__pycache__" in src_file.parts:
                        continue
                    rel = src_file.relative_to(SKILLS_SRC)
                    for c_name, c_info in clients.items():
                        if not c_info["installed"] or "skills_dir" not in c_info:
                            continue
                        dst = c_info["skills_dir"] / rel
                        src_bytes = src_file.read_bytes()
                        existed = dst.is_file()
                        dst_bytes = dst.read_bytes() if existed else None
                        if dst_bytes != src_bytes:
                            plan.append(("SKILL", f"{c_name} skill: {rel}", dst, src_bytes, dst_bytes, existed))

    # 2. Cài đặt 9 Modular Rules (rules/modules)
    if RULES_MODULES_SRC.is_dir():
        for rule_file in sorted(RULES_MODULES_SRC.glob("*.md")):
            rule_bytes = rule_file.read_bytes()
            for c_name in ["Claude Code", "Codex", "Cursor", "Shared Hub"]:
                c_info = clients[c_name]
                if not c_info["installed"] or "rules_dir" not in c_info:
                    continue
                dst = c_info["rules_dir"] / rule_file.name
                existed = dst.is_file()
                dst_bytes = dst.read_bytes() if existed else None
                if dst_bytes != rule_bytes:
                    plan.append(("RULE_MODULE", f"{c_name} module: {rule_file.name}", dst, rule_bytes, dst_bytes, existed))

    # 3. Tiêm khối quản trị vào các file chỉ dẫn gốc (CLAUDE.md, AGENTS.md, GEMINI.md)
    rules_block = generate_modular_rules_block(home)
    for c_name, c_info in clients.items():
        if not c_info["installed"]:
            continue
        root_file = c_info.get("root_file")
        if not root_file:
            continue
        existed = root_file.is_file()
        new_content, changed = inject_rules_block_safely(root_file, rules_block)
        if changed:
            new_bytes = new_content.encode("utf-8")
            old_bytes = root_file.read_bytes() if existed else None
            plan.append(("ROOT_INSTRUCTION", f"{c_name} root: {root_file.name}", root_file, new_bytes, old_bytes, existed))

    # 4. Cài đặt Guardrails cho Claude Code
    claude_info = clients["Claude Code"]
    if claude_info["installed"]:
        guardrail_src = SCRIPTS_DIR / "guardrail.py"
        if guardrail_src.is_file():
            dst_hook = claude_info["hooks_dir"] / "guardrail.py"
            hook_bytes = guardrail_src.read_bytes()
            existed = dst_hook.is_file()
            dst_hook_bytes = dst_hook.read_bytes() if existed else None
            if dst_hook_bytes != hook_bytes:
                plan.append(("GUARDRAIL_HOOK", "Claude Code Guardrail Hook", dst_hook, hook_bytes, dst_hook_bytes, existed))

    # Báo cáo kết quả lập kế hoạch
    print(f"\nSố lượng mục cần áp dụng/cập nhật: {len(plan)}")
    for act, desc, dst, _, old_b, existed in plan:
        status = "Cập nhật" if existed else "Cài mới"
        print(f"  [{status}] ({act:<16}) -> {dst}")

    if dry_run:
        print("\n[Dry-run] Hoàn tất kiểm tra trước. Không có thay đổi nào được ghi vào đĩa.")
        return

    # Thực thi cài đặt và sao lưu
    backup_records = []

    for act, desc, dst, new_b, old_b, existed in plan:
        bk_file_str = None
        if old_b is not None:
            backup_dir.mkdir(parents=True, exist_ok=True)
            bk_name = f"{len(backup_records):03d}_{dst.name}.bak"
            bk_file = backup_dir / bk_name
            bk_file.write_bytes(old_b)
            bk_file_str = str(bk_file)
            backup_records.append({
                "path": str(dst),
                "backup_file": bk_file_str,
                "sha256_before": hashlib.sha256(old_b).hexdigest()
            })

        mode = 0o755 if "guardrail" in dst.name else 0o644
        atomic_write(dst, new_b, mode)

        # Ghi nhận trạng thái sở hữu tệp (P0 Data Safety)
        active_entries[str(dst)] = {
            "type": act,
            "managed_mode": "injected_block" if act == "ROOT_INSTRUCTION" and existed else "managed_file",
            "existed_prior": existed,
            "backup_file": bk_file_str or active_entries.get(str(dst), {}).get("backup_file"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "sha256": hashlib.sha256(new_b).hexdigest()
        }
        print(f"  ✓ Đã ghi: {dst}")

    # Đăng ký hook vào Claude settings.json
    if claude_info["installed"]:
        hook_path = claude_info["hooks_dir"] / "guardrail.py"
        settings_file = claude_info["settings_file"]
        registered = configure_claude_guardrail(settings_file, hook_path, dry_run=False)
        if registered:
            print(f"  ✓ Đã kích hoạt PreToolUse hook trong: {settings_file}")

    # Lưu bản sao lưu và manifest cập nhật
    if backup_records:
        atomic_write(backup_dir / "manifest.json", json.dumps(backup_records, indent=2).encode("utf-8"))
        print(f"\n🛡️ Bản sao lưu an toàn được lưu tại: {backup_dir}")

    manifest_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    manifest_data["entries"] = active_entries
    save_manifest(manifest_file, manifest_data)

    print("\n🎉 CÀI ĐẶT HOÀN TẤT VÀ KIỂM CHỨNG THÀNH CÔNG!")
    print("Dùng 'python scripts/install.py --doctor' để kiểm tra tình trạng hệ thống bất cứ lúc nào.")


def cmd_doctor() -> bool:
    """Kiểm tra sức khỏe, tính toàn vẹn và rà soát lỗi của toàn bộ Agent Kit.
    Trả về True nếu pass 100%, False nếu có bất kỳ lỗi nào."""
    home = Path.home()
    clients = get_detected_clients(home)
    print("=" * 65)
    print("HUYNEX AGENT KIT — DOCTOR & INTEGRITY AUDITOR")
    print("=" * 65)

    all_passed = True

    # 1. Kiểm tra 9 Modules
    print("\n[1] Kiểm tra 9 Modules Quản trị (rules/modules):")
    if RULES_MODULES_SRC.is_dir():
        mod_count = len(list(RULES_MODULES_SRC.glob("*.md")))
        print(f"  ✓ Nguồn modules: {mod_count} files có sẵn.")
        if mod_count < 9:
            print(f"  ❌ Chỉ tìm thấy {mod_count}/9 modules nguồn!")
            all_passed = False
    else:
        print("  ❌ Thiếu thư mục rules/modules!")
        all_passed = False

    claude_rules = clients["Claude Code"]["rules_dir"]
    if clients["Claude Code"]["installed"]:
        if claude_rules.is_dir():
            c_count = len(list(claude_rules.glob("*.md")))
            print(f"  ✓ Đã cài đặt trong Claude Code: {c_count} files ({claude_rules}).")
            if c_count < 9:
                print(f"  ❌ Thiếu modules trong Claude Code: chỉ có {c_count}/9 files!")
                all_passed = False
        else:
            print(f"  ❌ Chưa cài đặt modules vào Claude Code ({claude_rules})!")
            all_passed = False

    # 2. Kiểm tra Root Instructions
    print("\n[2] Kiểm tra File Chỉ dẫn Gốc (CLAUDE.md, AGENTS.md, GEMINI.md):")
    checked_roots = 0
    for c_name, c_info in clients.items():
        if not c_info["installed"]:
            continue
        rf = c_info.get("root_file")
        if rf and rf.is_file():
            checked_roots += 1
            text = rf.read_text(encoding="utf-8", errors="ignore")
            has_tag = BEGIN_TAG in text and END_TAG in text
            if has_tag:
                print(f"  ✓ {c_name:<15}: {rf} (Khối quản trị OK)")
            else:
                print(f"  ⚠️ {c_name:<15}: {rf} (Chưa có tag quản trị)")
                all_passed = False
        else:
            if c_name in ["Claude Code", "Codex"]:
                print(f"  ⚠️ {c_name:<15}: Không tìm thấy {rf}")
                all_passed = False

    # 3. Kiểm tra Security Hook
    print("\n[3] Kiểm tra Claude Code Security Hook:")
    claude_info = clients["Claude Code"]
    if claude_info["installed"]:
        hook_file = claude_info["hooks_dir"] / "guardrail.py"
        settings_file = claude_info["settings_file"]

        if hook_file.is_file():
            print(f"  ✓ Hook script: {hook_file} (Quyền thực thi: {oct(hook_file.stat().st_mode)[-3:]})")
            # Chạy thử hook bằng mock input
            try:
                res = subprocess.run(
                    [sys.executable, str(hook_file)],
                    input=b'{"tool_input":{"command":"git push --force"}}',
                    capture_output=True
                )
                if res.returncode == 2:
                    print("  ✓ Hook test đối kháng (git push --force): Chặn thành công (Exit 2).")
                else:
                    print(f"  ❌ Hook test thất bại: Returncode={res.returncode}")
                    all_passed = False
            except Exception as e:
                print(f"  ❌ Lỗi khi chạy thử hook: {e}")
                all_passed = False
        else:
            print(f"  ❌ Hook script chưa cài đặt tại {hook_file}")
            all_passed = False

        if settings_file.is_file():
            try:
                cfg = json.loads(settings_file.read_text(encoding="utf-8"))
                hooks = cfg.get("hooks", {}).get("PreToolUse", [])
                has_hook = any("guardrail.py" in str(h) for h in hooks)
                if has_hook:
                    print("  ✓ Đăng ký cấu hình: Đã đăng ký PreToolUse")
                else:
                    print("  ❌ Đăng ký cấu hình: Chưa đăng ký hook trong settings.json!")
                    all_passed = False
            except Exception:
                print(f"  ❌ Cấu hình {settings_file} không phải JSON hợp lệ!")
                all_passed = False
        else:
            print(f"  ❌ File cấu hình Claude Code không tồn tại: {settings_file}")
            all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print("🎉 DOCTOR VERDICT: TOÀN BỘ HỆ THỐNG ĐẠT CHUẨN HOẠT ĐỘNG TỐT!")
        return True
    else:
        print("❌ DOCTOR VERDICT: PHÁT HIỆN HẠNG MỤC CHƯA ĐẠT (Chạy 'python scripts/install.py --all' để sửa).")
        return False


def cmd_uninstall():
    """Gỡ bỏ an toàn các file và cấu hình do HuyNex Agent Kit quản lý.
    P0 DATA SAFETY: TUYỆT ĐỐI KHÔNG XÓA FILE CÁ NHÂN GỐC CỦA NGƯỜI DÙNG!"""
    home = Path.home()
    manifest_file = home / ".huynex/installed_manifest.json"
    print("=" * 65)
    print("HUYNEX AGENT KIT — SAFE UNINSTALLER")
    print("=" * 65)

    if not manifest_file.is_file():
        print("❌ Không tìm thấy manifest cài đặt. Tiến hành dọn dẹp theo heuristics an toàn...")
        manifest_data = {"entries": {}}
    else:
        manifest_data = load_manifest(manifest_file)

    entries = manifest_data.get("entries", {})
    cleaned_count = 0
    unlinked_count = 0

    # 1. Gỡ bỏ các tệp được ghi nhận trong manifest
    for path_str, meta in list(entries.items()):
        p = Path(path_str)
        if not p.is_file():
            continue

        managed_mode = meta.get("managed_mode", "managed_file")
        existed_prior = meta.get("existed_prior", False)
        item_type = meta.get("type", "")

        # P0 DATA SAFETY RULE:
        # Nếu là ROOT_INSTRUCTION hoặc file đã tồn tại trước đó:
        # CHỈ ĐƯỢC PHÉP gỡ bỏ block <!-- HUYNEX_AGENT_KIT_START -->, KHÔNG ĐƯỢC UNLINK!
        if item_type == "ROOT_INSTRUCTION" or managed_mode == "injected_block" or existed_prior:
            cleaned_text, was_stripped = strip_rules_block_safely(p)
            if was_stripped:
                # Nếu file trống hoàn toàn sau khi strip và trước đây không tồn tại:
                if not cleaned_text and not existed_prior:
                    p.unlink(missing_ok=True)
                    unlinked_count += 1
                    print(f"  ✓ Đã xóa file rỗng do HuyNex tạo mới: {p}")
                else:
                    atomic_write(p, cleaned_text.encode("utf-8"))
                    cleaned_count += 1
                    print(f"  ✓ Đã gỡ khối quản trị, BẢO TOÀN nội dung riêng của người dùng: {p}")
        else:
            # File do HuyNex hoàn toàn tạo mới (skills, standalone rules, hook script)
            # Kiểm tra xem có bị người dùng sửa thêm nội dung ngoài không
            try:
                p.unlink(missing_ok=True)
                unlinked_count += 1
                print(f"  ✓ Đã xóa file do HuyNex cài: {p}")
            except OSError as e:
                print(f"  ❌ Lỗi khi xóa {p}: {e}")

    # 2. Quét dọn fallback đối với các file root nếu manifest bị thiếu
    clients = get_detected_clients(home)
    for c_name, c_info in clients.items():
        rf = c_info.get("root_file")
        if rf and rf.is_file():
            cleaned_text, was_stripped = strip_rules_block_safely(rf)
            if was_stripped:
                atomic_write(rf, cleaned_text.encode("utf-8"))
                cleaned_count += 1
                print(f"  ✓ Fallback: Đã gỡ khối quản trị khỏi {c_name} root: {rf}")

    # 3. Gỡ bỏ đăng ký hook khỏi Claude settings.json
    claude_settings = clients["Claude Code"]["settings_file"]
    if claude_settings.is_file():
        unregistered = unconfigure_claude_guardrail(claude_settings)
        if unregistered:
            print(f"  ✓ Đã gỡ bỏ đăng ký PreToolUse hook khỏi: {claude_settings}")

    # 4. Xóa manifest
    manifest_file.unlink(missing_ok=True)
    print(f"\n🎉 GỠ CÀI ĐẶT AN TOÀN HOÀN TẤT: {unlinked_count} files đã xóa, {cleaned_count} files được giữ nguyên và gỡ tag.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--all", action="store_true", help="Cài đặt toàn bộ (Skills, 9 Modules, Guardrails)")
    parser.add_argument("--check", action="store_true", help="Chế độ kiểm tra xem trước không ghi file (Dry-run)")
    parser.add_argument("--doctor", action="store_true", help="Kiểm tra sức khỏe và tính toàn vẹn hệ thống")
    parser.add_argument("--uninstall", action="store_true", help="Gỡ bỏ an toàn các tệp do Agent Kit quản lý")
    parser.add_argument("--auto-update", action="store_true", help="Kích hoạt Background Daemon tự động cập nhật")

    args = parser.parse_args()

    if args.doctor:
        ok = cmd_doctor()
        sys.exit(0 if ok else 1)
    elif args.uninstall:
        cmd_uninstall()
        sys.exit(0)
    elif args.all or args.check:
        cmd_install(is_all=args.all, dry_run=args.check)
        if args.auto_update and not args.check:
            update_script = SCRIPTS_DIR / "update.py"
            if update_script.is_file():
                subprocess.run([sys.executable, str(update_script), "--enable-auto-update"])
    else:
        ok = cmd_doctor()
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
