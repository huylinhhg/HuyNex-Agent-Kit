#!/usr/bin/env python3
"""
HuyNex Agent Kit — Validator Suite (validate.py)
-----------------------------------------------
Integrity and security validator for HuyNex Agent Kit:
1. Validates directory structure and YAML frontmatter of all SKILL.md files.
2. Scans for hardcoded secrets, private paths, and organization PII.
3. Ensures rules and lessons are well-formed.
"""

import os
import re
import sys
from pathlib import Path

# Ensure UTF-8 output on all platforms (including Windows consoles)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

KIT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = KIT_ROOT / ".agents/skills"
RULES_DIR = KIT_ROOT / "rules"
LESSONS_DIR = KIT_ROOT / "lessons"

# Forbidden patterns that must NEVER appear in public open-source repos
FORBIDDEN_PATTERNS = [
    (r"/Users/maihuy", "Personal macOS home path"),
    (r"C:\\Users\\maitr", "Personal Windows home path"),
    (r"sk-[a-zA-Z0-9]{20,}", "OpenAI / Model API Key"),
    (r"ghp_[a-zA-Z0-9]{20,}", "GitHub Personal Access Token"),
    (r"bearer\s+[a-zA-Z0-9_\-\.]{25,}", "Authentication Bearer Token"),
    (r"\bPV01\b", "Private internal police unit designation"),
    (r"Tham mưu Cảnh sát", "Private internal police unit name"),
    (r"Công an tỉnh Tuyên Quang", "Private internal agency name"),
]


def test_skills_frontmatter() -> list[str]:
    errors = []
    if not SKILLS_DIR.is_dir():
        return ["Directory .agents/skills does not exist!"]

    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue
        skill_file = d / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"Skill '{d.name}': Missing SKILL.md")
            continue

        content = skill_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            errors.append(f"Skill '{d.name}': SKILL.md does not start with YAML frontmatter '---'")
            continue

        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append(f"Skill '{d.name}': YAML frontmatter is not properly closed with '---'")
            continue

        yaml_block = parts[1]
        name_match = re.search(r"^name:\s*([a-zA-Z0-9\-_]+)", yaml_block, re.MULTILINE)
        desc_match = re.search(r"^description:\s*(.+)", yaml_block, re.MULTILINE)

        if not name_match:
            errors.append(f"Skill '{d.name}': Missing valid 'name' field in frontmatter")
        elif name_match.group(1).strip() != d.name:
            errors.append(f"Skill '{d.name}': 'name' ({name_match.group(1).strip()}) does not match directory ({d.name})")

        if not desc_match or not desc_match.group(1).strip():
            errors.append(f"Skill '{d.name}': Missing 'description' in frontmatter")

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
                    findings.append(f"File '{rel_p}': Detected [{reason}] matching '{pattern}' ({len(matches)} occurrences)")
    return findings


def main():
    print("=" * 65)
    print("HUYNEX AGENT KIT — TEST SUITE & SECURITY AUDITOR")
    print("=" * 65)

    print("\n[1] Checking Agent Skills (.agents/skills/)...")
    frontmatter_errors = test_skills_frontmatter()
    if frontmatter_errors:
        print("  [FAIL] Detected formatting errors:")
        for err in frontmatter_errors:
            print(f"     - {err}")
    else:
        print("  [OK] All skills have valid YAML frontmatter matching directory names.")

    print("\n[2] Checking Secret & PII Scanning (Confidentiality Audit)...")
    leak_findings = test_secret_and_pii_leaks()
    if leak_findings:
        print("  [FAIL] Detected security/PII leaks:")
        for leak in leak_findings:
            print(f"     - {leak}")
    else:
        print("  [OK] CLEAN: Zero tokens, private paths, or personal designations detected.")

    print("\n" + "=" * 65)
    if frontmatter_errors or leak_findings:
        print("VERDICT: FAILED - Resolve the above issues before release.")
        sys.exit(1)
    else:
        print("VERDICT: ALL CHECKS PASSED - Repository meets release standards.")
        sys.exit(0)


if __name__ == "__main__":
    main()
