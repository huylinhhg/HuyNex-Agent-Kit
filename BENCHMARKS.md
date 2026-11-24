# HuyNex Token Distillation — Benchmark & Verification Report

This document outlines the reproducible benchmark methodology and measured results for `huynex-distill` (Semantic Token Distillation CLI), synchronized directly with `./bin/huynex-distill --benchmark`.

---

## 📊 Reproducible Benchmark Results

Measured directly via `python3 bin/huynex-distill --benchmark` on the bundled synthetic fixtures:

| Workload Type | Raw Output Size | Distilled Output Size | Character Reduction (Est. Tokens*) | Acceptance Gate | Error / Diagnostic Preservation |
|---|---|---|---|---|---|
| **Test Suite Distillation** | 6,373 chars (~1,593 est. tokens) | 297 chars (~74 est. tokens) | **95.3%** | `>= 70%` (PASS) | **100%** (Error markers: `3 -> 4`, conserved) |
| **Git Diff Distillation** | 5,966 chars (~1,491 est. tokens) | 3,140 chars (~785 est. tokens) | **47.4%** | `>= 40%` (PASS) | **100%** (Context collapsed, modified hunks preserved) |

> **Measurement & Scope Note**: Benchmark metrics directly measure raw character stream reduction. Estimated token counts use standard character heuristics (~4 characters per token) for intuitive reference; they do not represent exact hardware BPE token counts, which vary across model tokenizers (e.g. OpenAI o200k, Claude tokenizer). The figures above reflect the deterministic fixtures built into `bin/huynex-distill --benchmark` (verified in CI on Linux and macOS). Input streams are capped at the bounded buffer limit (`MAX_BUFFER_BYTES`) to prevent memory exhaustion.

---

## 🔬 How to Reproduce

Run the automated benchmark locally using the bundled CLI:

```bash
# Run benchmark mode (exits non-zero if acceptance thresholds or conservation gate fail)
./bin/huynex-distill --benchmark
```

Or pipe real command outputs directly:

```bash
# In your terminal
npm test | ./bin/huynex-distill
git diff | ./bin/huynex-distill --diff
```

---

## 🛡️ The Conservation Gate Principle (Nothing Vanishes Silently)

Compression without verification is dangerous. If a token filter accidentally removes a fatal error message or panic trace, the AI Agent will hallucinate that everything passed.

`huynex-distill` enforces the **Conservation Gate**:
1. Pre-scans raw input for fatal patterns: `FAIL`, `Error:`, `Exception:`, `Traceback`, `AssertionError`, `panic:`.
2. Verifies that the distilled output retains every distinct error signature present in the raw input.
3. If an error signature detected in raw input is missing from the distilled output, the system **automatically falls back to raw mode**, guaranteeing zero diagnostic information loss within the bounded buffer.
