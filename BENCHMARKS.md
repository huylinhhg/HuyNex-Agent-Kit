# HuyNex Token Distillation — Benchmark & Verification Report

This document outlines the reproducible benchmark methodology and results for `huynex-distill` (Semantic Token Distillation CLI).

---

## 📊 Summary Results

| Workload Type | Raw Output Size | Distilled Output Size | Token Reduction (%) | Error / Stack Trace Preservation |
|---|---|---|---|---|
| **Vitest / Jest Test Suite (120 tests)** | ~1,594 tokens (6,376 chars) | ~71 tokens (284 chars) | **95.5%** | **100% (4/4 errors captured)** |
| **Git Diff Output (5 changed files)** | ~1,491 tokens (5,966 chars) | ~434 tokens (1,736 chars) | **70.9%** | **100% (All modified hunks kept)** |
| **Real-world Test Suite (09-65nam-csnd)** | ~4,200 tokens (16,800 chars) | ~68 tokens (270 chars) | **98.4%** | **100% (Summary + test counts preserved)** |

---

## 🔬 How to Reproduce

Run the automated benchmark locally using the bundled CLI:

```bash
# Run benchmark mode
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
2. Verifies that the distilled output retains equal or greater error signal indicators.
3. If an error is detected in raw input but missing from the distilled output, the system **automatically falls back to raw mode**, guaranteeing zero diagnostic information loss.
