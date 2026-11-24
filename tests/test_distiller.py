#!/usr/bin/env python3
"""
Unit tests for huynex-distill adhering to TDD and Conservation Gate requirements.
"""
import os
import sys
import unittest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from distill.distiller import (
    strip_ansi_and_spinners,
    distill_test_output,
    distill_git_diff,
    distill_generic,
    distill_stream,
    enforce_buffer_cap,
)
from distill.conservation import ConservationGate


class TestAnsiAndSpinners(unittest.TestCase):
    def test_strip_ansi_color_codes(self):
        raw = "\x1b[32mPASS\x1b[39m \x1b[2msrc/index.test.ts\x1b[22m"
        clean = strip_ansi_and_spinners(raw)
        self.assertEqual(clean, "PASS src/index.test.ts")

    def test_strip_carriage_return_progress(self):
        raw = "Downloading: 10%\rDownloading: 50%\rDownloading: 100%\nDone!"
        clean = strip_ansi_and_spinners(raw)
        self.assertIn("Done!", clean)
        self.assertNotIn("Downloading: 10%", clean)


class TestTestDistillation(unittest.TestCase):
    def test_vitest_output_compression_with_failure(self):
        raw_lines = [
            " \x1b[32m✓\x1b[39m tests/auth/login.test.ts (5 tests) 12ms",
            " \x1b[32m✓\x1b[39m tests/auth/register.test.ts (3 tests) 8ms",
            " \x1b[32m✓\x1b[39m tests/utils/hash.test.ts (20 tests) 4ms",
            " \x1b[31mFAIL\x1b[39m tests/billing/checkout.test.ts > payment fails on card expired",
            "AssertionError: expected 'active' to be 'expired'",
            "    at /workspace/src/billing.ts:42:15",
            "    at processTicksAndRejections (node:internal/process/task_queues:95:5)",
            " \x1b[32m✓\x1b[39m tests/billing/invoice.test.ts (10 tests) 15ms",
            "Test Files  1 failed | 4 passed (5)",
            "     Tests  1 failed | 38 passed (39)",
            "  Duration  1.24s",
        ]
        raw = "\n".join(raw_lines)
        distilled = distill_test_output(raw)

        self.assertIn("FAIL tests/billing/checkout.test.ts", distilled)
        self.assertIn("AssertionError: expected 'active' to be 'expired'", distilled)
        self.assertIn("at /workspace/src/billing.ts:42:15", distilled)
        self.assertNotIn("tests/auth/login.test.ts (5 tests)", distilled)
        self.assertIn("passed", distilled)
        self.assertLess(len(distilled), len(raw))


class TestGitDiffDistillation(unittest.TestCase):
    def test_collapse_large_unchanged_context(self):
        diff_lines = [
            "diff --git a/src/app.ts b/src/app.ts",
            "index 1234567..89abcdef 100644",
            "--- a/src/app.ts",
            "+++ b/src/app.ts",
            "@@ -10,25 +10,25 @@ function run() {",
        ]
        for i in range(10):
            diff_lines.append(f"     const val_{i} = {i};")
        diff_lines.append("-    return oldFunc();")
        diff_lines.append("+    return newFunc();")
        for i in range(10):
            diff_lines.append(f"     const after_{i} = {i};")
        diff_lines.append(" }")

        raw = "\n".join(diff_lines)
        distilled = distill_git_diff(raw)

        self.assertIn("-    return oldFunc();", distilled)
        self.assertIn("+    return newFunc();", distilled)
        self.assertIn("lines unchanged", distilled)
        self.assertLess(len(distilled), len(raw))


class TestBufferCap(unittest.TestCase):
    def test_buffer_cap_truncation(self):
        huge_text = "A" * (25 * 1024 * 1024)  # 25 MB
        capped = enforce_buffer_cap(huge_text, max_bytes=1000)
        self.assertIn("Stream capped", capped)
        self.assertLessEqual(len(capped), 1200)


class TestConservationGate(unittest.TestCase):
    def test_gate_detects_token_savings(self):
        raw = "INFO: Processing item\n" * 50 + "ERROR: Database connection timeout\n    at db.connect()\n"
        gate = ConservationGate()
        distilled, stats = gate.audit_and_distill(raw, runner_type="generic")

        self.assertIn("Database connection timeout", distilled)
        self.assertGreater(stats["reduction_pct"], 30.0)
        self.assertTrue(stats["conservation_passed"])

    def test_gate_catches_dropped_distinct_errors(self):
        gate = ConservationGate(fallback_on_loss=False)
        raw = (
            "Error: DB timeout connecting to postgres\n"
            "Error: Access denied for user admin\n"
            "Error: Data corrupt in table orders\n"
        )
        distilled_partial = (
            "Error: DB timeout connecting to postgres\n"
            "Error: Access denied for user admin\n"
        )
        passed, missing = gate.verify_error_conservation(raw, distilled_partial)
        self.assertFalse(passed)
        self.assertEqual(len(missing), 1)
        self.assertIn("Data corrupt", missing[0])

    def test_gate_falls_back_to_raw_on_loss(self):
        gate = ConservationGate(fallback_on_loss=True)
        raw = "AssertionError: expected 1 to be 2\n"

        # A broken distiller that erases all errors
        def broken_distiller(text):
            return "All passed successfully\n"

        output, stats = gate.audit_and_distill(raw, distill_func=broken_distiller)
        # Must fallback to raw input
        self.assertEqual(output, raw)
        self.assertIn("FALLBACK_TRIGGERED", stats.get("conservation_warning", ""))


if __name__ == "__main__":
    unittest.main()
