#!/usr/bin/env python3
"""
Conservation Gate: Ensures zero silent data loss (Nothing Vanishes Silently).
Enforces the ADOS standard: Audit input and output entities and error preservation.
"""
import re
from typing import Dict, Any, Tuple


class ConservationGate:
    ERROR_PATTERNS = [
        re.compile(r"\bFAIL(?:ED)?\b", re.IGNORECASE),
        re.compile(r"\bAssertionError\b", re.IGNORECASE),
        re.compile(r"\b(?:Error|Exception)\b", re.IGNORECASE),
        re.compile(r"\b(?:FATAL|CRITICAL)\b", re.IGNORECASE),
        re.compile(r"\bpanic\b", re.IGNORECASE),
        re.compile(r"Traceback \(most recent call last\):", re.IGNORECASE),
    ]

    def __init__(self, fallback_on_loss: bool = True):
        self.fallback_on_loss = fallback_on_loss

    def count_error_markers(self, text: str) -> int:
        count = 0
        for pattern in self.ERROR_PATTERNS:
            count += len(pattern.findall(text))
        return count

    def verify_error_conservation(self, raw: str, distilled: str) -> bool:
        """
        Verify that no error markers in raw were completely eradicated in distilled.
        If raw has errors, distilled must also retain errors.
        """
        raw_errors = self.count_error_markers(raw)
        distilled_errors = self.count_error_markers(distilled)

        if raw_errors > 0 and distilled_errors == 0:
            return False
        return True

    def calculate_stats(self, raw: str, distilled: str) -> Dict[str, Any]:
        chars_in = len(raw)
        chars_out = len(distilled)

        # Estimate tokens roughly at 4 characters per token
        tokens_in = max(1, chars_in // 4)
        tokens_out = max(1, chars_out // 4)

        reduction_pct = 0.0
        if chars_in > 0:
            reduction_pct = round(((chars_in - chars_out) / chars_in) * 100, 1)

        errors_in = self.count_error_markers(raw)
        errors_out = self.count_error_markers(distilled)
        conservation_passed = self.verify_error_conservation(raw, distilled)

        return {
            "chars_in": chars_in,
            "chars_out": chars_out,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "reduction_pct": reduction_pct,
            "errors_in": errors_in,
            "errors_out": errors_out,
            "conservation_passed": conservation_passed,
        }

    def audit_and_distill(
        self,
        raw: str,
        runner_type: str = "generic",
        distill_func: Any = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Runs distillation through the Conservation Gate.
        If distillation fails conservation and fallback_on_loss is True, returns raw.
        """
        if distill_func is not None:
            candidate = distill_func(raw)
        else:
            from .distiller import distill_stream
            candidate = distill_stream(raw, cmd_hint=runner_type)

        stats = self.calculate_stats(raw, candidate)

        if not stats["conservation_passed"]:
            if self.fallback_on_loss:
                # Fallback to raw to prevent silent error loss
                fallback_stats = self.calculate_stats(raw, raw)
                fallback_stats["conservation_warning"] = "FALLBACK_TRIGGERED_ERROR_LOSS"
                return raw, fallback_stats

        return candidate, stats
