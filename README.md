# HuyNex Agent Kit

[![CI](https://github.com/huylinhhg/HuyNex-Agent-Kit/actions/workflows/ci.yml/badge.svg)](https://github.com/huylinhhg/HuyNex-Agent-Kit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version: 0.3.6](https://img.shields.io/badge/Version-0.3.6-green.svg)](VERSION)
[![Platform: macOS | Linux | Windows](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-orange.svg)](#)

[ **English** | [Tiếng Việt](README.vi.md) ]

> **Production-grade governance, deterministic safety guardrails, and token distillation for AI Coding Agents** (Claude Code, OpenAI Codex, Google Antigravity, Cursor).

---

## ⚡ Quickstart — 1-Line Universal Installer

Deploy skills, modular rules, and security guardrails to your local agent clients in seconds:

### macOS & Linux
```bash
curl -fsSL https://raw.githubusercontent.com/huylinhhg/HuyNex-Agent-Kit/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/huylinhhg/HuyNex-Agent-Kit/main/install.ps1 | iex
```

Or manually clone and run:
```bash
git clone https://github.com/huylinhhg/HuyNex-Agent-Kit.git
cd HuyNex-Agent-Kit
python3 scripts/install.py --all
```

---

## 🌟 Core Pillars

1. **Deterministic Guardrails over Prompt Pleading**:
   Stop begging LLMs not to force-push. Intercept destructive commands (`git push --force`, `rm -rf`, `git reset --hard`) via `PreToolUse` hooks before execution.
2. **Semantic Token Distillation (`huynex-distill`)**:
   Filter noisy test logs and git diffs to cut **60% to 95%** of context tokens while preserving 100% of diagnostic stack traces.
3. **The Ladder of Laziness (7-Rung Engineering Philosophy)**:
   The best code is the code you never write. Enforce *YAGNI → Code Reuse → Standard Library → Native Platform → Existing Dependencies → Minimal Code → Smallest Change*.
4. **The Conservation Gate**:
   Nothing vanishes silently. Every transformation is checked against inputs to guarantee that error traces and critical data are never dropped.

---

## 🛡️ Architecture & The 9 Modular Rules (`rules/modules/`)

Organized as lean, composable rule modules compatible with Claude Code `@import` and multi-client root instructions:

| Module | Focus |
|---|---|
| `01-communication.md` | Technical Brutal Honesty, Goal Ancestry, Single-Tier Git Auto-Sync. |
| `02-truth-context.md` | Anti-Hallucination (Zero-Guessing), Semantic Distillation, Conservation Gate. |
| `03-code-engineering.md` | Senior Dev's Ladder of Laziness (7 Rungs), AGENTS.md, Zero-Friction DESIGN.md. |
| `04-data-safety.md` | 3-Tier Risk Approval Gate, Single-Root Safety (anti-destruction). |
| `05-verification.md` | Risk-based empirical verification standards. |
| `06-collaboration.md` | Subagent delegation boundaries and model selection. |
| `07-permissions-memory.md` | Credential/Secret protection and isolation. |
| `08-versioning.md` | SemVer 2.0.0 and Keep a Changelog standards. |
| `09-workspace-layout.md` | Portable workspace structure and Power-User Zero-Bloat standard. |

---

## 🔬 Benchmark: Token Distillation

Measured using reproducible test suite logs:

| Workload | Raw Chars (Tokens) | Distilled Chars (Tokens) | Token Savings | Diagnostic Retention |
|---|---|---|---|---|
| **Vitest Test Suite (101 tests)** | 6,373 (~1,593) | 297 (~74) | **95.3%** | **100% (All failure markers captured)** |
| **Git Diff (6 hunks)** | 5,966 (~1,491) | 3,140 (~785) | **47.4%** | **100% (Context collapsed, hunks preserved)** |

*All benchmarks dynamically verified: Test logs achieve $\ge 70\%$ reduction, Git diffs achieve $\ge 40\%$ reduction, with 100% error signatures conserved within the bounded buffer.*

To reproduce locally:
```bash
./bin/huynex-distill --benchmark

# Distill test runner output directly from pipe:
npm test | ./bin/huynex-distill

# Distill git diff directly from pipe:
git diff | ./bin/huynex-distill --diff
```
*See [BENCHMARKS.md](BENCHMARKS.md) for full methodology.*

---

## 🧰 Management & Diagnostics CLI

HuyNex Agent Kit includes a full lifecycle management suite:

```bash
# Verify system integrity, rule deployment, and hook permissions
python3 scripts/install.py --doctor

# Dry-run preview of installation changes without modifying files
python3 scripts/install.py --check

# Safely uninstall files managed by HuyNex Agent Kit
python3 scripts/install.py --uninstall

# Run evidence-based task verification gate
python3 scripts/spec_gate.py TASK.md --json
```

---

## 📚 Documentation Links

- [System Architecture](ARCHITECTURE.md)
- [Compatibility Matrix](COMPATIBILITY.md)
- [Security Policy & Threat Model](SECURITY.md)
- [Benchmark Report](BENCHMARKS.md)
- [Contributing Guidelines](CONTRIBUTING.md)

---

## 📄 License

Distributed under the **MIT License**. Free for personal and commercial use.
