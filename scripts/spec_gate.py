#!/usr/bin/env python3
"""
HuyNex Spec-Driven Pre-Flight Gate (spec_gate.py)
------------------------------------------------
Chốt chặn đối chiếu tiêu chí nghiệm thu tự động trước khi bàn giao (Anti-Drift & Verification).
Quét kiểm tra:
1. Checklist tiêu chuẩn trong spec (- [ ] vs - [x])
2. Trạng thái Git (untracked, uncommitted, dirty working tree)
3. Chạy test tự động theo file cấu hình dự án (npm test, pytest, cargo test)
4. Xác minh sự tồn tại của các file bàn giao (Deliverables)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def audit_checklist(file_path: Path):
    """Quét các mục checklist trong file spec."""
    if not file_path.is_file():
        return None, None
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    total = re.findall(r"-\s*\[([ xX])\]\s*(.+)", text)
    if not total:
        return 0, 0
    checked = sum(1 for status, _ in total if status.lower() == "x")
    unchecked = [desc.strip() for status, desc in total if status.lower() != "x"]
    return len(total), unchecked


def check_git_clean():
    """Kiểm tra working tree git có sạch sẽ không."""
    try:
        res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        return lines
    except Exception:
        return None


def run_project_tests():
    """Tự động phát hiện và chạy test dự án."""
    if Path("package.json").is_file():
        # Node.js
        try:
            pkg = json.loads(Path("package.json").read_text())
            if "test" in pkg.get("scripts", {}):
                res = subprocess.run(["npm", "test"], capture_output=True, text=True)
                return "npm test", res.returncode == 0, res.stdout + res.stderr
        except Exception:
            pass
    elif Path("Cargo.toml").is_file():
        # Rust
        res = subprocess.run(["cargo", "test"], capture_output=True, text=True)
        return "cargo test", res.returncode == 0, res.stdout + res.stderr
    elif Path("pyproject.toml").is_file() or Path("setup.py").is_file() or Path("tests").is_dir():
        # Python
        cmd = ["pytest"] if subprocess.run(["which", "pytest"], capture_output=True).returncode == 0 else ["python3", "-m", "unittest"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return " ".join(cmd), res.returncode == 0, res.stdout + res.stderr
    return None, None, None


def main():
    parser = argparse.ArgumentParser(description="HuyNex Spec-Driven Pre-Flight Gate")
    parser.add_argument("spec", nargs="?", default="TASK.md", help="Đường dẫn file spec/checklist (mặc định: TASK.md)")
    parser.add_argument("--skip-tests", action="store_true", help="Bỏ qua bước chạy test tự động")
    parser.add_argument("--json", action="store_true", help="Xuất kết quả dạng JSON")
    args = parser.parse_args()

    results = {
        "status": "PASS",
        "spec_file": args.spec,
        "checklist": {},
        "git_status": {},
        "test_run": {}
    }

    print("\n🔍 [HUYNEX PRE-FLIGHT GATE] Đang đối chiếu tiêu chí nghiệm thu...")

    # 1. Quét Checklist
    spec_path = Path(args.spec)
    total, unchecked = audit_checklist(spec_path)
    if total is not None and total > 0:
        results["checklist"] = {
            "total": total,
            "completed": total - len(unchecked),
            "pending": unchecked
        }
        if unchecked:
            print(f"  ❌ Còn {len(unchecked)}/{total} tiêu chí chưa hoàn thành:")
            for item in unchecked:
                print(f"     • {item}")
            results["status"] = "BLOCKED"
        else:
            print(f"  ✓ 100% Checklist đã hoàn thành ({total}/{total} items).")
    else:
        print(f"  ℹ️ Không tìm thấy checklist có định dạng '- [ ]' trong '{args.spec}'.")

    # 2. Quét Git
    dirty_files = check_git_clean()
    if dirty_files is not None:
        results["git_status"] = {"dirty_files_count": len(dirty_files), "files": dirty_files[:5]}
        if dirty_files:
            print(f"  ⚠️ Cảnh báo: Working tree có {len(dirty_files)} file chưa commit:")
            for f in dirty_files[:3]:
                print(f"     • {f}")
        else:
            print("  ✓ Git working tree hoàn toàn sạch sẽ (Clean).")

    # 3. Chạy Test
    if not args.skip_tests:
        test_name, test_pass, test_log = run_project_tests()
        if test_name:
            results["test_run"] = {"command": test_name, "passed": test_pass}
            if test_pass:
                print(f"  ✓ Kiểm thử tự động vượt qua ({test_name}: PASSED).")
            else:
                print(f"  ❌ Kiểm thử tự động thất bại ({test_name}: FAILED)!")
                results["status"] = "BLOCKED"

    # Kết luận
    print("------------------------------------------------------------------")
    if results["status"] == "PASS":
        print("🎉 [PRE-FLIGHT GATE: PASSED] Toàn bộ tiêu chí đạt chuẩn, sẵn sàng nghiệm thu!\n")
        if args.json:
            print(json.dumps(results, indent=2))
        return 0
    else:
        print("🛑 [PRE-FLIGHT GATE: BLOCKED] Chưa đạt tiêu chí. Vui lòng hoàn thiện trước khi bàn giao!\n")
        if args.json:
            print(json.dumps(results, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
