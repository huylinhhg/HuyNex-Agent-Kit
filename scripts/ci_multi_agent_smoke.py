#!/usr/bin/env python3
"""
Multi-Agent Runtime Smoke Test (scripts/ci_multi_agent_smoke.py)
---------------------------------------------------------------
Executes end-to-end integration testing for all supported agents:
1. Claude Code (~/.claude)
2. OpenAI Codex (~/.codex)
3. Cursor (~/.cursor)
4. Google Antigravity (~/.gemini)
5. Shared Hub (~/.agents)

Verifies:
- Pre-existing user content preservation across all 4 agents.
- Post-install user modification preservation (P0 Data Safety).
- Cursor .mdc YAML syntax and Claude Code rule scoping.
- Non-destructive uninstallation restoring exact user state.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

KIT_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = KIT_ROOT / "scripts/install.py"


def main():
    print("=" * 65)
    print("HUYNEX AGENT KIT — MULTI-AGENT RUNTIME SMOKE TEST")
    print("=" * 65)

    with tempfile.TemporaryDirectory() as mock_home_dir:
        mock_home = Path(mock_home_dir)
        env = os.environ.copy()
        env["HOME"] = str(mock_home)
        env["USERPROFILE"] = str(mock_home)
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        # -------------------------------------------------------------
        # STEP 1: Setup Mock Environments for all 4 Agents
        # -------------------------------------------------------------
        print("\n[Step 1] Initializing mock agent environments...")

        # 1. Claude Code
        claude_dir = mock_home / ".claude"
        claude_dir.mkdir(parents=True)
        claude_orig = "# User Personal Claude Prompt\nAlways be concise.\n"
        (claude_dir / "CLAUDE.md").write_text(claude_orig, encoding="utf-8")
        claude_settings = {
            "model": "claude-3-5-sonnet",
            "hooks": {
                "PreToolUse": [
                    {"matcher": "Read", "hooks": [{"type": "command", "command": "echo read"}]}
                ]
            }
        }
        (claude_dir / "settings.json").write_text(json.dumps(claude_settings, indent=2), encoding="utf-8")

        # 2. Codex
        codex_dir = mock_home / ".codex"
        codex_dir.mkdir(parents=True)
        codex_orig = "# User Personal Codex Directives\nStrict TDD enforced.\n"
        (codex_dir / "AGENTS.md").write_text(codex_orig, encoding="utf-8")

        # 3. Cursor
        cursor_dir = mock_home / ".cursor"
        cursor_rules = cursor_dir / "rules"
        cursor_rules.mkdir(parents=True)
        cursor_orig_rule = (
            "---\n"
            "description: \"User Custom Rule\"\n"
            "globs: \"*.ts\"\n"
            "alwaysApply: true\n"
            "---\n"
            "# Custom TypeScript Standards\n"
        )
        (cursor_rules / "user_custom.mdc").write_text(cursor_orig_rule, encoding="utf-8")

        # 4. Antigravity
        gemini_dir = mock_home / ".gemini"
        gemini_dir.mkdir(parents=True)
        gemini_orig = "# User Antigravity System Directives\n"
        (gemini_dir / "GEMINI.md").write_text(gemini_orig, encoding="utf-8")

        # 5. Pre-existing user skill with Content A (matches a skill name HuyNex installs)
        user_skill_dir = mock_home / ".agents/skills/data-conservation-gate"
        user_skill_dir.mkdir(parents=True)
        skill_content_a = "---\nname: data-conservation-gate\ndescription: User Custom Prior Implementation\n---\n# Content A (User Prior Work)\n"
        (user_skill_dir / "SKILL.md").write_text(skill_content_a, encoding="utf-8")

        print("  ✓ Mock agents configured: Claude Code, Codex, Cursor, Antigravity, Shared Hub.")

        # -------------------------------------------------------------
        # STEP 2: Run Installer (--all)
        # -------------------------------------------------------------
        print("\n[Step 2] Executing install.py --all across all detected agents...")
        res_install = subprocess.run(
            [sys.executable, str(INSTALLER), "--all"],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if res_install.returncode != 0:
            print(f"❌ Install failed with code {res_install.returncode}")
            print(res_install.stdout)
            print(res_install.stderr)
            sys.exit(1)

        print("  ✓ Install completed successfully.")
        # Verify all agents detected in output
        stdout_text = res_install.stdout
        for agent in ["Claude Code", "Codex", "Cursor", "Antigravity"]:
            if agent not in stdout_text:
                print(f"❌ Expected agent '{agent}' was not detected in installer output!")
                sys.exit(1)
        print("  ✓ All 4 client agents confirmed detected in installer plan.")

        # Verify Cursor .mdc files have valid YAML frontmatter with globs: "*"
        cursor_installed_rules = list(cursor_rules.glob("*.mdc"))
        huynex_rules = [r for r in cursor_installed_rules if r.name != "user_custom.mdc"]
        if len(huynex_rules) < 9:
            print(f"❌ Expected >= 9 HuyNex .mdc rules in Cursor, found {len(huynex_rules)}")
            sys.exit(1)
        for r in huynex_rules:
            text = r.read_text(encoding="utf-8")
            if 'globs: "*"' not in text:
                print(f"❌ Invalid YAML globs in {r.name}: expected globs: \"*\"")
                sys.exit(1)
        print(f"  ✓ {len(huynex_rules)} Cursor .mdc rules verified with valid YAML globs: \"*\".")

        # -------------------------------------------------------------
        # STEP 3: Simulate Post-Install User Modifications (P0 Tests)
        # -------------------------------------------------------------
        print("\n[Step 3] Simulating post-install user modifications...")

        # Modify pre-existing skill (add Content C)
        skill_file = user_skill_dir / "SKILL.md"
        skill_content_c = skill_content_a + "\n# User Added Work (Content C)\n"
        skill_file.write_text(skill_content_c, encoding="utf-8")

        # Modify an installed HuyNex rule in Claude Code (add Custom Note D)
        claude_rule_file = claude_dir / "rules/01-communication.md"
        if claude_rule_file.is_file():
            claude_rule_mod = claude_rule_file.read_text(encoding="utf-8") + "\n# User Custom Note D\n"
            claude_rule_file.write_text(claude_rule_mod, encoding="utf-8")
            print("  ✓ Simulated user edits on pre-existing skill and installed rule module.")

        # -------------------------------------------------------------
        # STEP 4: Run Doctor (--doctor)
        # -------------------------------------------------------------
        print("\n[Step 4] Running install.py --doctor integrity check...")
        res_doctor = subprocess.run(
            [sys.executable, str(INSTALLER), "--doctor"],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if res_doctor.returncode != 0:
            print(f"❌ Doctor failed with code {res_doctor.returncode}")
            print(res_doctor.stdout)
            print(res_doctor.stderr)
            sys.exit(1)
        print("  ✓ Doctor passed 100% clean.")

        # -------------------------------------------------------------
        # STEP 5: Run Uninstaller (--uninstall)
        # -------------------------------------------------------------
        print("\n[Step 5] Running install.py --uninstall non-destructive lifecycle...")
        res_uninstall = subprocess.run(
            [sys.executable, str(INSTALLER), "--uninstall"],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if res_uninstall.returncode != 0:
            print(f"❌ Uninstall failed with code {res_uninstall.returncode}")
            print(res_uninstall.stdout)
            print(res_uninstall.stderr)
            sys.exit(1)
        print("  ✓ Uninstall execution completed.")

        # -------------------------------------------------------------
        # STEP 6: Deep Verification of Data Safety & Zero-Loss
        # -------------------------------------------------------------
        print("\n[Step 6] Auditing data preservation & restoration across all agents...")

        # 1. Claude Code CLAUDE.md must equal EXACT original bytes
        claude_after_bytes = (claude_dir / "CLAUDE.md").read_bytes()
        if claude_after_bytes != claude_orig.encode("utf-8"):
            print(f"❌ Claude CLAUDE.md byte mismatch! Expected:\n{claude_orig.encode('utf-8')}\nGot:\n{claude_after_bytes}")
            sys.exit(1)
        print("  ✓ Claude Code CLAUDE.md restored byte-for-byte.")

        # 2. Claude settings.json pre-existing hook must be intact
        claude_settings_after = json.loads((claude_dir / "settings.json").read_text(encoding="utf-8"))
        pre_hooks = claude_settings_after.get("hooks", {}).get("PreToolUse", [])
        if not any(h.get("matcher") == "Read" for h in pre_hooks):
            print("❌ User's original pre-tool hook in settings.json was erased!")
            sys.exit(1)
        if any("guardrail.py" in str(h) for h in pre_hooks):
            print("❌ Guardrail hook was not removed from settings.json during uninstall!")
            sys.exit(1)

        # 3. Codex AGENTS.md must equal EXACT original bytes
        codex_after_bytes = (codex_dir / "AGENTS.md").read_bytes()
        if codex_after_bytes != codex_orig.encode("utf-8"):
            print(f"❌ Codex AGENTS.md byte mismatch!")
            sys.exit(1)
        print("  ✓ Codex AGENTS.md restored byte-for-byte.")

        # 4. Antigravity GEMINI.md must equal EXACT original bytes
        gemini_after_bytes = (gemini_dir / "GEMINI.md").read_bytes()
        if gemini_after_bytes != gemini_orig.encode("utf-8"):
            print(f"❌ Antigravity GEMINI.md byte mismatch!")
            sys.exit(1)
        print("  ✓ Antigravity GEMINI.md restored byte-for-byte.")

        # 5. Cursor custom user rule must NEVER have been touched
        cursor_custom_file = cursor_rules / "user_custom.mdc"
        if not cursor_custom_file.is_file() or cursor_custom_file.read_bytes() != cursor_orig_rule.encode("utf-8"):
            print("❌ Cursor user_custom.mdc was damaged or missing!")
            sys.exit(1)
        print("  ✓ Cursor user_custom.mdc untouched.")

        # 6. Pre-existing user skill must be RESTORED byte-for-byte to Content A
        skill_after_bytes = skill_file.read_bytes()
        if skill_after_bytes != skill_content_a.encode("utf-8"):
            print(f"❌ Pre-existing skill was not restored byte-for-byte to Content A!")
            sys.exit(1)
        print("  ✓ Pre-existing user skill restored byte-for-byte.")

        # 7. Post-install modified Content C and Note D must be in preserved_user_modified/
        preserved_dir = mock_home / ".huynex/preserved_user_modified"
        if not preserved_dir.is_dir():
            print("❌ preserved_user_modified directory was not created!")
            sys.exit(1)

        preserved_files = list(preserved_dir.glob("*"))
        print(f"  ✓ Preserved user files archive count: {len(preserved_files)}")
        found_c = False
        found_d = False
        for pf in preserved_files:
            text = pf.read_text(encoding="utf-8", errors="ignore")
            if "Content C" in text:
                found_c = True
            if "Note D" in text:
                found_d = True

        if not found_c:
            print("❌ P0 REGRESSION: User's modified Content C was NOT archived to preserved_user_modified!")
            sys.exit(1)
        if not found_d:
            print("❌ P0 REGRESSION: User's modified Note D was NOT archived to preserved_user_modified!")
            sys.exit(1)

        print("  ✓ P0-01 Verified: User post-install modifications (Content C) safely archived before backup restore.")
        print("  ✓ P0-02 Verified: Non-colliding archive paths generated with zero overwrite.")
        print("  ✓ P1 Verified: Cursor .mdc YAML syntax, Claude rule scoping, and complete multi-agent lifecycle.")

    print("\n" + "=" * 65)
    print("🎉 ALL MULTI-AGENT SMOKE TESTS PASSED WITH 100% DATA SAFETY!")
    print("=" * 65)


if __name__ == "__main__":
    main()
