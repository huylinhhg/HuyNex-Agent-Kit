# Security Policy & Threat Model

## 🛡️ Threat Model & Scope of Guardrails

HuyNex Agent Kit provides **client-side defense-in-depth guardrails** for developers using autonomous AI Coding Agents (such as Claude Code, Codex, Antigravity, and Cursor).

### 1. What HuyNex Guardrails Protect Against
- **Unintended Force Push**: Intercepts `git push --force`, `-f`, `+<ref>`, and `--force-with-lease` before execution.
- **Accidental Hard Reset**: Intercepts `git reset --hard` to prevent uncommitted work from being wiped.
- **Aggressive Workspace Deletion**: Intercepts `rm -rf` on root directories (`/`, `~`, `$HOME`, `.`, `*`, or current workspace root).
- **Destructive Git Cleaning**: Intercepts `git clean -fd` to prevent losing untracked work.

### 2. Limitations & Honest Security Boundaries
- **Application Hook vs. OS Kernel**: The PreToolUse hook runs inside the agent application runtime (Claude Code / Python wrapper). It is **not** an operating system kernel sandbox (eBPF, seccomp, AppArmor, or container jail).
- **Indirect Execution**: Commands invoked via obfuscated shell scripts, base64 payloads, or arbitrary Python subprocesses executed outside the tool hook interface bypass application-level command parsers.
- **Defense in Depth**: We strongly recommend combining this kit with **Git Remote Branch Protections** (e.g. disabling force-push on GitHub/GitLab repository settings) and running untrusted autonomous agents inside isolated Docker containers or ephemeral VMs.

---

## 🔒 Reporting a Vulnerability

If you discover a security vulnerability or bypass technique in HuyNex Agent Kit:

1. **Do not** open a public GitHub issue.
2. Please report findings privately to: `security@huynex.com` or via GitHub Private Vulnerability Reporting.
3. Include the bypass payload, environment details (OS, Python version, Agent client), and expected vs actual behavior.
4. We aim to acknowledge receipt within 48 hours and provide a fix or mitigation notice within 7 days.
