#!/usr/bin/env python3
"""
HuyNex Agent Kit — Universal Installer (install.py)
--------------------------------------------------
Cài đặt kỹ năng và quy tắc vào các AI Agent Clients:
- Codex (~/.codex/skills)
- Claude Code (~/.claude/skills)
- Antigravity (~/.gemini/config/skills)
- Shared Hub (~/.agents/skills)

Hoạt động an toàn trên macOS, Windows và Linux:
- Tự động sao lưu nguyên trạng trước khi ghi đè (Pre-mutation backup).
- Tính toán mã băm SHA-256 chống ghi đè dữ liệu trùng khớp.
- Hỗ trợ chế độ xem trước (Dry-run --check) không thay đổi file.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_SRC = KIT_ROOT / ".agents/skills"
RULES_SRC = KIT_ROOT / "rules"


def sha256_file(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_target_directories(home: Path) -> list[tuple[str, Path]]:
    targets = []
    # 1. Central Agent Skills Hub
    agents_hub = home / ".agents/skills"
    targets.append(("Agent Hub", agents_hub))

    # 2. Codex
    codex_dir = home / ".codex"
    if codex_dir.is_dir():
        targets.append(("Codex", codex_dir / "skills"))

    # 3. Claude Code
    claude_dir = home / ".claude"
    if claude_dir.is_dir():
        targets.append(("Claude Code", claude_dir / "skills"))

    # 4. Antigravity / Gemini
    gemini_dir = home / ".gemini"
    if gemini_dir.is_dir():
        targets.append(("Antigravity", gemini_dir / "config/skills"))

    return targets


def cmd_list():
    print("=" * 65)
    print("DANH MỤC TÀI NGUYÊN HUYNEX AGENT KIT")
    print("=" * 65)
    print("\n[1] KỸ NĂNG (.agents/skills/):")
    if SKILLS_SRC.is_dir():
        for d in sorted(SKILLS_SRC.iterdir()):
            if d.is_dir() and (d / "SKILL.md").is_file():
                # Đọc description ngắn
                desc = ""
                content = (d / "SKILL.md").read_text(encoding="utf-8")
                for line in content.splitlines():
                    if line.startswith("description:"):
                        desc = line.replace("description:", "").strip()
                        break
                print(f"  ⚡ {d.name:<25} - {desc[:60]}...")

    print("\n[2] QUY TẮC VẬN HÀNH (rules/):")
    if RULES_SRC.is_dir():
        for f in sorted(RULES_SRC.glob("*.md")):
            print(f"  🛡️ {f.name}")
    print("=" * 65)


def cmd_install(selected_skill: str, is_all: bool, dry_run: bool):
    home = Path.home()
    targets = get_target_directories(home)

    skills_to_install = []
    if is_all:
        for d in sorted(SKILLS_SRC.iterdir()):
            if d.is_dir() and (d / "SKILL.md").is_file():
                skills_to_install.append(d)
    elif selected_skill:
        target_dir = SKILLS_SRC / selected_skill
        if target_dir.is_dir() and (target_dir / "SKILL.md").is_file():
            skills_to_install.append(target_dir)
        else:
            print(f"❌ Không tìm thấy skill: '{selected_skill}' trong {SKILLS_SRC}")
            sys.exit(1)
    else:
        print("Vui lòng chỉ định --all hoặc --skill <tên-skill>. Dùng --list để xem danh mục.")
        sys.exit(1)

    print("=" * 65)
    print(f"BẮT ĐẦU CÀI ĐẶT (Chế độ: {'KIỂM TRA (DRY-RUN)' if dry_run else 'THỰC THI (APPLY)'})")
    print("=" * 65)
    print(f"Tổng số kỹ năng: {len(skills_to_install)}")
    print(f"Các client được phát hiện trên máy:")
    for name, path in targets:
        print(f"  - {name}: {path}")

    plan = []
    for skill in skills_to_install:
        for src_file in skill.rglob("*"):
            if not src_file.is_file() or "__pycache__" in src_file.parts:
                continue
            rel_path = src_file.relative_to(SKILLS_SRC)
            for client_name, target_root in targets:
                dst_file = target_root / rel_path
                src_hash = sha256_file(src_file)
                dst_hash = sha256_file(dst_file) if dst_file.is_file() else None
                if src_hash != dst_hash:
                    plan.append((client_name, src_file, dst_file, dst_hash is not None))

    print(f"\nSố tệp cần thay đổi/cập nhật: {len(plan)}")
    if not plan:
        print("✅ Tất cả kỹ năng đã đồng bộ hoàn hảo, không có file nào cần cập nhật.")
        return

    if dry_run:
        for client_name, src, dst, existed in plan:
            status = "Cập nhật" if existed else "Cài mới"
            print(f"  [{status}] {client_name} -> {dst}")
        print("\nHoàn tất kiểm tra (Dry-run). Dùng lệnh không có cờ --check để thực thi.")
        return

    # Sao lưu trước khi apply
    backup_dir = home / ".huynex/backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_records = []
    for client_name, src, dst, existed in plan:
        if existed:
            backup_dir.mkdir(parents=True, exist_ok=True)
            rel_bk = dst.name + f".{len(backup_records)}.bak"
            bk_path = backup_dir / rel_bk
            shutil.copy2(dst, bk_path)
            backup_records.append({"original": str(dst), "backup": str(bk_path)})

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  ✓ Đã cài đặt: {dst}")

    if backup_records:
        (backup_dir / "manifest.json").write_text(json.dumps(backup_records, indent=2), encoding="utf-8")
        print(f"\n🛡️ Đã sao lưu các file cũ vào: {backup_dir}")

    print("\n🎉 Cài đặt hoàn tất thành công! Hãy mở phiên agent mới để trải nghiệm.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="Liệt kê toàn bộ skills và rules")
    parser.add_argument("--all", action="store_true", help="Cài đặt toàn bộ skills")
    parser.add_argument("--skill", type=str, help="Cài đặt một skill cụ thể theo tên")
    parser.add_argument("--check", action="store_true", help="Chế độ kiểm tra xem trước (Dry-run)")
    parser.add_argument("--auto-update", action="store_true", help="Kích hoạt Background Daemon tự động phát hiện và kéo cập nhật khi có git mới")

    args = parser.parse_args()

    if args.list:
        cmd_list()
    elif args.all or args.skill:
        cmd_install(args.skill, args.all, args.check)
        if args.auto_update and not args.check:
            print("\n🔄 Đang thiết lập Background Daemon tự động cập nhật...")
            import subprocess
            subprocess.run([sys.executable, str(SCRIPTS_DIR / "update.py"), "--enable-auto-update"])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
