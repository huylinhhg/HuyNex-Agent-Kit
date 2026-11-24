#!/usr/bin/env python3
"""
HuyNex Security Guardrails V3 (scripts/guardrail.py)
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
6. Subshell/Eval wrapping: 'eval', 'sh -c', 'bash -c', '$(...)', '`...`' containing above operations.
"""

import json
import os
import re
import shlex
import sys
from pathlib import Path

# Ensure UTF-8 output on all platforms (including Windows consoles)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def get_workspace_root() -> Path:
    """Xác định thư mục gốc của workspace hiện tại một cách động."""
    cwd = Path.cwd().resolve()
    cur = cwd
    while cur != cur.parent:
        if (cur / ".git").is_dir() or (cur / ".git").is_file():
            return cur
        cur = cur.parent
    return cwd


def split_compound_commands(cmd_str: str) -> list[str]:
    """Tách câu lệnh ghép (;, &&, ||, |) thành các lệnh con đơn lẻ có bảo toàn quote."""
    cmd_str = cmd_str.strip()
    if not cmd_str:
        return []

    try:
        lexer = shlex.shlex(cmd_str, posix=True, punctuation_chars=True)
        lexer.whitespace_split = False
        tokens = list(lexer)
    except Exception:
        # Fallback to regex split if string has unclosed quotes
        parts = re.split(r"\s*(?:&&|\|\||;|\|)\s*", cmd_str)
        return [p.strip() for p in parts if p.strip()]

    commands = []
    current = []
    for t in tokens:
        if t in ("&&", "||", ";", "|", "&"):
            if current:
                commands.append(" ".join(current))
                current = []
        else:
            if " " in t or "\t" in t:
                current.append(shlex.quote(t))
            else:
                current.append(t)

    if current:
        commands.append(" ".join(current))

    return [c.strip() for c in commands if c.strip()]


def extract_command_substitutions(cmd_str: str) -> list[str]:
    """Trích xuất các câu lệnh con bên trong $(...) hoặc `...`."""
    subs = re.findall(r"\$\((.*?)\)|`([^`]+)`", cmd_str)
    res = []
    for s in subs:
        inner = (s[0] or s[1]).strip()
        if inner:
            res.append(inner)
    return res


def evaluate_single_command(cmd_segment: str, workspace_root: Path, depth: int = 0) -> tuple[bool, str]:
    """Phân tích một lệnh đơn qua shlex. Hỗ trợ đệ quy eval, subshell và command substitutions."""
    if depth > 5:
        return False, ""

    try:
        tokens = shlex.split(cmd_segment)
    except ValueError:
        tokens = cmd_segment.split()

    if not tokens:
        return False, ""

    # Kiểm tra các command substitutions lồng nhau bên trong lệnh đơn
    nested_subs = extract_command_substitutions(cmd_segment)
    for sub_cmd in nested_subs:
        blocked, reason = evaluate_single_command(sub_cmd, workspace_root, depth + 1)
        if blocked:
            return True, f"Bên trong command substitution: {reason}"

    raw_bin = tokens[0]
    bin_name = Path(raw_bin).name.lower()

    # =========================================================================
    # 0. ĐỆ QUY GIẢI MÃ SUBSHELL / EVAL (eval, sh -c, bash -c, zsh -c)
    # =========================================================================
    if bin_name == "eval" and len(tokens) > 1:
        inner_cmd = " ".join(tokens[1:])
        blocked, reason = evaluate_single_command(inner_cmd, workspace_root, depth + 1)
        if blocked:
            return True, f"Bên trong eval: {reason}"

    elif bin_name in ("sh", "bash", "zsh") and "-c" in tokens:
        idx = tokens.index("-c")
        if idx + 1 < len(tokens):
            inner_cmd = tokens[idx + 1]
            sub_commands = split_compound_commands(inner_cmd)
            for sub in sub_commands:
                blocked, reason = evaluate_single_command(sub, workspace_root, depth + 1)
                if blocked:
                    return True, f"Bên trong {bin_name} -c: {reason}"

    # =========================================================================
    # 1. KIỂM DUYỆT CÁC LỆNH GIT HỦY DIỆT
    # =========================================================================
    if bin_name == "git":
        idx = 1
        subcmd = None
        while idx < len(tokens):
            t = tokens[idx]
            if t in ("-C", "--work-tree", "--git-dir") and idx + 1 < len(tokens):
                idx += 2
                continue
            if t.startswith("-C") and len(t) > 2:
                idx += 1
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
                arg_clean = arg.split("=")[0]
                if (
                    arg_clean in ("--force", "-f", "--force-with-lease")
                    or arg.startswith("+")
                    or arg.startswith("--force-with-lease=")
                ):
                    return True, "Chặn đứng 'git push --force': Nguy cơ xóa đè lịch sử Git trên remote."

        elif subcmd == "reset":
            for arg in args_after_subcmd:
                if arg == "--hard" or arg.startswith("--hard="):
                    return True, "Chặn đứng 'git reset --hard': Nguy cơ mất vĩnh viễn các thay đổi chưa lưu."

        elif subcmd == "clean":
            for arg in args_after_subcmd:
                if arg in ("--force", "-f") or (arg.startswith("-") and "f" in arg):
                    return True, "Chặn đứng 'git clean -f': Nguy cơ xóa hàng loạt file untracked chưa commit."

        elif subcmd == "branch":
            for arg in args_after_subcmd:
                arg_clean = arg.split("=")[0]
                if arg_clean in ("-D", "--delete-force") or arg.startswith("--delete-force="):
                    return True, "Chặn đứng 'git branch -D': Cấm cưỡng chế xóa nhánh chưa merge."

    # =========================================================================
    # 2. KIỂM DUYỆT CÁC LỆNH XÓA ĐỆ QUY HỦY DIỆT (rm -rf / rmdir)
    # =========================================================================
    elif bin_name == "rm":
        has_recursive = any(
            (t.startswith("-") and "r" in t.lower()) or t in ("--recursive", "-r", "-R")
            for t in tokens[1:]
        )
        has_force = any(
            (t.startswith("-") and "f" in t.lower()) or t in ("--force", "-f")
            for t in tokens[1:]
        )

        if has_recursive and has_force:
            targets = [t for t in tokens[1:] if not t.startswith("-")]
            cwd = Path.cwd().resolve()
            home = Path.home().resolve()

            for target in targets:
                if target in ("/", "~", "$HOME", "%USERPROFILE%", ".", "*", ".."):
                    return True, f"Chốt chặn Single-Root Safety: Cấm xóa đệ quy trên thư mục gốc/hiện tại ('{target}')."

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
        sub_str = " ".join(tokens[1:]).lower()
        if "remove-item" in sub_str and "-recurse" in sub_str:
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

    # 1. Trích xuất và kiểm tra tất cả command substitutions ($(cmd) hoặc `cmd`)
    nested_subs = extract_command_substitutions(command)
    for sub in nested_subs:
        blocked, reason = evaluate_single_command(sub, workspace_root)
        if blocked:
            sys.stderr.write(
                f"\n🛑 [HUYNEX GUARDRAIL BLOCKED]\n"
                f"Lý do: Bên trong command substitution: {reason}\n"
                f"Lệnh vi phạm: '{command}'\n"
                f"Mục tiêu: Bảo vệ an toàn dữ liệu và lịch sử Git.\n"
            )
            sys.exit(2)

    # 2. Phân tích các câu lệnh ghép
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
