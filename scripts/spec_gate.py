#!/usr/bin/env python3
"""
HuyNex Spec-Driven Pre-Flight Gate V3 (scripts/spec_gate.py)
----------------------------------------------------------
Evidence-Based Pre-Flight Verification Gate for AI Agent Tasks.

Fail-Closed Philosophy:
- Never declare 'PASS' simply because checks were missing or skipped.
- Pure JSON output for automation/CI pipelines when '--json' is specified.
- Verifies:
  1. Spec existence and checklist completion (- [ ] vs - [x]). Spec with 0 items fails closed.
  2. Deliverables existence on disk.
  3. Git working tree cleanliness with error escalation (--require-clean-git).
  4. Automated project test suite execution.
  5. Clear separation between PASS, NOT_VERIFIED, and BLOCKED.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 output on all platforms (including Windows consoles)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def audit_checklist(file_path: Path) -> tuple[int, list[str]]:
    """Quét các mục checklist trong file spec. Trả về (total, unchecked_items)."""
    if not file_path.is_file():
        return 0, []
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    total = re.findall(r"-\s*\[([ xX])\]\s*(.+)", text)
    if not total:
        return 0, []
    unchecked = [desc.strip() for status, desc in total if status.lower() != "x"]
    return len(total), unchecked


def audit_deliverables(file_path: Path) -> tuple[list[str], list[str]]:
    """Trích xuất và kiểm tra sự tồn tại của các tệp bàn giao (Deliverables) được nêu trong spec."""
    if not file_path.is_file():
        return [], []
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    candidates = re.findall(r"`([a-zA-Z0-9_\-\./\\]+\.[a-zA-Z0-9]+)`", text)
    existing = []
    missing = []
    for cand in set(candidates):
        p = Path(cand)
        if p.is_file():
            existing.append(cand)
        elif "/" in cand or "\\" in cand:
            missing.append(cand)
    return existing, missing


def check_git_clean() -> tuple[list[str], str | None]:
    """Kiểm tra working tree git có sạch sẽ không. Trả về (dirty_files, error_msg)."""
    try:
        res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        return lines, None
    except Exception as e:
        return [], f"Git command failed: {e}"


def run_project_tests() -> tuple[str | None, bool, str]:
    """Tự động phát hiện và chạy test dự án."""
    if Path("package.json").is_file():
        try:
            pkg = json.loads(Path("package.json").read_text())
            if "test" in pkg.get("scripts", {}):
                res = subprocess.run(["npm", "test"], capture_output=True, text=True)
                return "npm test", res.returncode == 0, res.stdout + res.stderr
        except Exception:
            pass
    elif Path("Cargo.toml").is_file():
        res = subprocess.run(["cargo", "test"], capture_output=True, text=True)
        return "cargo test", res.returncode == 0, res.stdout + res.stderr
    elif Path("pyproject.toml").is_file() or Path("setup.py").is_file() or Path("tests").is_dir():
        cmd = ["pytest"] if subprocess.run(["which", "pytest"], capture_output=True).returncode == 0 else ["python3", "-m", "unittest"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return " ".join(cmd), res.returncode == 0, res.stdout + res.stderr
    return None, False, ""


def main():
    parser = argparse.ArgumentParser(description="HuyNex Spec-Driven Pre-Flight Gate V3")
    parser.add_argument("spec", nargs="?", default="TASK.md", help="Đường dẫn file spec (mặc định: TASK.md)")
    parser.add_argument("--skip-tests", action="store_true", help="Bỏ qua bước chạy test tự động")
    parser.add_argument("--require-clean-git", action="store_true", help="Bắt buộc Git working tree phải sạch sẽ mới PASS")
    parser.add_argument("--allow-unverified", action="store_true", help="Cho phép thoát với exit 0 nhưng đánh dấu NOT_VERIFIED khi thiếu bằng chứng")
    parser.add_argument("--json", action="store_true", help="Chỉ xuất kết quả JSON thuần (Machine-readable) ra stdout")
    args = parser.parse_args()

    results = {
        "status": "PASS",
        "spec_file": args.spec,
        "spec_found": False,
        "checklist": {"total": 0, "completed": 0, "pending": []},
        "deliverables": {"existing": [], "missing": []},
        "git_status": {"dirty_count": 0, "dirty_files": []},
        "test_run": {"command": None, "executed": False, "passed": False},
        "blocking_reasons": []
    }

    log_messages = []

    def log(msg: str):
        if not args.json:
            print(msg)
        else:
            log_messages.append(msg)

    log("\n🔍 [HUYNEX PRE-FLIGHT GATE V3] Đang đối chiếu tiêu chí nghiệm thu...")

    # 1. Quét Spec & Checklist
    spec_path = Path(args.spec)
    if spec_path.is_file():
        results["spec_found"] = True
        total, unchecked = audit_checklist(spec_path)
        results["checklist"] = {
            "total": total,
            "completed": total - len(unchecked),
            "pending": unchecked
        }
        if total > 0:
            if unchecked:
                log(f"  ❌ Còn {len(unchecked)}/{total} mục checklist chưa hoàn thành:")
                for item in unchecked:
                    log(f"     • {item}")
                results["blocking_reasons"].append(f"{len(unchecked)} pending checklist items")
            else:
                log(f"  ✓ 100% Checklist đã hoàn thành ({total}/{total} items).")
        else:
            log(f"  ❌ File '{args.spec}' tồn tại nhưng KHÔNG có mục checklist nào (- [ ]).")
            # Fail-closed: File spec rỗng không được coi là đạt
            results["blocking_reasons"].append(f"Spec file '{args.spec}' contains 0 checklist items")

        # 2. Quét Deliverables
        existing_deliv, missing_deliv = audit_deliverables(spec_path)
        results["deliverables"] = {"existing": existing_deliv, "missing": missing_deliv}
        if missing_deliv:
            log(f"  ❌ Phát hiện {len(missing_deliv)} tệp bàn giao được nêu trong spec nhưng không tồn tại trên đĩa:")
            for m in missing_deliv:
                log(f"     • {m}")
            results["blocking_reasons"].append(f"{len(missing_deliv)} missing deliverables on disk")
        elif existing_deliv:
            log(f"  ✓ Đã xác minh {len(existing_deliv)} tệp bàn giao thực tế tồn tại trên đĩa.")
    else:
        log(f"  ⚠️ Không tìm thấy file spec '{args.spec}'.")
        results["blocking_reasons"].append(f"Spec file '{args.spec}' not found")

    # 3. Quét Git Cleanliness
    dirty_files, git_err = check_git_clean()
    if git_err:
        log(f"  ⚠️ Lỗi khi kiểm tra Git status: {git_err}")
        results["git_status"] = {"error": git_err, "dirty_count": -1}
        if args.require_clean_git:
            results["blocking_reasons"].append(f"Git status failed to verify: {git_err}")
    else:
        results["git_status"] = {"dirty_count": len(dirty_files), "dirty_files": dirty_files[:10]}
        if dirty_files:
            log(f"  ⚠️ Cảnh báo: Git working tree có {len(dirty_files)} tệp chưa commit.")
            if args.require_clean_git:
                results["blocking_reasons"].append("Git working tree is dirty (--require-clean-git enforced)")
        else:
            log("  ✓ Git working tree hoàn toàn sạch sẽ (Clean).")

    # 4. Chạy Test Dự Án
    if not args.skip_tests:
        test_name, test_pass, test_log = run_project_tests()
        if test_name:
            results["test_run"] = {"command": test_name, "executed": True, "passed": test_pass}
            if test_pass:
                log(f"  ✓ Kiểm thử tự động vượt qua ({test_name}: PASSED).")
            else:
                log(f"  ❌ Kiểm thử tự động thất bại ({test_name}: FAILED)!")
                results["blocking_reasons"].append(f"Test suite '{test_name}' failed")
        else:
            log("  ℹ️ Không phát hiện bộ test tự động nào trong thư mục.")

    # Phán quyết Fail-Closed & Phân biệt rõ ràng PASS vs NOT_VERIFIED vs BLOCKED
    if results["blocking_reasons"]:
        if args.allow_unverified:
            results["status"] = "NOT_VERIFIED"
            exit_code = 0
        else:
            results["status"] = "BLOCKED"
            exit_code = 1
    elif not results["spec_found"] and not results["test_run"]["executed"]:
        results["status"] = "NOT_VERIFIED"
        if args.allow_unverified:
            exit_code = 0
        else:
            results["blocking_reasons"].append("Zero evidence found (no spec checklist, no automated tests)")
            results["status"] = "BLOCKED"
            exit_code = 1
    else:
        results["status"] = "PASS"
        exit_code = 0

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        log("------------------------------------------------------------------")
        if results["status"] == "PASS":
            log("🎉 [PRE-FLIGHT GATE: PASSED] Toàn bộ tiêu chí đạt chuẩn, sẵn sàng nghiệm thu!\n")
        elif results["status"] == "NOT_VERIFIED":
            log("⚠️ [PRE-FLIGHT GATE: NOT_VERIFIED] Chưa đủ bằng chứng khách quan (chạy với --allow-unverified).\n")
        else:
            log(f"🛑 [PRE-FLIGHT GATE: BLOCKED] Lỗi: {'; '.join(results['blocking_reasons'])}\n")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
