"""
PII Masking Module
Different strategies for masking detected PII
"""

import hashlib
import re
from enum import Enum
from typing import Optional
from .patterns import PIIType


class MaskingStrategy(Enum):
    """Available masking strategies"""
    FULL = "FULL"  # Replace entirely with placeholder
    PARTIAL = "PARTIAL"  # Show partial information (e.g., last 4 digits)
    REDACT = "REDACT"  # Replace with asterisks
    HASH = "HASH"  # Replace with hash value
    TOKENIZE = "TOKENIZE"  # Replace with token


class PIIMasker:
    """Handles masking of detected PII using various strategies"""
    
    def __init__(self, default_strategy: MaskingStrategy = MaskingStrategy.PARTIAL):
        """
        Initialize masker
        
        Args:
            default_strategy: Default masking strategy to use
        """
        self.default_strategy = default_strategy
        self._token_counter = 0
    
    def mask(
        self,
        value: str,
        pii_type: PIIType,
        strategy: Optional[MaskingStrategy] = None
    ) -> str:
        """
        Mask a PII value
        
        Args:
            value: Original PII value
            pii_type: Type of PII
            strategy: Masking strategy (uses default if None)
            
        Returns:
            Masked value
        """
        strategy = strategy or self.default_strategy
        
        # Route to appropriate masking method
        if strategy == MaskingStrategy.FULL:
            return self._mask_full(value, pii_type)
        elif strategy == MaskingStrategy.PARTIAL:
            return self._mask_partial(value, pii_type)
        elif strategy == MaskingStrategy.REDACT:
            return self._mask_redact(value)
        elif strategy == MaskingStrategy.HASH:
            return self._mask_hash(value, pii_type)
        elif strategy == MaskingStrategy.TOKENIZE:
            return self._mask_tokenize(value, pii_type)
        else:
            return self._mask_partial(value, pii_type)
    
    def _mask_full(self, value: str, pii_type: PIIType) -> str:
        """Replace entirely with placeholder"""
        placeholders = {
            PIIType.CREDIT_CARD: "[CREDIT_CARD]",
            PIIType.SSN: "[SSN]",
            PIIType.EMAIL: "[EMAIL]",
            PIIType.PHONE: "[PHONE]",
            PIIType.PERSON_NAME: "[NAME]",
            PIIType.ADDRESS: "[ADDRESS]",
            PIIType.IP_ADDRESS: "[IP_ADDRESS]",
            PIIType.DATE_OF_BIRTH: "[DATE_OF_BIRTH]",
            PIIType.PASSPORT: "[PASSPORT]",
            PIIType.DRIVER_LICENSE: "[DRIVER_LICENSE]",
            PIIType.BANK_ACCOUNT: "[BANK_ACCOUNT]",
            PIIType.TAX_ID: "[TAX_ID]",
        }
        return placeholders.get(pii_type, "[PII]")
    
    def _mask_partial(self, value: str, pii_type: PIIType) -> str:
        """Show partial information based on PII type"""
        
        if pii_type == PIIType.CREDIT_CARD:
            return self._mask_credit_card(value)
        elif pii_type == PIIType.SSN:
            return self._mask_ssn(value)
        elif pii_type == PIIType.EMAIL:
            return self._mask_email(value)
        elif pii_type == PIIType.PHONE:
            return self._mask_phone(value)
        elif pii_type == PIIType.PERSON_NAME:
            return self._mask_name(value)
        elif pii_type == PIIType.BANK_ACCOUNT:
            return self._mask_bank_account(value)
        else:
            return self._mask_full(value, pii_type)
    
    def _mask_redact(self, value: str) -> str:
        """Replace with asterisks"""
        return "*" * len(value)
    
    def _mask_hash(self, value: str, pii_type: PIIType) -> str:
        """Replace with hash value"""
        hash_value = hashlib.sha256(value.encode()).hexdigest()[:12]
        return f"[{pii_type.value}:{hash_value}]"
    
    def _mask_tokenize(self, value: str, pii_type: PIIType) -> str:
        """Replace with unique token"""
        self._token_counter += 1
        return f"[{pii_type.value}_TOKEN_{self._token_counter:04d}]"
    
    # Specific masking methods for each PII type
    
    def _mask_credit_card(self, card: str) -> str:
        """Mask credit card showing only last 4 digits"""
        clean = re.sub(r'[\s\-]', '', card)
        if len(clean) < 4:
            return "****"
        return "****-****-****-" + clean[-4:]
    
    def _mask_ssn(self, ssn: str) -> str:
        """Mask SSN showing only last 4 digits"""
        clean = re.sub(r'[\s\-]', '', ssn)
        if len(clean) < 4:
            return "***-**-****"
        return "***-**-" + clean[-4:]
    
    def _mask_email(self, email: str) -> str:
        """Mask email preserving domain"""
        parts = email.split('@')
        if len(parts) != 2:
            return "[EMAIL]"
        
        username = parts[0]
        domain = parts[1]
        
        if len(username) <= 2:
            masked_user = "***"
        elif len(username) <= 4:
            masked_user = username[0] + "***"
        else:
            masked_user = username[0] + "***" + username[-1]
        
        return f"{masked_user}@{domain}"
    
    def _mask_phone(self, phone: str) -> str:
        """Mask phone showing only last 4 digits"""
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) < 4:
            return "[PHONE]"
        return "***-***-" + digits[-4:]
    
    def _mask_name(self, name: str) -> str:
        """Mask name showing only first initial of each word"""
        parts = name.split()
        if len(parts) == 0:
            return "[NAME]"
        
        masked_parts = []
        for part in parts:
            if len(part) > 0:
                if part.lower() in ['mr', 'mrs', 'ms', 'dr', 'prof']:
                    # Keep titles as-is
                    masked_parts.append(part[0].upper() + "***")
                else:
                    masked_parts.append(part[0].upper() + "***")
            
        return ' '.join(masked_parts)
    
    def _mask_bank_account(self, account: str) -> str:
        """Mask bank account showing only last 4 digits"""
        clean = ''.join(c for c in account if c.isdigit())
        if len(clean) < 4:
            return "****"
        return "****" + clean[-4:]
    
    def _mask_address(self, address: str) -> str:
        """Mask address showing only street type"""
        # Extract street type if present
        words = address.lower().split()
        street_types = {'street', 'st', 'avenue', 'ave', 'road', 'rd', 
                       'boulevard', 'blvd', 'lane', 'ln', 'drive', 'dr'}
        
        for word in words:
            if word.rstrip('.,') in street_types:
                return f"[ADDRESS on {word.title()}]"
        
        return "[ADDRESS]"


class ReversibleMasker:
    """
    Masker that can reverse masking (for testing/debugging only)
    WARNING: Do not use in production for actual PII protection
    """
    
    def __init__(self):
        self._mapping = {}
        self._counter = 0
    
    def mask(self, value: str, pii_type: PIIType) -> str:
        """
        Mask value and store mapping
        
        Args:
            value: Original value
            pii_type: PII type
            
        Returns:
            Masked token
        """
        self._counter += 1
        token = f"[{pii_type.value}_{self._counter:04d}]"
        self._mapping[token] = value
        return token
    
    def unmask(self, token: str) -> Optional[str]:
        """
        Unmask a token
        
        Args:
            token: Masked token
            
        Returns:
            Original value or None if not found
        """
        return self._mapping.get(token)
    
    def unmask_text(self, text: str) -> str:
        """
        Unmask all tokens in text
        
        Args:
            text: Text with masked tokens
            
        Returns:
            Text with original values restored
        """
        result = text
        for token, original in self._mapping.items():
            result = result.replace(token, original)
        return result
    
    def clear_mapping(self):
        """Clear the mapping (for security)"""
        self._mapping.clear()
        self._counter = 0


class MaskingConfig:
    """Configuration for masking behavior"""
    
    def __init__(self):
        self.strategies = {
            PIIType.CREDIT_CARD: MaskingStrategy.PARTIAL,
            PIIType.SSN: MaskingStrategy.PARTIAL,
            PIIType.EMAIL: MaskingStrategy.PARTIAL,
            PIIType.PHONE: MaskingStrategy.PARTIAL,
            PIIType.PERSON_NAME: MaskingStrategy.PARTIAL,
            PIIType.ADDRESS: MaskingStrategy.FULL,
            PIIType.IP_ADDRESS: MaskingStrategy.FULL,
            PIIType.DATE_OF_BIRTH: MaskingStrategy.FULL,
            PIIType.PASSPORT: MaskingStrategy.FULL,
            PIIType.DRIVER_LICENSE: MaskingStrategy.FULL,
            PIIType.BANK_ACCOUNT: MaskingStrategy.PARTIAL,
            PIIType.TAX_ID: MaskingStrategy.FULL,
        }
    
    def get_strategy(self, pii_type: PIIType) -> MaskingStrategy:
        """Get masking strategy for PII type"""
        return self.strategies.get(pii_type, MaskingStrategy.FULL)
    
    def set_strategy(self, pii_type: PIIType, strategy: MaskingStrategy):
        """Set masking strategy for PII type"""
        self.strategies[pii_type] = strategy
    
    def set_all_strategies(self, strategy: MaskingStrategy):
        """Set same strategy for all PII types"""
        for pii_type in PIIType:
            self.strategies[pii_type] = strategy
