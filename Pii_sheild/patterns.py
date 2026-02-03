"""
PII Pattern Definitions
Centralized repository for all PII detection patterns and types
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Pattern


class PIIType(Enum):
    """Enumeration of all supported PII types"""
    CREDIT_CARD = "CREDIT_CARD"
    SSN = "SSN"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    PERSON_NAME = "PERSON_NAME"
    ADDRESS = "ADDRESS"
    IP_ADDRESS = "IP_ADDRESS"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    PASSPORT = "PASSPORT"
    DRIVER_LICENSE = "DRIVER_LICENSE"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    TAX_ID = "TAX_ID"


@dataclass
class PIIPattern:
    """Definition of a PII pattern with metadata"""
    pii_type: PIIType
    pattern: str
    confidence: float
    description: str
    requires_validation: bool = False


class PatternRegistry:
    """Central registry for all PII detection patterns"""
    
    def __init__(self):
        self._patterns = self._initialize_patterns()
        
    def _initialize_patterns(self) -> List[PIIPattern]:
        """Initialize all PII patterns"""
        return [
            # Credit Card Patterns
            PIIPattern(
                pii_type=PIIType.CREDIT_CARD,
                pattern=r'\b4\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
                confidence=0.95,
                description="Visa credit card",
                requires_validation=True
            ),
            PIIPattern(
                pii_type=PIIType.CREDIT_CARD,
                pattern=r'\b5[1-5]\d{2}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
                confidence=0.95,
                description="Mastercard",
                requires_validation=True
            ),
            PIIPattern(
                pii_type=PIIType.CREDIT_CARD,
                pattern=r'\b3[47]\d{2}[\s\-]?\d{6}[\s\-]?\d{5}\b',
                confidence=0.95,
                description="American Express",
                requires_validation=True
            ),
            PIIPattern(
                pii_type=PIIType.CREDIT_CARD,
                pattern=r'\b6(?:011|5\d{2})[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
                confidence=0.95,
                description="Discover card",
                requires_validation=True
            ),
            
            # SSN Patterns
            PIIPattern(
                pii_type=PIIType.SSN,
                pattern=r'\b(?!000|666|9\d{2})\d{3}[\s\-]?(?!00)\d{2}[\s\-]?(?!0000)\d{4}\b',
                confidence=0.98,
                description="Social Security Number with separators",
                requires_validation=True
            ),
            PIIPattern(
                pii_type=PIIType.SSN,
                pattern=r'\b(?!000|666|9\d{2})\d{3}(?!00)\d{2}(?!0000)\d{4}\b',
                confidence=0.98,
                description="Social Security Number without separators",
                requires_validation=True
            ),
            
            # Email Pattern
            PIIPattern(
                pii_type=PIIType.EMAIL,
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                confidence=0.99,
                description="Email address",
                requires_validation=False
            ),
            
            # Phone Patterns
            PIIPattern(
                pii_type=PIIType.PHONE,
                pattern=r'\b(?:\+?1[\s\-]?)?\(?([0-9]{3})\)?[\s\-]?([0-9]{3})[\s\-]?([0-9]{4})\b',
                confidence=0.85,
                description="US phone number",
                requires_validation=False
            ),
            PIIPattern(
                pii_type=PIIType.PHONE,
                pattern=r'\b(?:\+\d{1,3}[\s\-]?)?\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}\b',
                confidence=0.80,
                description="International phone number",
                requires_validation=False
            ),
            
            # IP Address Pattern
            PIIPattern(
                pii_type=PIIType.IP_ADDRESS,
                pattern=r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                confidence=0.90,
                description="IPv4 address",
                requires_validation=False
            ),
            
            # Date of Birth Patterns
            PIIPattern(
                pii_type=PIIType.DATE_OF_BIRTH,
                pattern=r'\b(?:0[1-9]|1[0-2])[/\-](?:0[1-9]|[12][0-9]|3[01])[/\-](?:19|20)\d{2}\b',
                confidence=0.75,
                description="Date of birth MM/DD/YYYY",
                requires_validation=False
            ),
            PIIPattern(
                pii_type=PIIType.DATE_OF_BIRTH,
                pattern=r'\b(?:0[1-9]|[12][0-9]|3[01])[/\-](?:0[1-9]|1[0-2])[/\-](?:19|20)\d{2}\b',
                confidence=0.75,
                description="Date of birth DD/MM/YYYY",
                requires_validation=False
            ),
            
            # Passport Pattern
            PIIPattern(
                pii_type=PIIType.PASSPORT,
                pattern=r'\b[A-Z]{1,2}\d{6,9}\b',
                confidence=0.70,
                description="US Passport number",
                requires_validation=False
            ),
            
            # Driver License Patterns
            PIIPattern(
                pii_type=PIIType.DRIVER_LICENSE,
                pattern=r'\b[A-Z]\d{7,8}\b',
                confidence=0.65,
                description="Driver license (CA, TX, etc.)",
                requires_validation=False
            ),
            PIIPattern(
                pii_type=PIIType.DRIVER_LICENSE,
                pattern=r'\b\d{9}\b',
                confidence=0.60,
                description="Driver license (FL, etc.)",
                requires_validation=False
            ),
            
            # Bank Account Pattern
            PIIPattern(
                pii_type=PIIType.BANK_ACCOUNT,
                pattern=r'\b\d{8,17}\b',
                confidence=0.50,
                description="Bank account number",
                requires_validation=False
            ),
            
            # Tax ID Pattern
            PIIPattern(
                pii_type=PIIType.TAX_ID,
                pattern=r'\b\d{2}[\-]?\d{7}\b',
                confidence=0.75,
                description="Tax identification number",
                requires_validation=False
            ),
        ]
    
    def get_patterns(self, pii_type: PIIType = None) -> List[PIIPattern]:
        """
        Get patterns, optionally filtered by type
        
        Args:
            pii_type: Optional PII type to filter by
            
        Returns:
            List of PIIPattern objects
        """
        if pii_type:
            return [p for p in self._patterns if p.pii_type == pii_type]
        return self._patterns
    
    def get_compiled_patterns(self, pii_type: PIIType = None) -> List[tuple]:
        """
        Get compiled regex patterns for efficient matching
        
        Args:
            pii_type: Optional PII type to filter by
            
        Returns:
            List of tuples (PIIPattern, compiled_regex)
        """
        patterns = self.get_patterns(pii_type)
        return [(p, re.compile(p.pattern)) for p in patterns]


class NamePatterns:
    """Specialized patterns and data for name detection"""
    
    # Common name prefixes
    PREFIXES = {
        'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'rev',
        'hon', 'sir', 'lord', 'lady', 'capt', 'col', 'gen',
        'lt', 'sgt', 'cpl', 'pvt', 'adm', 'cmdr', 'maj'
    }
    
    # Common name suffixes
    SUFFIXES = {
        'jr', 'sr', 'ii', 'iii', 'iv', 'v', 'esq', 'md', 'phd',
        'dds', 'jd', 'cpa', 'rn', 'dvm', 'do', 'od', 'pharmd'
    }
    
    # Common first names (extended set for better detection)
    COMMON_FIRST_NAMES = {
        # Male names
        'james', 'john', 'robert', 'michael', 'william', 'david',
        'richard', 'joseph', 'thomas', 'charles', 'christopher', 'daniel',
        'matthew', 'anthony', 'mark', 'donald', 'steven', 'paul',
        'andrew', 'joshua', 'kenneth', 'kevin', 'brian', 'george',
        'edward', 'ronald', 'timothy', 'jason', 'jeffrey', 'ryan',
        # Female names
        'mary', 'patricia', 'jennifer', 'linda', 'barbara', 'elizabeth',
        'susan', 'jessica', 'sarah', 'karen', 'nancy', 'lisa',
        'betty', 'margaret', 'sandra', 'ashley', 'kimberly', 'emily',
        'donna', 'michelle', 'dorothy', 'carol', 'amanda', 'melissa',
        'deborah', 'stephanie', 'rebecca', 'sharon', 'laura', 'cynthia',
        'kathleen', 'amy', 'angela', 'shirley', 'anna', 'brenda',
        'pamela', 'emma', 'nicole', 'helen', 'samantha', 'katherine',
    }


class AddressPatterns:
    """Specialized patterns and data for address detection"""
    
    # Street type suffixes
    STREET_TYPES = {
        'street', 'st', 'avenue', 'ave', 'road', 'rd', 'boulevard',
        'blvd', 'lane', 'ln', 'drive', 'dr', 'court', 'ct', 'circle',
        'cir', 'way', 'place', 'pl', 'terrace', 'ter', 'parkway', 'pkwy',
        'highway', 'hwy', 'trail', 'path', 'alley', 'walk', 'plaza',
        'square', 'loop', 'crescent', 'creek', 'crossing', 'bend'
    }
    
    # US state names and abbreviations
    US_STATES = {
        'alabama', 'al', 'alaska', 'ak', 'arizona', 'az', 'arkansas', 'ar',
        'california', 'ca', 'colorado', 'co', 'connecticut', 'ct',
        'delaware', 'de', 'florida', 'fl', 'georgia', 'ga',
        'hawaii', 'hi', 'idaho', 'id', 'illinois', 'il', 'indiana', 'in',
        'iowa', 'ia', 'kansas', 'ks', 'kentucky', 'ky', 'louisiana', 'la',
        'maine', 'me', 'maryland', 'md', 'massachusetts', 'ma',
        'michigan', 'mi', 'minnesota', 'mn', 'mississippi', 'ms',
        'missouri', 'mo', 'montana', 'mt', 'nebraska', 'ne', 'nevada', 'nv',
        'hampshire', 'nh', 'jersey', 'nj', 'mexico', 'nm', 'york', 'ny',
        'carolina', 'nc', 'dakota', 'nd', 'ohio', 'oh', 'oklahoma', 'ok',
        'oregon', 'or', 'pennsylvania', 'pa', 'rhode', 'ri',
        'tennessee', 'tn', 'texas', 'tx', 'utah', 'ut', 'vermont', 'vt',
        'virginia', 'va', 'washington', 'wa', 'wisconsin', 'wi',
        'wyoming', 'wy'
    }
    
    # Directional prefixes
    DIRECTIONALS = {'n', 'north', 's', 'south', 'e', 'east', 'w', 'west',
                   'ne', 'nw', 'se', 'sw', 'northeast', 'northwest',
                   'southeast', 'southwest'}


# Singleton instances
PATTERN_REGISTRY = PatternRegistry()
NAME_PATTERNS = NamePatterns()
ADDRESS_PATTERNS = AddressPatterns()
