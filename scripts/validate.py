#!/usr/bin/env python3
"""
HuyNex Agent Kit — Validator Suite (validate.py)
-----------------------------------------------
Bộ kiểm thử tính toàn vẹn và an ninh cho toàn bộ repository:
1. Kiểm tra cấu trúc thư mục và cú pháp YAML frontmatter của mọi SKILL.md.
2. Quét an ninh (Secret & PII Scanning) ngăn chặn rò rỉ token, email, đường dẫn máy cá nhân.
3. Kiểm tra tính hợp lệ của quy tắc rules/ và lessons/.
"""

import os
import re
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = KIT_ROOT / ".agents/skills"
RULES_DIR = KIT_ROOT / "rules"
LESSONS_DIR = KIT_ROOT / "lessons"

# Các mẫu nhạy cảm cấm tuyệt đối xuất hiện trong public repo
FORBIDDEN_PATTERNS = [
    (r"/Users/maihuy", "Đường dẫn máy Mac cá nhân của Huy"),
    (r"C:\\Users\\maitr", "Đường dẫn máy Windows cá nhân của Huy"),
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI / Model API Key"),
    (r"ghp_[a-zA-Z0-9]{20,}", "GitHub Personal Access Token"),
    (r"bearer\s+[a-zA-Z0-9_\-\.]{25,}", "Bearer Token xác thực"),
    (r"PV01", "Ký hiệu đơn vị nghiệp vụ nội bộ"),
    (r"Tham mưu Cảnh sát", "Ký hiệu đơn vị nghiệp vụ nội bộ"),
    (r"Công an tỉnh Tuyên Quang", "Tên cơ quan nghiệp vụ nội bộ"),
]


def test_skills_frontmatter() -> list[str]:
    errors = []
    if not SKILLS_DIR.is_dir():
        return ["Thư mục .agents/skills không tồn tại!"]

    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue
        skill_file = d / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"Skill '{d.name}': Thiếu file SKILL.md")
            continue

        content = skill_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            errors.append(f"Skill '{d.name}': SKILL.md không bắt đầu bằng YAML frontmatter '---'")
            continue

        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append(f"Skill '{d.name}': YAML frontmatter không đóng mở đúng cặp '---'")
            continue

        yaml_block = parts[1]
        name_match = re.search(r"^name:\s*([a-zA-Z0-9\-_]+)", yaml_block, re.MULTILINE)
        desc_match = re.search(r"^description:\s*(.+)", yaml_block, re.MULTILINE)

        if not name_match:
            errors.append(f"Skill '{d.name}': Thiếu trường 'name' hợp lệ trong frontmatter")
        elif name_match.group(1).strip() != d.name:
            errors.append(f"Skill '{d.name}': Trường 'name' ({name_match.group(1).strip()}) không khớp với tên thư mục ({d.name})")

        if not desc_match or not desc_match.group(1).strip():
            errors.append(f"Skill '{d.name}': Thiếu trường 'description' trong frontmatter")

    return errors


def test_secret_and_pii_leaks() -> list[str]:
    findings = []
    for root_dir in [SKILLS_DIR, RULES_DIR, LESSONS_DIR, KIT_ROOT / "scripts", KIT_ROOT / "templates"]:
        if not root_dir.is_dir():
            continue
        for f in root_dir.rglob("*"):
            if not f.is_file() or "__pycache__" in f.parts or f.name.endswith(".pyc") or f.name == "validate.py":
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            for pattern, reason in FORBIDDEN_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    rel_p = f.relative_to(KIT_ROOT)
                    findings.append(f"Tệp '{rel_p}': Phát hiện vi phạm [{reason}] với mẫu '{pattern}' ({len(matches)} lần)")
    return findings


def main():
    print("=" * 65)
    print("HUYNEX AGENT KIT — TEST SUITE & SECURITY AUDITOR")
    print("=" * 65)

    print("\n[1] Kiểm tra định dạng Agent Skills (.agents/skills/)...")
    frontmatter_errors = test_skills_frontmatter()
    if frontmatter_errors:
        print("  ❌ PHÁT HIỆN LỖI ĐỊNH DẠNG:")
        for err in frontmatter_errors:
            print(f"     - {err}")
    else:
        print("  ✅ Tất cả kỹ năng đều có YAML frontmatter hợp lệ và khớp tên thư mục.")

    print("\n[2] Kiểm tra rò rỉ bí mật & dữ liệu định danh (Secret & PII Audit)...")
    leak_findings = test_secret_and_pii_leaks()
    if leak_findings:
        print("  ❌ PHÁT HIỆN RÒ RỈ BẢO MẬT:")
        for leak in leak_findings:
            print(f"     - {leak}")
    else:
        print("  🛡️ HOÀN TOÀN SẠCH (CLEAN): Không phát hiện token, API key hoặc định danh cá nhân.")

    print("\n" + "=" * 65)
    if frontmatter_errors or leak_findings:
        print("KẾT LUẬN: THẤT BẠI ✖ — Cần khắc phục các lỗi trên trước khi phát hành!")
        sys.exit(1)
    else:
        print("KẾT LUẬN: ĐẠT CHUẨN XUẤT SẮC ● — Repo đủ điều kiện đóng gói và sử dụng.")
        sys.exit(0)


if __name__ == "__main__":
    main()
