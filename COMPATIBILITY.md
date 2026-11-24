# Multi-Agent Compatibility Matrix

This matrix documents the integration and verification state across supported AI Coding Agents.

---

## 🛡️ Verification Tiers

To maintain strict engineering honesty, we distinguish between three levels of verification:
1. **AGENT_RUNTIME_VERIFIED**: Verified via live agent binary execution and interactive session behavior.
2. **FILESYSTEM_INTEGRATION_VERIFIED**: Verified via automated CI multi-agent integration smoke testing across Ubuntu, macOS, and Windows (validating directory discovery, settings hooks, non-destructive lifecycle, and data safety).
3. **FORMAT_VERIFIED**: Syntactically verified against vendor format specifications (e.g., Cursor `.mdc` YAML frontmatter, Claude Code path scoping).

---

## 📋 Compatibility Summary

| Agent Client | Skills Support | Rules Engine | Hook Enforcement | Verification Tier |
|---|---|---|---|---|
| **Claude Code** | Native (`~/.claude/skills/`) | 9 Modular Rules (`~/.claude/rules/`) with path-scoping | Native `PreToolUse` (`guardrail.py`) | **FILESYSTEM_INTEGRATION_VERIFIED** + **AGENT_RUNTIME_VERIFIED** |
| **Google Antigravity** | Native (`~/.gemini/config/skills/`) | Root Instruction (`~/.gemini/GEMINI.md`) | Soft Prompt Governance & System Rules | **FILESYSTEM_INTEGRATION_VERIFIED** + **AGENT_RUNTIME_VERIFIED** |
| **OpenAI Codex** | Native (`~/.codex/skills/`) | Root Instruction (`~/.codex/AGENTS.md`) | Soft Prompt Governance | **FILESYSTEM_INTEGRATION_VERIFIED** & **FORMAT_VERIFIED** |
| **Cursor** | Workspace (`.cursor/rules/`) | Native Rules (`.cursor/rules/*.mdc`) | Soft Prompt Governance | **FILESYSTEM_INTEGRATION_VERIFIED** & **FORMAT_VERIFIED** (`globs: "*"`) |
| **Shared Agent Hub** | Native (`~/.agents/skills/`) | Universal (`~/.agents/rules/`) | Global fallback | **FILESYSTEM_INTEGRATION_VERIFIED** |

---

## 🔍 Detailed Notes by Client

### 1. Claude Code
- **Skills**: Recognized in `~/.claude/skills/<skill-name>/SKILL.md`.
- **Rules**: Claude Code automatically loads all `.md` files deployed to `~/.claude/rules/`. Heavy engineering rules (`03-code-engineering` and `05-verification`) include Anthropic `paths:` scoping frontmatter to prevent token bloat during general sessions.
- **Hooks**: Supports deterministic `PreToolUse` hooks in `~/.claude/settings.json`. Exit code `2` interrupts execution and displays the refusal reason to the model.

### 2. Google Antigravity
- **Skills**: Deployed to `~/.gemini/config/skills/`.
- **Rules**: Injected into `~/.gemini/GEMINI.md` within `<!-- HUYNEX_AGENT_KIT_START -->` block.

### 3. OpenAI Codex
- **Skills**: Deployed to `~/.codex/skills/`.
- **Rules**: Injected into `~/.codex/AGENTS.md`.

### 4. Cursor
- **Rules**: Deployed as official Cursor `.mdc` format into `~/.cursor/rules/*.mdc` (or workspace `.cursor/rules/`).
- **Format**: Each file includes YAML frontmatter with `globs: "*"` and `alwaysApply: true` (valid YAML syntax validated against PyYAML parser) to ensure active injection into Cursor's agent context.

### 5. Shared Agent Hub
- **Fallback Directory**: `~/.agents/skills/` and `~/.agents/rules/`. Serves as cross-client standard repository when multiple tools share common configurations.
