"""
PII Detector Module
Main detection engine that coordinates pattern matching, validation, and masking
"""

import re
import time
from typing import List, Optional, Set
from .patterns import (
    PIIType, PATTERN_REGISTRY, NAME_PATTERNS, ADDRESS_PATTERNS
)
from .validator import PIIValidator, ContextValidator
from .masking import PIIMasker, MaskingStrategy, MaskingConfig
from .utils import (
    PIIMatch, OverlapResolver, ConfidenceCalculator,
    StatisticsCollector, TextProcessor
)


class PIIDetector:
    """
    Main PII Detection Engine
    Coordinates pattern matching, validation, and confidence scoring
    """
    
    def __init__(
        self,
        enable_context_validation: bool = True,
        enable_strict_validation: bool = True,
        collect_statistics: bool = False
    ):
        """
        Initialize PII Detector
        
        Args:
            enable_context_validation: Use context for validation
            enable_strict_validation: Apply strict validation rules
            collect_statistics: Collect detection statistics
        """
        self.validator = PIIValidator()
        self.context_validator = ContextValidator()
        self.masker = PIIMasker()
        self.masking_config = MaskingConfig()
        
        self.enable_context_validation = enable_context_validation
        self.enable_strict_validation = enable_strict_validation
        
        self.statistics = StatisticsCollector() if collect_statistics else None
        
        # Compile patterns for efficiency
        self._compiled_patterns = PATTERN_REGISTRY.get_compiled_patterns()
    
    def detect_all(
        self,
        text: str,
        confidence_threshold: float = 0.7,
        pii_types: Optional[List[PIIType]] = None
    ) -> List[PIIMatch]:
        """
        Detect all PII in text
        
        Args:
            text: Input text to scan
            confidence_threshold: Minimum confidence score (0.0-1.0)
            pii_types: Optional list of specific PII types to detect
            
        Returns:
            List of PIIMatch objects sorted by position
        """
        start_time = time.time()
        
        all_matches = []
        
        # Detect pattern-based PII
        all_matches.extend(self._detect_pattern_based(text, pii_types))
        
        # Detect names (requires special handling)
        if pii_types is None or PIIType.PERSON_NAME in pii_types:
            all_matches.extend(self._detect_names(text))
        
        # Detect addresses (requires special handling)
        if pii_types is None or PIIType.ADDRESS in pii_types:
            all_matches.extend(self._detect_addresses(text))
        
        # Filter by confidence threshold
        filtered_matches = [
            m for m in all_matches
            if m.confidence >= confidence_threshold
        ]
        
        # Resolve overlaps
        final_matches = OverlapResolver.resolve_overlaps(filtered_matches)
        
        # Record statistics
        if self.statistics:
            processing_time = time.time() - start_time
            self.statistics.record_processing(processing_time)
            for match in final_matches:
                self.statistics.record_detection(match.pii_type)
        
        return final_matches
    
    def _detect_pattern_based(
        self,
        text: str,
        pii_types: Optional[List[PIIType]] = None
    ) -> List[PIIMatch]:
        """Detect PII using regex patterns"""
        matches = []
        
        for pattern_def, compiled_regex in self._compiled_patterns:
            # Skip if not in requested types
            if pii_types and pattern_def.pii_type not in pii_types:
                continue
            
            # Find all matches
            for regex_match in compiled_regex.finditer(text):
                value = regex_match.group(0)
                start = regex_match.start()
                end = regex_match.end()
                
                # Validate if required
                is_valid = True
                if pattern_def.requires_validation and self.enable_strict_validation:
                    is_valid = self._validate_match(value, pattern_def.pii_type)
                
                if not is_valid:
                    continue
                
                # Calculate confidence
                confidence = self._calculate_confidence(
                    text, value, start, end,
                    pattern_def.pii_type,
                    pattern_def.confidence,
                    is_valid
                )
                
                # Get masking strategy and mask
                strategy = self.masking_config.get_strategy(pattern_def.pii_type)
                masked_value = self.masker.mask(value, pattern_def.pii_type, strategy)
                
                matches.append(PIIMatch(
                    pii_type=pattern_def.pii_type.value,
                    value=value,
                    start=start,
                    end=end,
                    confidence=confidence,
                    masked_value=masked_value
                ))
        
        return matches
    
    def _detect_names(self, text: str) -> List[PIIMatch]:
        """
        Detect person names using heuristic algorithms
        Looks for capitalized word sequences with name indicators
        """
        matches = []
        words = text.split()
        i = 0
        
        while i < len(words):
            word = words[i].strip('.,!?;:()[]{}')
            word_lower = word.lower()
            
            # Check for name prefix
            if word_lower in NAME_PATTERNS.PREFIXES and i + 1 < len(words):
                name_parts, next_i = self._extract_name_sequence(
                    words, i, text
                )
                
                if name_parts and len(name_parts) >= 2:
                    full_name = ' '.join(name_parts)
                    start_pos = text.find(full_name)
                    
                    if start_pos != -1:
                        # Validate context if enabled
                        context_valid = True
                        if self.enable_context_validation:
                            context_valid = self.context_validator.is_likely_name_context(
                                text, start_pos, start_pos + len(full_name)
                            )
                        
                        confidence = 0.85 if context_valid else 0.70
                        masked = self.masker.mask(full_name, PIIType.PERSON_NAME)
                        
                        matches.append(PIIMatch(
                            pii_type=PIIType.PERSON_NAME.value,
                            value=full_name,
                            start=start_pos,
                            end=start_pos + len(full_name),
                            confidence=confidence,
                            masked_value=masked
                        ))
                
                i = next_i
                continue
            
            # Check for common first name followed by capitalized word
            if word_lower in NAME_PATTERNS.COMMON_FIRST_NAMES and i + 1 < len(words):
                next_word = words[i + 1].strip('.,!?;:()[]{}')
                
                if TextProcessor.is_capitalized_word(next_word) and len(next_word) > 2:
                    full_name = f"{words[i]} {words[i + 1]}"
                    start_pos = text.find(full_name)
                    
                    if start_pos != -1:
                        context_valid = True
                        if self.enable_context_validation:
                            context_valid = self.context_validator.is_likely_name_context(
                                text, start_pos, start_pos + len(full_name)
                            )
                        
                        confidence = 0.75 if context_valid else 0.60
                        masked = self.masker.mask(full_name, PIIType.PERSON_NAME)
                        
                        matches.append(PIIMatch(
                            pii_type=PIIType.PERSON_NAME.value,
                            value=full_name,
                            start=start_pos,
                            end=start_pos + len(full_name),
                            confidence=confidence,
                            masked_value=masked
                        ))
                
                i += 2
                continue
            
            i += 1
        
        return matches
    
    def _extract_name_sequence(
        self,
        words: List[str],
        start_idx: int,
        full_text: str
    ) -> tuple:
        """
        Extract a sequence of words that form a name
        
        Returns:
            Tuple of (name_parts, next_index)
        """
        name_parts = [words[start_idx]]
        i = start_idx + 1
        
        while i < len(words) and i < start_idx + 4:
            word = words[i].strip('.,!?;:()[]{}')
            word_lower = word.lower()
            
            # Check if it's a capitalized word or suffix
            if (TextProcessor.is_capitalized_word(word) or
                word_lower in NAME_PATTERNS.SUFFIXES):
                name_parts.append(words[i])
                i += 1
            else:
                break
        
        return name_parts, i
    
    def _detect_addresses(self, text: str) -> List[PIIMatch]:
        """Detect street addresses"""
        matches = []
        
        # Pattern: number + street name + street type
        street_types_pattern = '|'.join(ADDRESS_PATTERNS.STREET_TYPES)
        pattern = (r'\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:' +
                  street_types_pattern + r')\b')
        
        for match in re.finditer(pattern, text, re.IGNORECASE):
            address = match.group(0)
            start = match.start()
            end = match.end()
            
            # Validate context if enabled
            context_valid = True
            if self.enable_context_validation:
                context_valid = self.context_validator.is_likely_address_context(
                    text, start, end
                )
            
            confidence = 0.80 if context_valid else 0.65
            masked = self.masker.mask(address, PIIType.ADDRESS)
            
            matches.append(PIIMatch(
                pii_type=PIIType.ADDRESS.value,
                value=address,
                start=start,
                end=end,
                confidence=confidence,
                masked_value=masked
            ))
        
        return matches
    
    def _validate_match(self, value: str, pii_type: PIIType) -> bool:
        """Validate a detected PII value"""
        if pii_type == PIIType.CREDIT_CARD:
            return self.validator.validate_credit_card(value)
        elif pii_type == PIIType.SSN:
            return self.validator.validate_ssn(value)
        elif pii_type == PIIType.EMAIL:
            return self.validator.validate_email(value)
        elif pii_type == PIIType.PHONE:
            return self.validator.validate_phone(value)
        elif pii_type == PIIType.IP_ADDRESS:
            return self.validator.validate_ip_address(value)
        elif pii_type == PIIType.DATE_OF_BIRTH:
            return self.validator.validate_date_of_birth(value)
        elif pii_type == PIIType.PASSPORT:
            return self.validator.is_valid_passport(value)
        else:
            return True
    
    def _calculate_confidence(
        self,
        text: str,
        value: str,
        start: int,
        end: int,
        pii_type: PIIType,
        base_confidence: float,
        validation_passed: bool
    ) -> float:
        """Calculate final confidence score"""
        
        # Check context if enabled
        context_match = False
        if self.enable_context_validation:
            if pii_type == PIIType.PERSON_NAME:
                context_match = self.context_validator.is_likely_name_context(
                    text, start, end
                )
            elif pii_type == PIIType.ADDRESS:
                context_match = self.context_validator.is_likely_address_context(
                    text, start, end
                )
        
        # Check if length is appropriate
        length_appropriate = True
        if pii_type == PIIType.CREDIT_CARD:
            clean_value = re.sub(r'[\s\-]', '', value)
            length_appropriate = 13 <= len(clean_value) <= 19
        elif pii_type == PIIType.SSN:
            clean_value = re.sub(r'[\s\-]', '', value)
            length_appropriate = len(clean_value) == 9
        
        return ConfidenceCalculator.adjust_confidence(
            base_confidence,
            context_match,
            validation_passed,
            length_appropriate
        )
    
    def mask_text(
        self,
        text: str,
        matches: Optional[List[PIIMatch]] = None,
        confidence_threshold: float = 0.7
    ) -> str:
        """
        Mask PII in text
        
        Args:
            text: Original text
            matches: Optional pre-detected matches (will detect if None)
            confidence_threshold: Threshold if detecting
            
        Returns:
            Text with PII masked
        """
        if matches is None:
            matches = self.detect_all(text, confidence_threshold)
        
        if not matches:
            return text
        
        # Sort matches by start position in reverse order
        sorted_matches = sorted(matches, key=lambda x: x.start, reverse=True)
        
        result = text
        for match in sorted_matches:
            result = (result[:match.start] +
                     match.masked_value +
                     result[match.end:])
        
        return result
    
    def get_statistics(self) -> Optional[dict]:
        """Get detection statistics"""
        if self.statistics:
            return self.statistics.get_stats()
        return None
    
    def reset_statistics(self):
        """Reset statistics"""
        if self.statistics:
            self.statistics.reset()
    
    def set_masking_strategy(
        self,
        pii_type: PIIType,
        strategy: MaskingStrategy
    ):
        """Set masking strategy for a PII type"""
        self.masking_config.set_strategy(pii_type, strategy)
    
    def set_all_masking_strategies(self, strategy: MaskingStrategy):
        """Set same masking strategy for all PII types"""
        self.masking_config.set_all_strategies(strategy)
