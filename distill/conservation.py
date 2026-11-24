#!/usr/bin/env python3
"""
Conservation Gate: Ensures zero silent data loss (Nothing Vanishes Silently).
Enforces the standard: Audit input and output entities and ensure 100% error signature preservation.
"""
import re
from typing import Dict, Any, Tuple, Set, List


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

    def extract_error_signatures(self, text: str) -> Set[str]:
        """
        Trích xuất tập hợp các chữ ký/thông điệp lỗi cụ thể (error signatures).
        Mỗi dòng chứa lỗi được chuẩn hóa để đối chiếu từng lỗi riêng biệt (Error A, Error B, Error C).
        """
        signatures = set()
        for line in text.splitlines():
            line_clean = line.strip()
            if not line_clean:
                continue
            for pattern in self.ERROR_PATTERNS:
                if pattern.search(line_clean):
                    # Chuẩn hóa khoảng trắng và lấy tối đa 100 ký tự đại diện cho thông điệp
                    norm = re.sub(r"\s+", " ", line_clean)
                    signatures.add(norm[:120])
                    break
        return signatures

    def verify_error_conservation(self, raw: str, distilled: str) -> Tuple[bool, List[str]]:
        """
        Kiểm tra tính bảo toàn lỗi nghiêm ngặt:
        1. Nếu raw có lỗi, distilled không được có 0 lỗi.
        2. TẤT CẢ các chữ ký lỗi riêng biệt (distinct error signatures) trong raw
           bắt buộc phải xuất hiện trong distilled (không được làm rớt bất kỳ lỗi nào).
        """
        raw_errors = self.count_error_markers(raw)
        distilled_errors = self.count_error_markers(distilled)

        if raw_errors > 0 and distilled_errors == 0:
            return False, ["All error markers eradicated in distilled output"]

        raw_sigs = self.extract_error_signatures(raw)
        distilled_norm = re.sub(r"\s+", " ", distilled)
        missing_sigs = []

        for sig in raw_sigs:
            sig_norm = re.sub(r"\s+", " ", sig).strip()
            # Lấy phần cốt lõi của thông điệp lỗi (sau dấu hai chấm nếu có)
            core_msg = sig_norm.split(":", 1)[-1].strip() if ":" in sig_norm else sig_norm

            # Kiểm tra xem sig hoặc core_msg có nằm trong distilled đã chuẩn hóa khoảng trắng không
            if sig_norm not in distilled_norm and core_msg not in distilled_norm:
                missing_sigs.append(sig)

        if missing_sigs:
            return False, missing_sigs

        return True, []

    @staticmethod
    def estimate_tokens(char_count: int) -> int:
        """
        Ước tính số token theo tiêu chuẩn thực nghiệm ~4 ký tự / token (BPE estimate).
        Lưu ý: Đây là số ước tính kỹ thuật (heuristic estimate), không thay thế tokenizer BPE cụ thể.
        """
        return max(1, char_count // 4)

    def calculate_stats(self, raw: str, distilled: str) -> Dict[str, Any]:
        chars_in = len(raw)
        chars_out = len(distilled)

        tokens_in = self.estimate_tokens(chars_in)
        tokens_out = self.estimate_tokens(chars_out)

        reduction_pct = 0.0
        if chars_in > 0:
            reduction_pct = round(((chars_in - chars_out) / chars_in) * 100, 1)

        errors_in = self.count_error_markers(raw)
        errors_out = self.count_error_markers(distilled)
        conservation_passed, missing_errors = self.verify_error_conservation(raw, distilled)

        return {
            "chars_in": chars_in,
            "chars_out": chars_out,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "reduction_pct": reduction_pct,
            "errors_in": errors_in,
            "errors_out": errors_out,
            "conservation_passed": conservation_passed,
            "missing_errors": missing_errors,
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
                fallback_stats = self.calculate_stats(raw, raw)
                fallback_stats["conservation_warning"] = f"FALLBACK_TRIGGERED: Missing {len(stats['missing_errors'])} errors"
                return raw, fallback_stats

        return candidate, stats
