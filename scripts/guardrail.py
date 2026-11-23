#!/usr/bin/env python3
"""
HuyNex Security Guardrails V2 (scripts/guardrail.py)
---------------------------------------------------
Client-Side Deterministic PreToolUse Interceptor for AI Coding Agents.

Threat Model & Honest Scope:
- Intercepts and blocks high-risk destructive shell commands before execution.
- Scope: Application-level command parsing & validation (PreToolUse Hook).
- Note: This is a client-level defense-in-depth barrier. It is NOT an OS kernel
  sandbox (eBPF/seccomp). It works alongside Git remote branch protections.

Blocked Destructive Operations:
1. Git force push: 'git push --force', '-f', '+<ref>', '--force-with-lease'
2. Git hard reset: 'git reset --hard'
3. Git destructive clean: 'git clean -f', '-fd', '-fx'
4. Git force branch deletion: 'git branch -D'
5. Recursive root/workspace destruction: 'rm -rf' on '/', '~', '.', '*', or workspace root.
"""

import json
import os
import re
import shlex
import sys
from pathlib import Path


def get_workspace_root() -> Path:
    """Xác định thư mục gốc của workspace hiện tại một cách động."""
    cwd = Path.cwd().resolve()
    # Thử tìm root git
    cur = cwd
    while cur != cur.parent:
        if (cur / ".git").is_dir() or (cur / ".git").is_file():
            return cur
        cur = cur.parent
    return cwd


def split_compound_commands(cmd_str: str) -> list[str]:
    """Tách câu lệnh ghép (;, &&, ||, |) thành các lệnh con đơn lẻ."""
    # Tách theo toán tử shell cơ bản
    parts = re.split(r"\s*(?:&&|\|\||;|\|)\s*", cmd_str.strip())
    return [p.strip() for p in parts if p.strip()]


def evaluate_single_command(cmd_segment: str, workspace_root: Path) -> tuple[bool, str]:
    """Phân tích một lệnh đơn qua shlex. Trả về (is_blocked, reason)."""
    try:
        tokens = shlex.split(cmd_segment)
    except ValueError:
        # Nếu câu lệnh malformed không thể tokenize, kiểm tra fallback regex an toàn
        tokens = cmd_segment.split()

    if not tokens:
        return False, ""

    # Lấy tên nhị phân thực thi
    raw_bin = tokens[0]
    bin_name = Path(raw_bin).name.lower()

    # =========================================================================
    # 1. KIỂM DUYỆT CÁC LỆNH GIT HỦY DIỆT
    # =========================================================================
    if bin_name == "git":
        # Chuẩn hóa bỏ qua các cờ toàn cục của git (như -C <path>, -c <key=val>)
        idx = 1
        subcmd = None
        while idx < len(tokens):
            t = tokens[idx]
            if t in ("-C", "--work-tree", "--git-dir") and idx + 1 < len(tokens):
                idx += 2
                continue
            if t.startswith("-c") and idx < len(tokens):
                idx += 1
                continue
            if not t.startswith("-"):
                subcmd = t.lower()
                idx += 1
                break
            idx += 1

        args_after_subcmd = tokens[idx:] if idx <= len(tokens) else []

        if subcmd == "push":
            for arg in args_after_subcmd:
                if arg in ("--force", "-f", "--force-with-lease") or arg.startswith("+"):
                    return True, "Chặn đứng 'git push --force': Nguy cơ xóa đè lịch sử Git trên remote."

        elif subcmd == "reset":
            if any(arg == "--hard" or arg.startswith("--hard=") for arg in args_after_subcmd):
                return True, "Chặn đứng 'git reset --hard': Nguy cơ mất vĩnh viễn các thay đổi chưa lưu."

        elif subcmd == "clean":
            for arg in args_after_subcmd:
                if arg.startswith("-") and "f" in arg:
                    return True, "Chặn đứng 'git clean -f': Nguy cơ xóa hàng loạt file untracked chưa commit."

        elif subcmd == "branch":
            if any(arg in ("-D", "--delete-force") for arg in args_after_subcmd):
                return True, "Chặn đứng 'git branch -D': Cấm cưỡng chế xóa nhánh chưa merge."

    # =========================================================================
    # 2. KIỂM DUYỆT CÁC LỆNH XÓA ĐỆ QUY HỦY DIỆT (rm -rf / rmdir)
    # =========================================================================
    elif bin_name == "rm":
        has_recursive = any(t.startswith("-") and "r" in t.lower() for t in tokens[1:])
        has_force = any(t.startswith("-") and "f" in t.lower() for t in tokens[1:])

        if has_recursive and has_force:
            # Lấy danh sách targets không phải flags
            targets = [t for t in tokens[1:] if not t.startswith("-")]
            cwd = Path.cwd().resolve()
            home = Path.home().resolve()

            for target in targets:
                # 1. Các target gốc nguy hiểm hiển nhiên
                if target in ("/", "~", "$HOME", "%USERPROFILE%", ".", "*", ".."):
                    return True, f"Chốt chặn Single-Root Safety: Cấm xóa đệ quy trên thư mục gốc/hiện tại ('{target}')."

                # 2. Target phân giải thành thư mục gốc hoặc workspace root
                try:
                    resolved = Path(os.path.expanduser(os.path.expandvars(target))).resolve()
                    if resolved in (Path("/"), home, cwd, workspace_root):
                        return True, f"Chốt chặn Single-Root Safety: Thư mục mục tiêu ('{target}') trùng với thư mục gốc."
                except Exception:
                    pass

    # =========================================================================
    # 3. KIỂM DUYỆT CÁC LỆNH POWERSHELL HỦY DIỆT
    # =========================================================================
    elif bin_name in ("powershell", "pwsh"):
        for sub_token in tokens[1:]:
            if "remove-item" in sub_token.lower() and "-recurse" in sub_token.lower():
                return True, "Chặn đứng lệnh PowerShell: Remove-Item -Recurse trên thư mục trọng yếu."

    return False, ""


def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            sys.exit(0)
        data = json.loads(raw_input)
    except Exception:
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    workspace_root = get_workspace_root()
    sub_commands = split_compound_commands(command)

    for cmd in sub_commands:
        blocked, reason = evaluate_single_command(cmd, workspace_root)
        if blocked:
            sys.stderr.write(
                f"\n🛑 [HUYNEX GUARDRAIL BLOCKED]\n"
                f"Lý do: {reason}\n"
                f"Lệnh vi phạm: '{command}'\n"
                f"Mục tiêu: Bảo vệ an toàn dữ liệu và lịch sử Git.\n"
            )
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
