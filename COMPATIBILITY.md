# Multi-Agent Compatibility Matrix

This matrix documents the verified integration state across supported AI Coding Agents.

---

## 📋 Compatibility Summary

| Agent Client | Skills Support | Rules Engine | Hook Enforcement | Verification Status |
|---|---|---|---|---|
| **Claude Code** | Native (`~/.claude/skills/`) | 9 Modular Rules (`~/.claude/rules/`) | Native `PreToolUse` (`guardrail.py`) | **RUNTIME_VERIFIED** (macOS, Linux & Windows) |
| **Google Antigravity** | Native (`~/.gemini/config/skills/`) | Root Instruction (`~/.gemini/GEMINI.md`) | Soft Prompt Governance & System Rules | **RUNTIME_VERIFIED** |
| **OpenAI Codex** | Native (`~/.codex/skills/`) | Root Instruction (`~/.codex/AGENTS.md`) | Soft Prompt Governance | **FORMAT_VERIFIED** |
| **Cursor** | Workspace (`.cursor/rules/`) | Native Rules (`.cursor/rules/*.mdc`) | Soft Prompt Governance | **FORMAT_VERIFIED** (YAML frontmatter + alwaysApply) |
| **Shared Agent Hub** | Native (`~/.agents/skills/`) | Universal (`~/.agents/rules/`) | Global fallback | **RUNTIME_VERIFIED** |

---

## 🔍 Detailed Notes by Client

### 1. Claude Code
- **Skills**: Fully recognized in `~/.claude/skills/<skill-name>/SKILL.md`.
- **Rules**: Claude Code automatically loads all `.md` files deployed to `~/.claude/rules/`.
- **Hooks**: Supports deterministic `PreToolUse` hooks in `~/.claude/settings.json`. Exit code `2` interrupts execution and displays the refusal reason to the model.

### 2. Google Antigravity
- **Skills**: Deployed to `~/.gemini/config/skills/`.
- **Rules**: Injected into `~/.gemini/GEMINI.md` within `<!-- HUYNEX_AGENT_KIT_START -->` block.

### 3. OpenAI Codex
- **Skills**: Deployed to `~/.codex/skills/`.
- **Rules**: Injected into `~/.codex/AGENTS.md`.

### 4. Cursor
- **Rules**: Deployed as official Cursor `.mdc` format into `~/.cursor/rules/*.mdc` (or workspace `.cursor/rules/`).
- **Format**: Each file includes YAML frontmatter with `globs: *` and `alwaysApply: true` to ensure active injection into Cursor's agent context.

### 5. Shared Agent Hub
- **Fallback Directory**: `~/.agents/skills/` and `~/.agents/rules/`. Serves as cross-client standard repository when multiple tools share common configurations.
