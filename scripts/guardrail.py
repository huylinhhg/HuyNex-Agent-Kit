#!/usr/bin/env python3
"""
ADOS Hard Guardrail Hook (PreToolUse for Claude Code & AI Agents)
Chốt chặn cứng ở mức hệ điều hành — Chặn đứng các lệnh hủy diệt trước khi thực thi.
"""
import json
import re
import sys

DANGEROUS_PATTERNS = [
    # Force push — nguy cơ xóa đè lịch sử repo
    (r"git\s+push\s+.*(--force|-f\b)", "Chặn đứng 'git push --force': Tuyệt đối không xóa đè lịch sử Git."),
    # Reset hard — nguy cơ mất code chưa commit
    (r"git\s+reset\s+--hard", "Chặn đứng 'git reset --hard': Nguy cơ mất vĩnh viễn code chưa lưu."),
    # Clean force — xóa file chưa track
    (r"git\s+clean\s+.*(-f|-fd|-df)", "Chặn đứng 'git clean -f': Nguy cơ xóa nhầm file untracked."),
    # Branch delete force
    (r"git\s+branch\s+.*-D\b", "Chặn đứng 'git branch -D': Cấm xóa nhánh bắt buộc."),
    # Xóa đệ quy gốc hoặc thư mục cha (Single-Root Safety)
    (r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-rf|-fr)\s+(/|~|\$HOME|\.\./|\.\.|/Users/maihuy/HuyNex\b|.*HuyNex/?$|.*0[0-9]_)", 
     "Chốt chặn Single-Root Safety: Nghiêm cấm lệnh 'rm -rf' trên thư mục gốc HuyNex hoặc thư mục cha."),
    # PowerShell equivalent destructive commands
    (r"(Remove-Item|rmdir|rd)\s+.*-Recurse.*(HuyNex|0[0-9]_)", 
     "Chốt chặn Single-Root Safety (PowerShell): Nghiêm cấm xóa đệ quy trên thư mục HuyNex/00-08.")
]

def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            sys.exit(0)
        data = json.loads(raw_input)
    except Exception:
        sys.exit(0)

    # Lấy câu lệnh terminal dự định chạy
    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    for pattern, warning in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            sys.stderr.write(f"\n🛑 [ADOS HARD GUARDRAIL BLOCKED]\n{warning}\nLệnh bị từ chối: '{command}'\n")
            sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
