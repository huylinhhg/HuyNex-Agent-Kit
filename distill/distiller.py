#!/usr/bin/env python3
"""
Core distillation logic for terminal output, test suites, and git diffs.
Prioritizes high compression ratio (60-90%) with 100% error conservation.
"""
import re
from typing import List, Optional

# Regex for ANSI sequences (colors, cursor control, erase in display, OSC)
ANSI_PATTERN = re.compile(
    r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\([a-zA-Z]|\x1b\][^\x07\x1b]*(\x07|\x1b\\)|\x1b\[[0-9;]*m"
)
SPINNER_CHARS = set("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")


def strip_ansi_and_spinners(text: str) -> str:
    """Removes ANSI formatting, braille spinners, and handles \\r progress rewrites."""
    # Strip ANSI
    cleaned = ANSI_PATTERN.sub("", text)

    # Process carriage returns (\r) line by line (split by newline \n, not splitlines())
    processed_lines: List[str] = []
    for line in cleaned.split("\n"):
        if "\r" in line:
            # When progress bar overwrites on the same line, the last segment is the final state
            parts = [p for p in line.split("\r") if p]
            if parts:
                line = parts[-1]
            else:
                line = ""

        # Strip lone spinners at line start
        line_stripped = line.strip()
        if line_stripped and line_stripped[0] in SPINNER_CHARS:
            line = line.replace(line_stripped[0], "", 1).lstrip()

        processed_lines.append(line)

    return "\n".join(processed_lines)


def distill_test_output(text: str) -> str:
    """
    Distills test runner logs (vitest, jest, pytest, cargo test, playwright).
    Collapses successful tests into a compact summary, preserves 100% of errors/traces.
    """
    cleaned = strip_ansi_and_spinners(text)
    lines = cleaned.splitlines()

    passing_patterns = [
        re.compile(r"^\s*[✓√✔]\s+"),
        re.compile(r"^\s*PASS\s+"),
        re.compile(r"^\s*test\s+.*(?:\.\.\.\s*ok|\bpassed\b)"),
        re.compile(r"^\s*ok\s+\d+"),
    ]

    failing_patterns = [
        re.compile(r"^\s*(?:FAIL|FAILED|✕|✖)\s+"),
        re.compile(r"AssertionError"),
        re.compile(r"Error:"),
        re.compile(r"Exception:"),
        re.compile(r"^\s*at\s+"),
        re.compile(r"Expected:"),
        re.compile(r"Received:"),
        re.compile(r"Diff:"),
        re.compile(r"\bFAIL\b"),
    ]

    summary_patterns = [
        re.compile(r"Test Files\s+"),
        re.compile(r"Tests\s+"),
        re.compile(r"Duration\s+"),
        re.compile(r"test result:"),
        re.compile(r"passed,\s*failed"),
        re.compile(r"passed in"),
    ]

    kept_lines: List[str] = []
    passed_count = 0
    in_failure_block = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_failure_block:
                kept_lines.append(line)
            continue

        # Check if line indicates failure
        is_failure = any(p.search(line) for p in failing_patterns)
        if is_failure:
            in_failure_block = True
            kept_lines.append(line)
            continue

        # Check if line indicates stack trace or failure context
        if in_failure_block:
            # End failure block if we encounter a new passing test or final summary
            is_passing = any(p.search(line) for p in passing_patterns)
            is_summary = any(p.search(line) for p in summary_patterns)
            if is_passing:
                in_failure_block = False
                passed_count += 1
                continue
            elif is_summary:
                in_failure_block = False
                kept_lines.append(line)
                continue
            else:
                # Keep lines in the failure block (traces, source snippets)
                kept_lines.append(line)
                continue

        # Check if line is a passing test
        if any(p.search(line) for p in passing_patterns):
            passed_count += 1
            continue

        # Check if line is part of final test summary
        if any(p.search(line) for p in summary_patterns):
            kept_lines.append(line)
            continue

        # Keep other neutral lines if not excessively noisy
        if not re.search(r"npm (?:notice|warn)|found 0 vulnerabilities", line, re.IGNORECASE):
            kept_lines.append(line)

    result_parts: List[str] = []
    if passed_count > 0:
        result_parts.append(f"✓ [Collapsed] {passed_count} test items passed cleanly.")

    result_parts.extend(kept_lines)
    return "\n".join(result_parts)


def distill_git_diff(text: str) -> str:
    """
    Distills git diffs by collapsing large stretches of unchanged context lines (> 3 lines)
    while keeping 100% of headers, additions (+), and deletions (-).
    """
    cleaned = strip_ansi_and_spinners(text)
    lines = cleaned.splitlines()

    distilled_lines: List[str] = []
    unchanged_buffer: List[str] = []

    def flush_unchanged():
        nonlocal unchanged_buffer
        if not unchanged_buffer:
            return
        if len(unchanged_buffer) <= 3:
            distilled_lines.extend(unchanged_buffer)
        else:
            # Keep 1 before, 1 after, collapse the rest
            distilled_lines.append(unchanged_buffer[0])
            omitted = len(unchanged_buffer) - 2
            distilled_lines.append(f"  ... [{omitted} unchanged lines omitted]")
            distilled_lines.append(unchanged_buffer[-1])
        unchanged_buffer = []

    for line in lines:
        if line.startswith("diff --git") or line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
            flush_unchanged()
            distilled_lines.append(line)
        elif line.startswith("+") or line.startswith("-"):
            flush_unchanged()
            distilled_lines.append(line)
        elif line.startswith(" ") or line == "":
            unchanged_buffer.append(line)
        else:
            flush_unchanged()
            distilled_lines.append(line)

    flush_unchanged()
    return "\n".join(distilled_lines)


def distill_generic(text: str) -> str:
    """
    Generic distillation: removes duplicate lines, noisy package manager banners,
    and collapses multiple blank lines.
    """
    cleaned = strip_ansi_and_spinners(text)
    lines = cleaned.splitlines()

    NOISE_PATTERNS = [
        re.compile(r"^npm notice", re.IGNORECASE),
        re.compile(r"^\s*added \d+ packages", re.IGNORECASE),
        re.compile(r"^\s*found 0 vulnerabilities", re.IGNORECASE),
        re.compile(r"^\[notice\] A new release of pip is available", re.IGNORECASE),
        re.compile(r"^\s*to update run: pip install", re.IGNORECASE),
    ]

    filtered: List[str] = []
    last_line = None
    repeat_count = 1

    for line in lines:
        stripped = line.strip()

        # Skip noise patterns
        if any(p.search(stripped) for p in NOISE_PATTERNS):
            continue

        # Skip consecutive empty lines
        if not stripped:
            if filtered and filtered[-1] == "":
                continue
            filtered.append("")
            last_line = ""
            continue

        # Deduplicate identical consecutive lines
        if line == last_line:
            repeat_count += 1
            continue
        else:
            if repeat_count > 1 and filtered:
                filtered[-1] = f"{filtered[-1]} ... (repeated {repeat_count} times)"
            filtered.append(line)
            last_line = line
            repeat_count = 1

    if repeat_count > 1 and filtered:
        filtered[-1] = f"{filtered[-1]} ... (repeated {repeat_count} times)"

    return "\n".join(filtered)


def distill_stream(raw_text: str, cmd_hint: Optional[str] = None) -> str:
    """
    Intelligently routes raw terminal text to the optimal distillation handler.
    """
    hint = (cmd_hint or "").lower()

    if "diff" in hint or "diff --git" in raw_text:
        return distill_git_diff(raw_text)

    test_triggers = ["test", "vitest", "jest", "pytest", "cargo test", "playwright"]
    if any(t in hint for t in test_triggers) or "Test Files" in raw_text or "AssertionError" in raw_text:
        return distill_test_output(raw_text)

    return distill_generic(raw_text)
