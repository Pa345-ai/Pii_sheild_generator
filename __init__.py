"""
PII-Shield Engine
Enterprise-grade PII detection and masking for AI traffic protection
"""

from .detector import PIIDetector
from .patterns import PIIType, PIIPattern
from .masking import PIIMasker, MaskingStrategy
from .validator import PIIValidator

__version__ = "1.0.0"
__author__ = "PII-Shield Team"
__all__ = [
    "PIIDetector",
    "PIIType",
    "PIIPattern",
    "PIIMasker",
    "MaskingStrategy",
    "PIIValidator",
]
