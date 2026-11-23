#!/usr/bin/env python3
"""
Unit tests for huynex-distill adhering to TDD and Conservation Gate requirements.
"""
import sys
import os
import unittest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from distill.distiller import (
    strip_ansi_and_spinners,
    distill_test_output,
    distill_git_diff,
    distill_generic,
    distill_stream,
)
from distill.conservation import ConservationGate


class TestAnsiAndSpinners(unittest.TestCase):
    def test_strip_ansi_color_codes(self):
        raw = "\x1b[32mPASS\x1b[39m \x1b[2msrc/index.test.ts\x1b[22m"
        clean = strip_ansi_and_spinners(raw)
        self.assertEqual(clean, "PASS src/index.test.ts")

    def test_strip_carriage_return_progress(self):
        # Progress bar repeatedly overwriting via \r
        raw = "Downloading: 10%\rDownloading: 50%\rDownloading: 100%\nDone!"
        clean = strip_ansi_and_spinners(raw)
        self.assertIn("Done!", clean)
        self.assertNotIn("Downloading: 10%", clean)


class TestTestDistillation(unittest.TestCase):
    def test_vitest_output_compression_with_failure(self):
        # Sample vitest output with 10 passing tests and 1 failing test
        raw_lines = [
            " \x1b[32m✓\x1b[39m tests/auth/login.test.ts (5 tests) 12ms",
            " \x1b[32m✓\x1b[39m tests/auth/register.test.ts (3 tests) 8ms",
            " \x1b[32m✓\x1b[39m tests/utils/hash.test.ts (20 tests) 4ms",
            " \x1b[31mFAIL\x1b[39m tests/billing/checkout.test.ts > payment fails on card expired",
            "AssertionError: expected 'active' to be 'expired'",
            "    at /Users/maihuy/app/billing.ts:42:15",
            "    at processTicksAndRejections (node:internal/process/task_queues:95:5)",
            " \x1b[32m✓\x1b[39m tests/billing/invoice.test.ts (10 tests) 15ms",
            "Test Files  1 failed | 4 passed (5)",
            "     Tests  1 failed | 38 passed (39)",
            "  Duration  1.24s",
        ]
        raw = "\n".join(raw_lines)
        distilled = distill_test_output(raw)

        # Verification:
        # 1. Error preserved 100%
        self.assertIn("FAIL tests/billing/checkout.test.ts", distilled)
        self.assertIn("AssertionError: expected 'active' to be 'expired'", distilled)
        self.assertIn("at /Users/maihuy/app/billing.ts:42:15", distilled)
        # 2. Passing tests collapsed
        self.assertNotIn("tests/auth/login.test.ts (5 tests)", distilled)
        self.assertIn("passed", distilled)
        # 3. Reduction achieved
        self.assertLess(len(distilled), len(raw))


class TestGitDiffDistillation(unittest.TestCase):
    def test_collapse_large_unchanged_context(self):
        # A git diff with 20 unchanged lines surrounding a single change
        diff_lines = [
            "diff --git a/src/app.ts b/src/app.ts",
            "index 1234567..89abcdef 100644",
            "--- a/src/app.ts",
            "+++ b/src/app.ts",
            "@@ -10,25 +10,25 @@ function run() {",
        ]
        # 10 unchanged lines
        for i in range(10):
            diff_lines.append(f"     const val_{i} = {i};")
        # 1 change
        diff_lines.append("-    return oldFunc();")
        diff_lines.append("+    return newFunc();")
        # 10 unchanged lines
        for i in range(10):
            diff_lines.append(f"     const after_{i} = {i};")
        diff_lines.append(" }")

        raw = "\n".join(diff_lines)
        distilled = distill_git_diff(raw)

        # Verification:
        self.assertIn("-    return oldFunc();", distilled)
        self.assertIn("+    return newFunc();", distilled)
        self.assertIn("omitted", distilled)
        self.assertLess(len(distilled), len(raw))


class TestConservationGate(unittest.TestCase):
    def test_gate_detects_token_savings(self):
        raw = "INFO: Processing item\n" * 50 + "ERROR: Database connection timeout\n    at db.connect()\n"
        gate = ConservationGate()
        distilled, stats = gate.audit_and_distill(raw, runner_type="generic")

        self.assertGreaterEqual(stats["reduction_pct"], 50.0)
        self.assertTrue(stats["conservation_passed"])
        self.assertIn("Database connection timeout", distilled)

    def test_gate_warns_on_error_loss(self):
        raw = "CRITICAL ERROR: Kernel panic!"
        # If someone passed a buggy distillation that dropped the error
        gate = ConservationGate()
        is_safe = gate.verify_error_conservation(raw, "Everything was fine.")
        self.assertFalse(is_safe)


    def test_benchmark_large_test_suite_reduction(self):
        # Generate 100 passing tests and 2 failures with stack traces
        lines = []
        for i in range(100):
            lines.append(f" \x1b[32m✓\x1b[39m tests/module_{i}/suite.test.ts ({i+1} tests) {i*2}ms")
        lines.append(" \x1b[31mFAIL\x1b[39m tests/core/auth.test.ts > login fails")
        lines.append(" AssertionError: Expected 200 Received 401")
        lines.append("     at /Users/maihuy/app/auth.ts:15:10")
        lines.append("     at processTicksAndRejections (node:internal/process/task_queues:95:5)")
        lines.append(" Test Files  1 failed | 100 passed (101)")
        lines.append("      Tests  1 failed | 5050 passed (5051)")
        lines.append("   Duration  3.42s")
        raw = "\n".join(lines)

        gate = ConservationGate()
        distilled, stats = gate.audit_and_distill(raw, runner_type="test")

        # Acceptance Criteria: >= 60% token reduction
        self.assertGreaterEqual(stats["reduction_pct"], 80.0)
        self.assertTrue(stats["conservation_passed"])
        self.assertIn("AssertionError: Expected 200 Received 401", distilled)
        self.assertIn("at /Users/maihuy/app/auth.ts:15:10", distilled)

    def test_benchmark_large_git_diff_reduction(self):
        # Generate a large diff with multiple hunks having 30 unchanged lines each
        lines = ["diff --git a/src/service.ts b/src/service.ts", "--- a/src/service.ts", "+++ b/src/service.ts"]
        for hunk in range(5):
            lines.append(f"@@ -{hunk*50},40 +{hunk*50},40 @@")
            for j in range(20):
                lines.append(f"     const context_var_{hunk}_{j} = true;")
            lines.append(f"-    const old_config_{hunk} = false;")
            lines.append(f"+    const new_config_{hunk} = true;")
            for j in range(20):
                lines.append(f"     const context_post_{hunk}_{j} = true;")
        raw = "\n".join(lines)

        gate = ConservationGate()
        distilled, stats = gate.audit_and_distill(raw, runner_type="git")

        # Acceptance Criteria: >= 60% reduction
        self.assertGreaterEqual(stats["reduction_pct"], 60.0)
        self.assertTrue(stats["conservation_passed"])
        self.assertIn("+    const new_config_0 = true;", distilled)
        self.assertIn("-    const old_config_0 = false;", distilled)
        self.assertIn("unchanged lines omitted", distilled)


if __name__ == "__main__":
    unittest.main()
