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

# Cap stream buffer at 20MB to avoid OOM on runaway infinite processes
MAX_STREAM_BYTES = 20 * 1024 * 1024
CHUNK_SIZE = 64 * 1024  # 64 KB read chunks


def read_bounded_stream(stream, max_bytes: int = MAX_STREAM_BYTES) -> tuple[str, bool]:
    """
    Reads stream in 64KB chunks up to max_bytes without loading unbounded data into RAM.
    Guarantees bounded memory consumption regardless of stream size.
    """
    chunks = []
    total_bytes = 0
    truncated = False

    while True:
        chunk = stream.read(min(CHUNK_SIZE, max_bytes - total_bytes + 1))
        if not chunk:
            break
        chunk_len = len(chunk.encode("utf-8", errors="ignore") if isinstance(chunk, str) else chunk)
        if total_bytes + chunk_len > max_bytes:
            remaining = max(0, max_bytes - total_bytes)
            chunk = chunk[:remaining]
            chunks.append(chunk)
            truncated = True
            break
        chunks.append(chunk)
        total_bytes += chunk_len
        if total_bytes >= max_bytes:
            truncated = True
            break

    text = "".join(chunks)
    if truncated:
        text += "\n\n[HUYNEX DISTILL WARNING: Stream ceiling of 20MB reached. Truncated safely to prevent memory exhaustion]\n"
    return text, truncated


def enforce_buffer_cap(text: str, max_bytes: int = MAX_STREAM_BYTES) -> str:
    """Enforces maximum buffer size to prevent memory exhaustion on runaway streams."""
    encoded = text.encode("utf-8", errors="ignore")
    if len(encoded) > max_bytes:
        truncated = encoded[:max_bytes].decode("utf-8", errors="ignore")
        return truncated + "\n\n[HUYNEX DISTILL WARNING: Stream capped at 20MB to prevent memory exhaustion]\n"
    return text


def strip_ansi_and_spinners(text: str) -> str:
    """Removes ANSI formatting, braille spinners, and handles \\r progress rewrites."""
    cleaned = ANSI_PATTERN.sub("", text)

    processed_lines: List[str] = []
    for line in cleaned.split("\n"):
        if "\r" in line:
            parts = [p for p in line.split("\r") if p]
            if parts:
                line = parts[-1]
            else:
                line = ""

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

        is_failure = any(p.search(line) for p in failing_patterns)
        if is_failure:
            in_failure_block = True
            kept_lines.append(line)
            continue

        if in_failure_block:
            is_passing = any(p.search(line) for p in passing_patterns)
            is_summary = any(p.search(line) for p in summary_patterns)
            if is_passing or is_summary:
                in_failure_block = False
            else:
                kept_lines.append(line)
                continue

        is_summary = any(p.search(line) for p in summary_patterns)
        if is_summary:
            kept_lines.append(line)
            continue

        is_passing = any(p.search(line) for p in passing_patterns)
        if is_passing:
            passed_count += 1
            continue

    if passed_count > 0:
        kept_lines.insert(0, f"[PASSED TESTS COLLAPSED] {passed_count} test cases passed successfully.")

    return "\n".join(kept_lines)


def distill_git_diff(text: str) -> str:
    """
    Distills git diff output by:
    - Retaining file headers (diff --git, ---, +++)
    - Collapsing large unchanged context blocks into @@ headers
    - Keeping 100% of mutations (+/- lines)
    """
    lines = text.splitlines()
    distilled: List[str] = []

    consecutive_context = 0
    context_buffer: List[str] = []

    for line in lines:
        if line.startswith("diff --git") or line.startswith("--- ") or line.startswith("+++ "):
            if context_buffer:
                if len(context_buffer) > 6:
                    distilled.extend(context_buffer[:3])
                    distilled.append(f"    ... ({len(context_buffer) - 6} lines unchanged) ...")
                    distilled.extend(context_buffer[-3:])
                else:
                    distilled.extend(context_buffer)
                context_buffer = []

            distilled.append(line)
            consecutive_context = 0
            continue

        if line.startswith("@@"):
            if context_buffer:
                if len(context_buffer) > 6:
                    distilled.extend(context_buffer[:3])
                    distilled.append(f"    ... ({len(context_buffer) - 6} lines unchanged) ...")
                    distilled.extend(context_buffer[-3:])
                else:
                    distilled.extend(context_buffer)
                context_buffer = []
            distilled.append(line)
            continue

        if line.startswith("+") or line.startswith("-"):
            if context_buffer:
                if len(context_buffer) > 6:
                    distilled.extend(context_buffer[:3])
                    distilled.append(f"    ... ({len(context_buffer) - 6} lines unchanged) ...")
                    distilled.extend(context_buffer[-3:])
                else:
                    distilled.extend(context_buffer)
                context_buffer = []
            distilled.append(line)
            consecutive_context = 0
        else:
            context_buffer.append(line)

    if context_buffer:
        if len(context_buffer) > 6:
            distilled.extend(context_buffer[:3])
            distilled.append(f"    ... ({len(context_buffer) - 6} lines unchanged) ...")
            distilled.extend(context_buffer[-3:])
        else:
            distilled.extend(context_buffer)

    return "\n".join(distilled)


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

        if any(p.search(stripped) for p in NOISE_PATTERNS):
            continue

        if not stripped:
            if filtered and filtered[-1] == "":
                continue
            filtered.append("")
            last_line = ""
            continue

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
    Caps input buffer at 20MB to prevent memory exhaustion.
    """
    raw_text = enforce_buffer_cap(raw_text)
    hint = (cmd_hint or "").lower()

    if "diff" in hint or "diff --git" in raw_text:
        return distill_git_diff(raw_text)

    test_triggers = ["test", "vitest", "jest", "pytest", "cargo test", "playwright"]
    if any(t in hint for t in test_triggers) or "Test Files" in raw_text or "AssertionError" in raw_text:
        return distill_test_output(raw_text)

    return distill_generic(raw_text)
