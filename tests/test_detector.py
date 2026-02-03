"""
PII Detector Tests
Comprehensive tests for PII detection functionality
"""

import pytest
from pii_shield import PIIDetector
from pii_shield.patterns import PIIType


class TestCreditCardDetection:
    """Test credit card detection"""
    
    def setup_method(self):
        self.detector = PIIDetector()
    
    def test_visa_detection(self):
        text = "My Visa is 4532-1488-0343-6467"
        matches = self.detector.detect_all(text)
        cc_matches = [m for m in matches if m.pii_type == PIIType.CREDIT_CARD.value]
        assert len(cc_matches) > 0
        assert "4532" in cc_matches[0].value
    
    def test_mastercard_detection(self):
        text = "Mastercard: 5425 2334 3010 9903"
        matches = self.detector.detect_all(text)
        cc_matches = [m for m in matches if m.pii_type == PIIType.CREDIT_CARD.value]
        assert len(cc_matches) > 0
    
    def test_amex_detection(self):
        text = "Amex: 3782 822463 10005"
        matches = self.detector.detect_all(text)
        cc_matches = [m for m in matches if m.pii_type == PIIType.CREDIT_CARD.value]
        assert len(cc_matches) > 0
    
    def test_invalid_luhn_rejected(self):
        text = "Card: 4532-1488-0343-6468"  # Invalid Luhn
        matches = self.detector.detect_all(text)
        cc_matches = [m for m in matches if m.pii_type == PIIType.CREDIT_CARD.value]
        assert len(cc_matches) == 0


class TestSSNDetection:
    """Test SSN detection"""
    
    def setup_method(self):
        self.detector = PIIDetector()
    
    def test_ssn_with_dashes(self):
        text = "SSN: 123-45-6789"
        matches = self.detector.detect_all(text)
        ssn_matches = [m for m in matches if m.pii_type == PIIType.SSN.value]
        assert len(ssn_matches) > 0
    
    def test_ssn_without_dashes(self):
        text = "My SSN is 856432190"
        matches = self.detector.detect_all(text)
        ssn_matches = [m for m in matches if m.pii_type == PIIType.SSN.value]
        assert len(ssn_matches) > 0
    
    def test_invalid_ssn_area_000(self):
        text = "SSN: 000-12-3456"
        matches = self.detector.detect_all(text)
        ssn_matches = [m for m in matches if m.pii_type == PIIType.SSN.value]
        assert len(ssn_matches) == 0
    
    def test_invalid_ssn_area_666(self):
        text = "SSN: 666-12-3456"
        matches = self.detector.detect_all(text)
        ssn_matches = [m for m in matches if m.pii_type == PIIType.SSN.value]
        assert len(ssn_matches) == 0


class TestEmailDetection:
    """Test email detection"""
    
    def setup_method(self):
        self.detector = PIIDetector()
    
    def test_simple_email(self):
        text = "Contact me at john@example.com"
        matches = self.detector.detect_all(text)
        email_matches = [m for m in matches if m.pii_type == PIIType.EMAIL.value]
        assert len(email_matches) > 0
        assert "john@example.com" in email_matches[0].value
    
    def test_email_with_dots(self):
        text = "Email: john.doe@company.co.uk"
        matches = self.detector.detect_all(text)
        email_matches = [m for m in matches if m.pii_type == PIIType.EMAIL.value]
        assert len(email_matches) > 0
    
    def test_email_with_numbers(self):
        text = "user123@test.io"
        matches = self.detector.detect_all(text)
        email_matches = [m for m in matches if m.pii_type == PIIType.EMAIL.value]
        assert len(email_matches) > 0


class TestPhoneDetection:
    """Test phone number detection"""
    
    def setup_method(self):
        self.detector = PIIDetector()
    
    def test_phone_with_parentheses(self):
        text = "Call me at (555) 123-4567"
        matches = self.detector.detect_all(text)
        phone_matches = [m for m in matches if m.pii_type == PIIType.PHONE.value]
        assert len(phone_matches) > 0
    
    def test_phone_with_dashes(self):
        text = "Phone: 555-987-6543"
        matches = self.detector.detect_all(text)
        phone_matches = [m for m in matches if m.pii_type == PIIType.PHONE.value]
        assert len(phone_matches) > 0
    
    def test_international_phone(self):
        text = "Mobile: +1-555-246-8135"
        matches = self.detector.detect_all(text)
        phone_matches = [m for m in matches if m.pii_type == PIIType.PHONE.value]
        assert len(phone_matches) > 0


class TestNameDetection:
    """Test person name detection"""
    
    def setup_method(self):
        self.detector = PIIDetector()
    
    def test_name_with_prefix(self):
        text = "Dr. John Smith will see you now"
        matches = self.detector.detect_all(text)
        name_matches = [m for m in matches if m.pii_type == PIIType.PERSON_NAME.value]
        assert len(name_matches) > 0
    
    def test_common_first_name(self):
        text = "Contact Sarah Williams for details"
        matches = self.detector.detect_all(text)
        name_matches = [m for m in matches if m.pii_type == PIIType.PERSON_NAME.value]
        assert len(name_matches) > 0


class TestMasking:
    """Test PII masking functionality"""
    
    def setup_method(self):
        self.detector = PIIDetector()
    
    def test_mask_credit_card(self):
        text = "Card: 4532-1488-0343-6467"
        matches = self.detector.detect_all(text)
        masked = self.detector.mask_text(text, matches)
        assert "6467" in masked
        assert "4532" not in masked
    
    def test_mask_ssn(self):
        text = "SSN: 123-45-6789"
        matches = self.detector.detect_all(text)
        masked = self.detector.mask_text(text, matches)
        assert "6789" in masked
        assert "123-45" not in masked
    
    def test_mask_email(self):
        text = "Email: john@example.com"
        matches = self.detector.detect_all(text)
        masked = self.detector.mask_text(text, matches)
        assert "example.com" in masked
        assert "john" not in masked


class TestComprehensive:
    """Test comprehensive detection scenarios"""
    
    def setup_method(self):
        self.detector = PIIDetector()
    
    def test_multiple_pii_types(self):
        text = """
        Contact Dr. Sarah Johnson at sarah.j@company.com
        Phone: (555) 234-5678
        SSN: 123-45-6789
        Card: 4532-1488-0343-6467
        """
        matches = self.detector.detect_all(text)
        assert len(matches) >= 4
    
    def test_overlapping_detections(self):
        text = "My number is 555-123-4567"
        matches = self.detector.detect_all(text)
        # Should not have duplicates
        positions = [(m.start, m.end) for m in matches]
        assert len(positions) == len(set(positions))
    
    def test_confidence_filtering(self):
        text = "Email: test@example.com"
        
        # High threshold
        high_matches = self.detector.detect_all(text, confidence_threshold=0.95)
        
        # Low threshold
        low_matches = self.detector.detect_all(text, confidence_threshold=0.5)
        
        assert len(low_matches) >= len(high_matches)
    
    def test_specific_pii_types(self):
        text = "Email: test@test.com, Phone: 555-1234, SSN: 123-45-6789"
        
        # Only detect emails
        matches = self.detector.detect_all(
            text,
            pii_types=[PIIType.EMAIL]
        )
        
        assert all(m.pii_type == PIIType.EMAIL.value for m in matches)


class TestPerformance:
    """Test performance characteristics"""
    
    def setup_method(self):
        self.detector = PIIDetector()
    
    def test_large_text(self):
        import time
        
        # Generate large text
        text = "Contact john@example.com. " * 1000
        
        start = time.time()
        matches = self.detector.detect_all(text)
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 1.0  # Less than 1 second
        assert len(matches) > 0
    
    def test_no_pii_performance(self):
        import time
        
        text = "The quick brown fox jumps over the lazy dog. " * 100
        
        start = time.time()
        matches = self.detector.detect_all(text)
        elapsed = time.time() - start
        
        assert len(matches) == 0
        assert elapsed < 0.1  # Very fast for no matches


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
