# HuyNex Agent Kit — System Architecture

```
+-------------------------------------------------------------------------+
|                  Layer 1: Universal Portable Core                      |
| (Ladder of Laziness, Brutal Honesty, Zero-Guessing, Conservation Gate)  |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  Layer 2: Platform & Client Adapters                    |
|    (Claude Code @import, Codex AGENTS.md, Antigravity, Cursor .mdc)     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  Layer 3: Domain & Extension Packs                      |
|       (Office OpenXML ECMA-376 Guard, Media & Design Contracts)         |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|             Layer 4: Deterministic Runtime Defenses                     |
|  (PreToolUse Guardrails, huynex-distill Token Distiller, Spec Gate)    |
+-------------------------------------------------------------------------+
```

---

## 🏗️ Architectural Principles

1. **Separation of Policy and Execution**:
   - Instructions are declarations of intent (Soft Policy).
   - Shell hooks and filters are deterministic barriers (Hard Guards).
   - Never conflate prompt instructions with operating system isolation.

2. **The Conservation Gate**:
   - Any transformation, compression, or distillation step must verify its input against output (`sourceHash` or error indicator preservation).
   - If a failure indicator is present in raw input but missing in distilled output, the system fails closed and falls back to raw data.

3. **YAGNI & Minimal Complexity**:
   - Zero external binary dependencies for core functionality; built purely on standard library Python, POSIX shell, and PowerShell.
   - Idempotent lifecycle management: install, doctor, verify, and uninstall with atomic file writes.
