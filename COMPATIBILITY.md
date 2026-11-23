# Multi-Agent Compatibility Matrix

This matrix documents the verified integration state across supported AI Coding Agents.

---

## 📋 Compatibility Summary

| Agent Client | Skills Support | Rules Engine | Hook Enforcement | Verification Status |
|---|---|---|---|---|
| **Claude Code** | Native (`~/.claude/skills/`) | 9 Modular Rules (`@import` & `~/.claude/rules/`) | Native `PreToolUse` (`guardrail.py`) | **RUNTIME_VERIFIED** (macOS & Windows) |
| **OpenAI Codex** | Native (`~/.codex/skills/`) | Root Instruction (`~/.codex/AGENTS.md`) | Soft Prompt Governance | **CONFIG_VERIFIED** |
| **Google Antigravity** | Native (`~/.gemini/config/skills/`) | Root Instruction (`~/.gemini/GEMINI.md`) | Soft Prompt Governance & System Rules | **RUNTIME_VERIFIED** |
| **Cursor** | Workspace (`.cursor/rules/`) | Directory Rules (`.cursor/rules/*.mdc`) | Soft Prompt Governance | **CONFIG_VERIFIED** |
| **Shared Agent Hub** | Native (`~/.agents/skills/`) | Universal (`~/.agents/rules/`) | Global fallback | **RUNTIME_VERIFIED** |

---

## 🔍 Detailed Notes by Client

### 1. Claude Code
- **Skills**: Fully recognized in `~/.claude/skills/<skill-name>/SKILL.md`.
- **Rules**: Supports `@import` syntax in `CLAUDE.md`. When configured, Claude Code discovers `.md` rule modules.
- **Hooks**: Supports `PreToolUse` hooks in `~/.claude/settings.json`. Exit code `2` interrupts execution and displays the refusal reason to the model.

### 2. Google Antigravity
- **Skills**: Placed in `~/.gemini/config/skills/`.
- **Rules**: Injected into `~/.gemini/GEMINI.md` within `<!-- HUYNEX_AGENT_KIT_START -->` block.

### 3. OpenAI Codex
- **Skills**: Placed in `~/.codex/skills/`.
- **Rules**: Injected into `~/.codex/AGENTS.md`.

### 4. Cursor
- **Rules**: Can be synced into project workspace `.cursor/rules/` with `alwaysApply: true`.
