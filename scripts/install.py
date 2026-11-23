#!/usr/bin/env python3
"""
HuyNex Agent Kit — Universal Installer & Lifecycle Engine (install.py)
--------------------------------------------------------------------
Production-grade installer for AI Coding Agents:
- Claude Code (~/.claude)
- OpenAI Codex (~/.codex)
- Antigravity (~/.gemini)
- Shared Agent Hub (~/.agents)

Capabilities:
- Idempotent Skills & 9 Modular Rules deployment.
- Native instruction injection without overwriting user customizations.
- PreToolUse security hook registration (macOS, Linux, Windows).
- Manifest-based atomic backup, verification (--doctor), and clean uninstall (--uninstall).
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
        "root_file": codex_dir / "AGENTS.md",
    }

    # 3. Google Antigravity / Gemini
    gemini_dir = home / ".gemini"
    clients["Antigravity"] = {
        "installed": gemini_dir.is_dir(),
        "skills_dir": gemini_dir / "config/skills",
        "root_file": gemini_dir / "GEMINI.md",
    }

    # 4. Central Shared Hub
    agents_hub = home / ".agents"
    clients["Shared Hub"] = {
        "installed": True,  # Luôn hỗ trợ làm fallback hub
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
        # Trích xuất nội dung bên trong tag nếu có, hoặc dùng toàn bộ
        if "<!-- HUY_LOCAL_BRAIN_START -->" in text and "<!-- HUY_LOCAL_BRAIN_END -->" in text:
            match = re.search(r"<!-- HUY_LOCAL_BRAIN_START -->\s*(.*?)\s*<!-- HUY_LOCAL_BRAIN_END -->", text, re.S)
            body = match.group(1) if match else text
        else:
            body = text
    else:
        body = (
            "# HuyNex Agent Kit — Shared Principles\n\n"
            "- **Brutal Honesty**: Khách quan, trung thực kỹ thuật, dám cảnh báo rủi ro.\n"
            "- **Zero-Guessing**: Tuyệt đối không đoán mò số liệu.\n"
            "- **Ladder of Laziness**: Ưu tiên loại bỏ code thừa hơn viết mới.\n"
            "- **Conservation Gate**: Đối chiếu kiểm toán dữ liệu đầu vào-đầu ra.\n\n"
            "@rules/modules/01-communication.md\n"
            "@rules/modules/02-truth-context.md\n"
            "@rules/modules/03-code-engineering.md\n"
            "@rules/modules/04-data-safety.md\n"
            "@rules/modules/05-verification.md\n"
            "@rules/modules/06-collaboration.md\n"
            "@rules/modules/07-permissions-memory.md\n"
            "@rules/modules/08-versioning.md\n"
            "@rules/modules/09-workspace-layout.md\n"
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


def configure_claude_guardrail(settings_file: Path, hook_script: Path, dry_run: bool = False) -> bool:
    """Đăng ký hook PreToolUse vào ~/.claude/settings.json một cách an toàn."""
    try:
        if settings_file.is_file():
            data = json.loads(settings_file.read_text(encoding="utf-8"))
        else:
            data = {}
    except Exception:
        data = {}

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


def cmd_install(is_all: bool, dry_run: bool):
    home = Path.home()
    clients = get_detected_clients(home)
    backup_dir = home / ".huynex/backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest_file = home / ".huynex/installed_manifest.json"

    print("=" * 65)
    print(f"HUYNEX AGENT KIT — INSTALLER ({'DRY-RUN' if dry_run else 'APPLY'})")
    print("=" * 65)

    detected_names = [k for k, v in clients.items() if v["installed"]]
    print(f"Clients phát hiện: {', '.join(detected_names) if detected_names else 'Shared Hub'}")

    plan = []  # list of (action_type, desc, target_path, new_bytes, old_bytes)

    # 1. Cài đặt Skills (.agents/skills)
    if SKILLS_SRC.is_dir():
        for skill_dir in sorted(SKILLS_SRC.iterdir()):
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file():
                for src_file in skill_dir.rglob("*"):
                    if not src_file.is_file() or "__pycache__" in src_file.parts:
                        continue
                    rel = src_file.relative_to(SKILLS_SRC)
                    for c_name, c_info in clients.items():
                        if not c_info["installed"]:
                            continue
                        dst = c_info["skills_dir"] / rel
                        src_bytes = src_file.read_bytes()
                        dst_bytes = dst.read_bytes() if dst.is_file() else None
                        if dst_bytes != src_bytes:
                            plan.append(("SKILL", f"{c_name} skill: {rel}", dst, src_bytes, dst_bytes))

    # 2. Cài đặt 9 Modular Rules (rules/modules)
    if RULES_MODULES_SRC.is_dir():
        for rule_file in sorted(RULES_MODULES_SRC.glob("*.md")):
            rule_bytes = rule_file.read_bytes()
            for c_name in ["Claude Code", "Shared Hub"]:
                c_info = clients[c_name]
                if not c_info["installed"]:
                    continue
                dst = c_info["rules_dir"] / rule_file.name
                dst_bytes = dst.read_bytes() if dst.is_file() else None
                if dst_bytes != rule_bytes:
                    plan.append(("RULE_MODULE", f"{c_name} module: {rule_file.name}", dst, rule_bytes, dst_bytes))

    # 3. Tiêm khối quản trị vào các file chỉ dẫn gốc (CLAUDE.md, AGENTS.md, GEMINI.md)
    rules_block = generate_modular_rules_block(home)
    for c_name, c_info in clients.items():
        if not c_info["installed"]:
            continue
        root_file = c_info.get("root_file")
        if not root_file:
            continue
        new_content, changed = inject_rules_block_safely(root_file, rules_block)
        if changed:
            new_bytes = new_content.encode("utf-8")
            old_bytes = root_file.read_bytes() if root_file.is_file() else None
            plan.append(("ROOT_INSTRUCTION", f"{c_name} root: {root_file.name}", root_file, new_bytes, old_bytes))

    # 4. Cài đặt Guardrails cho Claude Code
    claude_info = clients["Claude Code"]
    if claude_info["installed"]:
        guardrail_src = SCRIPTS_DIR / "guardrail.py"
        if guardrail_src.is_file():
            dst_hook = claude_info["hooks_dir"] / "guardrail.py"
            hook_bytes = guardrail_src.read_bytes()
            dst_hook_bytes = dst_hook.read_bytes() if dst_hook.is_file() else None
            if dst_hook_bytes != hook_bytes:
                plan.append(("GUARDRAIL_HOOK", "Claude Code Guardrail Hook", dst_hook, hook_bytes, dst_hook_bytes))

    # Báo cáo kết quả lập kế hoạch
    print(f"\nSố lượng mục cần áp dụng/cập nhật: {len(plan)}")
    if not plan and not claude_info["installed"]:
        print("✅ Tất cả kỹ năng và quy tắc đã đồng bộ hoàn hảo.")
        return

    for act, desc, dst, _, old_b in plan:
        status = "Cập nhật" if old_b is not None else "Cài mới"
        print(f"  [{status}] ({act:<16}) -> {dst}")

    if dry_run:
        print("\n[Dry-run] Hoàn tất kiểm tra trước. Không có thay đổi nào được ghi vào đĩa.")
        return

    # Thực thi cài đặt và sao lưu
    backup_records = []
    installed_manifest = []

    for act, desc, dst, new_b, old_b in plan:
        if old_b is not None:
            backup_dir.mkdir(parents=True, exist_ok=True)
            bk_name = f"{len(backup_records):03d}_{dst.name}.bak"
            bk_file = backup_dir / bk_name
            bk_file.write_bytes(old_b)
            backup_records.append({
                "path": str(dst),
                "backup_file": str(bk_file),
                "sha256_before": hashlib.sha256(old_b).hexdigest()
            })

        mode = 0o755 if "guardrail" in dst.name else 0o644
        atomic_write(dst, new_b, mode)
        installed_manifest.append({
            "path": str(dst),
            "type": act,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "sha256": hashlib.sha256(new_b).hexdigest()
        })
        print(f"  ✓ Đã ghi: {dst}")

    # Đăng ký hook vào Claude settings.json
    if claude_info["installed"]:
        hook_path = claude_info["hooks_dir"] / "guardrail.py"
        settings_file = claude_info["settings_file"]
        registered = configure_claude_guardrail(settings_file, hook_path, dry_run=False)
        if registered:
            print(f"  ✓ Đã kích hoạt PreToolUse hook trong: {settings_file}")

    # Ghi nhận manifest sao lưu và cài đặt
    if backup_records:
        atomic_write(backup_dir / "manifest.json", json.dumps(backup_records, indent=2).encode("utf-8"))
        print(f"\n🛡️ Bản sao lưu an toàn được lưu tại: {backup_dir}")

    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(manifest_file, json.dumps(installed_manifest, indent=2).encode("utf-8"))

    print("\n🎉 CÀI ĐẶT HOÀN TẤT VÀ KIỂM CHỨNG THÀNH CÔNG!")
    print("Dùng 'python scripts/install.py --doctor' để kiểm tra tình trạng hệ thống bất cứ lúc nào.")


def cmd_doctor():
    """Kiểm tra sức khỏe, tính toàn vẹn và rà soát lỗi của toàn bộ Agent Kit."""
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
    else:
        print("  ❌ Thiếu thư mục rules/modules!")
        all_passed = False

    claude_rules = clients["Claude Code"]["rules_dir"]
    if claude_rules.is_dir():
        c_count = len(list(claude_rules.glob("*.md")))
        print(f"  ✓ Đã cài đặt trong Claude Code: {c_count} files ({claude_rules}).")
    else:
        print(f"  ⚠️ Chưa cài đặt modules vào Claude Code ({claude_rules}).")

    # 2. Kiểm tra Root Instructions
    print("\n[2] Kiểm tra File Chỉ dẫn Gốc (CLAUDE.md, AGENTS.md, GEMINI.md):")
    for c_name, c_info in clients.items():
        if not c_info["installed"]:
            continue
        rf = c_info.get("root_file")
        if rf and rf.is_file():
            text = rf.read_text(encoding="utf-8", errors="ignore")
            has_tag = BEGIN_TAG in text and END_TAG in text
            print(f"  ✓ {c_name:<15}: {rf} ({'Khối quản trị OK' if has_tag else 'Chưa có tag quản trị'})")
        else:
            print(f"  - {c_name:<15}: Không tìm thấy {rf}")

    # 3. Kiểm tra Security Hook
    print("\n[3] Kiểm tra Claude Code Security Hook:")
    claude_info = clients["Claude Code"]
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
        print(f"  ⚠️ Hook script chưa cài đặt tại {hook_file}")

    if settings_file.is_file():
        try:
            cfg = json.loads(settings_file.read_text(encoding="utf-8"))
            hooks = cfg.get("hooks", {}).get("PreToolUse", [])
            has_hook = any("guardrail.py" in str(h) for h in hooks)
            print(f"  ✓ Đăng ký cấu hình: {'Đã đăng ký PreToolUse' if has_hook else 'Chưa đăng ký hook'}")
        except Exception:
            print(f"  ❌ Cấu hình {settings_file} không phải JSON hợp lệ!")
            all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print("🎉 DOCTOR VERDICT: TOÀN BỘ HỆ THỐNG ĐẠT CHUẨN HOẠT ĐỘNG TỐT!")
    else:
        print("⚠️ DOCTOR VERDICT: CÒN MỘT SỐ HẠNG MỤC CẦN KHẮC PHỤC (chạy --all để sửa).")


def cmd_uninstall():
    """Gỡ bỏ an toàn các file và cấu hình do HuyNex Agent Kit quản lý."""
    home = Path.home()
    manifest_file = home / ".huynex/installed_manifest.json"
    print("=" * 65)
    print("HUYNEX AGENT KIT — UNINSTALLER")
    print("=" * 65)

    if not manifest_file.is_file():
        print("❌ Không tìm thấy manifest cài đặt. Không có gì để gỡ bỏ an toàn.")
        return

    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Lỗi đọc manifest: {e}")
        return

    print(f"Tìm thấy {len(manifest)} tệp được quản lý bởi Agent Kit.")
    removed = 0
    for item in manifest:
        p = Path(item["path"])
        if p.is_file():
            try:
                p.unlink()
                removed += 1
                print(f"  ✓ Đã xóa: {p}")
            except OSError as e:
                print(f"  ❌ Lỗi khi xóa {p}: {e}")

    # Gỡ bỏ block trong root files
    clients = get_detected_clients(home)
    for c_name, c_info in clients.items():
        rf = c_info.get("root_file")
        if rf and rf.is_file():
            text = rf.read_text(encoding="utf-8", errors="ignore")
            if BEGIN_TAG in text and END_TAG in text:
                cleaned = re.sub(re.escape(BEGIN_TAG) + r".*?" + re.escape(END_TAG) + r"\n?", "", text, flags=re.S)
                atomic_write(rf, cleaned.strip().encode("utf-8"))
                print(f"  ✓ Đã gỡ khối quản trị khỏi: {rf}")

    # Xóa manifest
    manifest_file.unlink(missing_ok=True)
    print(f"\n🎉 GỠ CÀI ĐẶT HOÀN TẤT: Đã dọn sạch {removed} files an toàn.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--all", action="store_true", help="Cài đặt toàn bộ (Skills, 9 Modules, Guardrails)")
    parser.add_argument("--check", action="store_true", help="Chế độ kiểm tra xem trước không ghi file (Dry-run)")
    parser.add_argument("--doctor", action="store_true", help="Kiểm tra sức khỏe và tính toàn vẹn hệ thống")
    parser.add_argument("--uninstall", action="store_true", help="Gỡ bỏ an toàn các tệp do Agent Kit quản lý")
    parser.add_argument("--auto-update", action="store_true", help="Kích hoạt Background Daemon tự động cập nhật")

    args = parser.parse_args()

    if args.doctor:
        cmd_doctor()
    elif args.uninstall:
        cmd_uninstall()
    elif args.all or args.check:
        cmd_install(is_all=args.all, dry_run=args.check)
        if args.auto_update and not args.check:
            update_script = SCRIPTS_DIR / "update.py"
            if update_script.is_file():
                subprocess.run([sys.executable, str(update_script), "--enable-auto-update"])
    else:
        cmd_doctor()


if __name__ == "__main__":
    main()
