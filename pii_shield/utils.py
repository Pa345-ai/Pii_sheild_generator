"""
Utility Functions
Helper functions for PII detection and processing
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PIIMatch:
    """Represents a detected PII instance"""
    pii_type: str
    value: str
    start: int
    end: int
    confidence: float
    masked_value: str
    context: Optional[str] = None


class TextProcessor:
    """Utilities for text processing"""
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text"""
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def get_context(text: str, start: int, end: int, window: int = 50) -> str:
        """
        Get context around a position
        
        Args:
            text: Full text
            start: Start position
            end: End position
            window: Number of characters before/after
            
        Returns:
            Context string
        """
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        
        before = text[context_start:start]
        match = text[start:end]
        after = text[end:context_end]
        
        return f"...{before}[{match}]{after}..."
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def is_capitalized_word(word: str) -> bool:
        """Check if word is properly capitalized (title case)"""
        if len(word) == 0:
            return False
        if len(word) == 1:
            return word.isupper()
        return word[0].isupper() and word[1:].islower()


class OverlapResolver:
    """Resolves overlapping PII detections"""
    
    @staticmethod
    def resolve_overlaps(matches: List[PIIMatch]) -> List[PIIMatch]:
        """
        Remove overlapping matches, keeping highest confidence
        
        Args:
            matches: List of PIIMatch objects
            
        Returns:
            List of non-overlapping matches
        """
        if not matches:
            return []
        
        # Sort by start position, then by confidence (descending)
        sorted_matches = sorted(
            matches,
            key=lambda x: (x.start, -x.confidence)
        )
        
        result = []
        
        for match in sorted_matches:
            # Check if this match overlaps with any already selected
            overlaps = False
            for existing in result:
                if OverlapResolver._has_overlap(match, existing):
                    # Keep the one with higher confidence
                    if match.confidence > existing.confidence:
                        result.remove(existing)
                        result.append(match)
                    overlaps = True
                    break
            
            if not overlaps:
                result.append(match)
        
        # Sort by position for final output
        return sorted(result, key=lambda x: x.start)
    
    @staticmethod
    def _has_overlap(match1: PIIMatch, match2: PIIMatch) -> bool:
        """Check if two matches overlap"""
        return (match1.start < match2.end and match1.end > match2.start)


class ConfidenceCalculator:
    """Calculate confidence scores for PII detections"""
    
    @staticmethod
    def adjust_confidence(
        base_confidence: float,
        context_match: bool = False,
        validation_passed: bool = True,
        length_appropriate: bool = True
    ) -> float:
        """
        Adjust confidence based on various factors
        
        Args:
            base_confidence: Base confidence from pattern
            context_match: Whether surrounding context matches
            validation_passed: Whether validation checks passed
            length_appropriate: Whether length is appropriate
            
        Returns:
            Adjusted confidence score (0.0-1.0)
        """
        confidence = base_confidence
        
        # Boost for positive context
        if context_match:
            confidence = min(1.0, confidence + 0.1)
        
        # Reduce if validation failed
        if not validation_passed:
            confidence *= 0.5
        
        # Reduce if length is inappropriate
        if not length_appropriate:
            confidence *= 0.7
        
        return max(0.0, min(1.0, confidence))


class StatisticsCollector:
    """Collect statistics about PII detections"""
    
    def __init__(self):
        self.total_detections = 0
        self.detections_by_type = {}
        self.total_texts_processed = 0
        self.total_processing_time = 0.0
    
    def record_detection(self, pii_type: str):
        """Record a PII detection"""
        self.total_detections += 1
        if pii_type not in self.detections_by_type:
            self.detections_by_type[pii_type] = 0
        self.detections_by_type[pii_type] += 1
    
    def record_processing(self, processing_time: float):
        """Record processing time"""
        self.total_texts_processed += 1
        self.total_processing_time += processing_time
    
    def get_stats(self) -> dict:
        """Get statistics summary"""
        avg_time = (self.total_processing_time / self.total_texts_processed
                   if self.total_texts_processed > 0 else 0.0)
        
        return {
            'total_detections': self.total_detections,
            'detections_by_type': self.detections_by_type,
            'total_texts_processed': self.total_texts_processed,
            'avg_processing_time_ms': avg_time * 1000,
        }
    
    def reset(self):
        """Reset statistics"""
        self.total_detections = 0
        self.detections_by_type.clear()
        self.total_texts_processed = 0
        self.total_processing_time = 0.0


class BatchProcessor:
    """Process multiple texts efficiently"""
    
    def __init__(self, detector):
        """
        Initialize batch processor
        
        Args:
            detector: PIIDetector instance
        """
        self.detector = detector
    
    def process_batch(
        self,
        texts: List[str],
        confidence_threshold: float = 0.7
    ) -> List[List[PIIMatch]]:
        """
        Process multiple texts
        
        Args:
            texts: List of texts to process
            confidence_threshold: Minimum confidence threshold
            
        Returns:
            List of match lists (one per input text)
        """
        results = []
        for text in texts:
            matches = self.detector.detect_all(text, confidence_threshold)
            results.append(matches)
        return results


class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'total_matches': 0,
            'total_time_ms': 0.0,
            'min_time_ms': float('inf'),
            'max_time_ms': 0.0,
        }
    
    def record_request(self, num_matches: int, time_ms: float):
        """Record a request's metrics"""
        self.metrics['total_requests'] += 1
        self.metrics['total_matches'] += num_matches
        self.metrics['total_time_ms'] += time_ms
        self.metrics['min_time_ms'] = min(self.metrics['min_time_ms'], time_ms)
        self.metrics['max_time_ms'] = max(self.metrics['max_time_ms'], time_ms)
    
    def get_summary(self) -> dict:
        """Get performance summary"""
        avg_time = (self.metrics['total_time_ms'] / self.metrics['total_requests']
                   if self.metrics['total_requests'] > 0 else 0.0)
        
        return {
            'total_requests': self.metrics['total_requests'],
            'total_matches': self.metrics['total_matches'],
            'avg_time_ms': avg_time,
            'min_time_ms': self.metrics['min_time_ms'] if self.metrics['min_time_ms'] != float('inf') else 0,
            'max_time_ms': self.metrics['max_time_ms'],
            'throughput_per_sec': 1000 / avg_time if avg_time > 0 else 0,
        }


def sanitize_for_logging(text: str, max_length: int = 100) -> str:
    """
    Sanitize text for safe logging
    
    Args:
        text: Text to sanitize
        max_length: Maximum length
        
    Returns:
        Sanitized text
    """
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    # Remove any potential PII (basic)
    # This is a simple version - in production, run full detection
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    text = re.sub(r'\b\d{16}\b', '[CARD]', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    return text


def format_match_for_display(match: PIIMatch) -> str:
    """
    Format a PII match for display
    
    Args:
        match: PIIMatch object
        
    Returns:
        Formatted string
    """
    return (f"{match.pii_type}: '{match.value}' -> '{match.masked_value}' "
            f"(confidence: {match.confidence:.2f})")


def calculate_text_entropy(text: str) -> float:
    """
    Calculate Shannon entropy of text
    Higher entropy suggests more random/diverse content
    
    Args:
        text: Input text
        
    Returns:
        Entropy value
    """
    import math
    from collections import Counter
    
    if not text:
        return 0.0
    
    # Count character frequencies
    counter = Counter(text)
    length = len(text)
    
    # Calculate entropy
    entropy = 0.0
    for count in counter.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    
    return entropy
