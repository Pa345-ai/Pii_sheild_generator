"""
PII Masking Tests
Comprehensive tests for PII masking functionality
"""

import pytest
from pii_shield.masking import (
    PIIMasker, MaskingStrategy, MaskingConfig, ReversibleMasker
)
from pii_shield.patterns import PIIType


class TestPIIMasker:
    """Test main PIIMasker class"""
    
    def setup_method(self):
        self.masker = PIIMasker()
    
    def test_default_strategy(self):
        """Test default masking strategy"""
        assert self.masker.default_strategy == MaskingStrategy.PARTIAL
    
    def test_mask_with_full_strategy(self):
        """Test full masking strategy"""
        value = "john@example.com"
        result = self.masker.mask(value, PIIType.EMAIL, MaskingStrategy.FULL)
        assert result == "[EMAIL]"
    
    def test_mask_with_partial_strategy(self):
        """Test partial masking strategy"""
        value = "john@example.com"
        result = self.masker.mask(value, PIIType.EMAIL, MaskingStrategy.PARTIAL)
        assert "@example.com" in result
        assert "john" not in result
    
    def test_mask_with_redact_strategy(self):
        """Test redact masking strategy"""
        value = "sensitive"
        result = self.masker.mask(value, PIIType.EMAIL, MaskingStrategy.REDACT)
        assert result == "*" * len(value)
    
    def test_mask_with_hash_strategy(self):
        """Test hash masking strategy"""
        value = "test@example.com"
        result = self.masker.mask(value, PIIType.EMAIL, MaskingStrategy.HASH)
        assert result.startswith("[EMAIL:")
        assert result.endswith("]")
    
    def test_mask_with_tokenize_strategy(self):
        """Test tokenize masking strategy"""
        value = "test@example.com"
        result = self.masker.mask(value, PIIType.EMAIL, MaskingStrategy.TOKENIZE)
        assert "EMAIL_TOKEN" in result


class TestCreditCardMasking:
    """Test credit card specific masking"""
    
    def setup_method(self):
        self.masker = PIIMasker()
    
    def test_mask_credit_card_with_dashes(self):
        """Test masking credit card with dashes"""
        card = "4532-1488-0343-6467"
        result = self.masker._mask_credit_card(card)
        assert result == "****-****-****-6467"
    
    def test_mask_credit_card_with_spaces(self):
        """Test masking credit card with spaces"""
        card = "5425 2334 3010 9903"
        result = self.masker._mask_credit_card(card)
        assert result == "****-****-****-9903"
    
    def test_mask_credit_card_no_separator(self):
        """Test masking credit card without separators"""
        card = "378282246310005"
        result = self.masker._mask_credit_card(card)
        assert result == "****-****-****-0005"
    
    def test_mask_short_card(self):
        """Test masking short card number"""
        card = "123"
        result = self.masker._mask_credit_card(card)
        assert result == "****"


class TestSSNMasking:
    """Test SSN specific masking"""
    
    def setup_method(self):
        self.masker = PIIMasker()
    
    def test_mask_ssn_with_dashes(self):
        """Test masking SSN with dashes"""
        ssn = "123-45-6789"
        result = self.masker._mask_ssn(ssn)
        assert result == "***-**-6789"
    
    def test_mask_ssn_without_dashes(self):
        """Test masking SSN without dashes"""
        ssn = "123456789"
        result = self.masker._mask_ssn(ssn)
        assert result == "***-**-6789"
    
    def test_mask_short_ssn(self):
        """Test masking short SSN"""
        ssn = "12"
        result = self.masker._mask_ssn(ssn)
        assert result == "***-**-****"


class TestEmailMasking:
    """Test email specific masking"""
    
    def setup_method(self):
        self.masker = PIIMasker()
    
    def test_mask_simple_email(self):
        """Test masking simple email"""
        email = "john@example.com"
        result = self.masker._mask_email(email)
        assert "@example.com" in result
        assert result.startswith("j***")
    
    def test_mask_short_email(self):
        """Test masking short email"""
        email = "ab@test.com"
        result = self.masker._mask_email(email)
        assert "***@test.com" in result
    
    def test_mask_long_email(self):
        """Test masking long email"""
        email = "verylongemail@example.com"
        result = self.masker._mask_email(email)
        assert result.startswith("v***")
        assert result.endswith("l@example.com")
    
    def test_mask_invalid_email(self):
        """Test masking invalid email"""
        email = "notanemail"
        result = self.masker._mask_email(email)
        assert result == "[EMAIL]"


class TestPhoneMasking:
    """Test phone specific masking"""
    
    def setup_method(self):
        self.masker = PIIMasker()
    
    def test_mask_phone_10_digits(self):
        """Test masking 10-digit phone"""
        phone = "(555) 123-4567"
        result = self.masker._mask_phone(phone)
        assert result == "***-***-4567"
    
    def test_mask_phone_11_digits(self):
        """Test masking 11-digit phone"""
        phone = "1-555-123-4567"
        result = self.masker._mask_phone(phone)
        assert result == "***-***-4567"
    
    def test_mask_phone_no_format(self):
        """Test masking phone without formatting"""
        phone = "5551234567"
        result = self.masker._mask_phone(phone)
        assert result == "***-***-4567"
    
    def test_mask_short_phone(self):
        """Test masking short phone"""
        phone = "123"
        result = self.masker._mask_phone(phone)
        assert result == "[PHONE]"


class TestNameMasking:
    """Test name specific masking"""
    
    def setup_method(self):
        self.masker = PIIMasker()
    
    def test_mask_simple_name(self):
        """Test masking simple name"""
        name = "John Smith"
        result = self.masker._mask_name(name)
        assert result == "J*** S***"
    
    def test_mask_name_with_prefix(self):
        """Test masking name with prefix"""
        name = "Dr. Sarah Johnson"
        result = self.masker._mask_name(name)
        assert "D***" in result
        assert "S***" in result
        assert "J***" in result
    
    def test_mask_single_name(self):
        """Test masking single name"""
        name = "John"
        result = self.masker._mask_name(name)
        assert result == "J***"
    
    def test_mask_empty_name(self):
        """Test masking empty name"""
        name = ""
        result = self.masker._mask_name(name)
        assert result == "[NAME]"


class TestBankAccountMasking:
    """Test bank account masking"""
    
    def setup_method(self):
        self.masker = PIIMasker()
    
    def test_mask_bank_account(self):
        """Test masking bank account"""
        account = "1234567890"
        result = self.masker._mask_bank_account(account)
        assert result == "****7890"
    
    def test_mask_short_account(self):
        """Test masking short account"""
        account = "123"
        result = self.masker._mask_bank_account(account)
        assert result == "****"


class TestMaskingConfig:
    """Test masking configuration"""
    
    def test_default_strategies(self):
        """Test default masking strategies"""
        config = MaskingConfig()
        
        assert config.get_strategy(PIIType.CREDIT_CARD) == MaskingStrategy.PARTIAL
        assert config.get_strategy(PIIType.SSN) == MaskingStrategy.PARTIAL
        assert config.get_strategy(PIIType.EMAIL) == MaskingStrategy.PARTIAL
        assert config.get_strategy(PIIType.ADDRESS) == MaskingStrategy.FULL
    
    def test_set_strategy(self):
        """Test setting custom strategy"""
        config = MaskingConfig()
        config.set_strategy(PIIType.EMAIL, MaskingStrategy.FULL)
        
        assert config.get_strategy(PIIType.EMAIL) == MaskingStrategy.FULL
    
    def test_set_all_strategies(self):
        """Test setting all strategies at once"""
        config = MaskingConfig()
        config.set_all_strategies(MaskingStrategy.HASH)
        
        assert config.get_strategy(PIIType.EMAIL) == MaskingStrategy.HASH
        assert config.get_strategy(PIIType.CREDIT_CARD) == MaskingStrategy.HASH
        assert config.get_strategy(PIIType.SSN) == MaskingStrategy.HASH


class TestReversibleMasker:
    """Test reversible masker (for testing/debugging)"""
    
    def setup_method(self):
        self.masker = ReversibleMasker()
    
    def test_mask_and_unmask(self):
        """Test masking and unmasking"""
        original = "test@example.com"
        token = self.masker.mask(original, PIIType.EMAIL)
        
        assert token != original
        assert "EMAIL" in token
        
        unmasked = self.masker.unmask(token)
        assert unmasked == original
    
    def test_unmask_text(self):
        """Test unmasking entire text"""
        original_text = "Email: test@example.com, Phone: 555-1234"
        
        email_token = self.masker.mask("test@example.com", PIIType.EMAIL)
        phone_token = self.masker.mask("555-1234", PIIType.PHONE)
        
        masked_text = f"Email: {email_token}, Phone: {phone_token}"
        
        unmasked_text = self.masker.unmask_text(masked_text)
        assert unmasked_text == original_text
    
    def test_clear_mapping(self):
        """Test clearing mapping"""
        token = self.masker.mask("test@example.com", PIIType.EMAIL)
        self.masker.clear_mapping()
        
        unmasked = self.masker.unmask(token)
        assert unmasked is None
    
    def test_unmask_unknown_token(self):
        """Test unmasking unknown token"""
        result = self.masker.unmask("[UNKNOWN_TOKEN]")
        assert result is None


class TestMaskingStrategiesIntegration:
    """Integration tests for different masking strategies"""
    
    def setup_method(self):
        self.masker = PIIMasker()
    
    def test_all_strategies_on_email(self):
        """Test all strategies on email"""
        email = "john.doe@example.com"
        
        full = self.masker.mask(email, PIIType.EMAIL, MaskingStrategy.FULL)
        assert full == "[EMAIL]"
        
        partial = self.masker.mask(email, PIIType.EMAIL, MaskingStrategy.PARTIAL)
        assert "@example.com" in partial
        
        redact = self.masker.mask(email, PIIType.EMAIL, MaskingStrategy.REDACT)
        assert all(c == '*' for c in redact)
        
        hash_result = self.masker.mask(email, PIIType.EMAIL, MaskingStrategy.HASH)
        assert hash_result.startswith("[EMAIL:")
        
        token = self.masker.mask(email, PIIType.EMAIL, MaskingStrategy.TOKENIZE)
        assert "EMAIL_TOKEN" in token
    
    def test_all_strategies_on_credit_card(self):
        """Test all strategies on credit card"""
        card = "4532-1488-0343-6467"
        
        full = self.masker.mask(card, PIIType.CREDIT_CARD, MaskingStrategy.FULL)
        assert full == "[CREDIT_CARD]"
        
        partial = self.masker.mask(card, PIIType.CREDIT_CARD, MaskingStrategy.PARTIAL)
        assert "6467" in partial
        
        redact = self.masker.mask(card, PIIType.CREDIT_CARD, MaskingStrategy.REDACT)
        assert all(c == '*' for c in redact)


class TestEdgeCases:
    """Test edge cases in masking"""
    
    def setup_method(self):
        self.masker = PIIMasker()
    
    def test_mask_empty_string(self):
        """Test masking empty string"""
        result = self.masker._mask_credit_card("")
        assert result == "****"
    
    def test_mask_special_characters(self):
        """Test masking with special characters"""
        email = "test+tag@example.com"
        result = self.masker._mask_email(email)
        assert "@example.com" in result
    
    def test_mask_unicode_name(self):
        """Test masking name with unicode characters"""
        name = "José García"
        result = self.masker._mask_name(name)
        assert "J***" in result
    
    def test_consecutive_masking(self):
        """Test consecutive masking operations"""
        masker = PIIMasker(MaskingStrategy.TOKENIZE)
        
        token1 = masker.mask("test1@example.com", PIIType.EMAIL)
        token2 = masker.mask("test2@example.com", PIIType.EMAIL)
        
        assert token1 != token2
        assert "EMAIL_TOKEN_0001" in token1
        assert "EMAIL_TOKEN_0002" in token2


class TestPerformance:
    """Test masking performance"""
    
    def setup_method(self):
        self.masker = PIIMasker()
    
    def test_masking_performance(self):
        """Test masking performance on large dataset"""
        import time
        
        emails = [f"user{i}@example.com" for i in range(1000)]
        
        start = time.time()
        for email in emails:
            self.masker.mask(email, PIIType.EMAIL, MaskingStrategy.PARTIAL)
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 0.1  # Less than 100ms for 1000 operations
    
    def test_hash_performance(self):
        """Test hash masking performance"""
        import time
        
        data = ["test@example.com"] * 100
        
        start = time.time()
        for item in data:
            self.masker.mask(item, PIIType.EMAIL, MaskingStrategy.HASH)
        elapsed = time.time() - start
        
        assert elapsed < 0.05  # Less than 50ms for 100 operations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
