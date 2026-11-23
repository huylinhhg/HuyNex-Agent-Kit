"""
huynex-distill: Ultra-lightweight Semantic Token Distillation for AI Context.
Follows the 2 Pillars: Semantic Distillation & Conservation Gate.
"""

from .distiller import (
    strip_ansi_and_spinners,
    distill_test_output,
    distill_git_diff,
    distill_generic,
    distill_stream,
)
from .conservation import ConservationGate

__version__ = "1.0.0"
