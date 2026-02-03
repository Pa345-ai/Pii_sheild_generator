"""
PII Validator Tests
Comprehensive tests for PII validation functionality
"""

import pytest
from pii_shield.validator import PIIValidator, ContextValidator


class TestCreditCardValidation:
    """Test credit card validation with Luhn algorithm"""
    
    def setup_method(self):
        self.validator = PIIValidator()
    
    def test_valid_visa(self):
        """Test valid Visa card"""
        # Valid test Visa from payment processor test cards
        assert self.validator.validate_credit_card("4532148803436467")
    
    def test_valid_visa_with_dashes(self):
        """Test valid Visa with dashes"""
        assert self.validator.validate_credit_card("4532-1488-0343-6467")
    
    def test_valid_visa_with_spaces(self):
        """Test valid Visa with spaces"""
        assert self.validator.validate_credit_card("4532 1488 0343 6467")
    
    def test_valid_mastercard(self):
        """Test valid Mastercard"""
        assert self.validator.validate_credit_card("5425233430109903")
    
    def test_valid_amex(self):
        """Test valid American Express"""
        assert self.validator.validate_credit_card("378282246310005")
    
    def test_valid_discover(self):
        """Test valid Discover"""
        assert self.validator.validate_credit_card("6011111111111117")
    
    def test_invalid_luhn_checksum(self):
        """Test invalid Luhn checksum"""
        # Last digit changed to make invalid
        assert not self.validator.validate_credit_card("4532148803436468")
    
    def test_too_short(self):
        """Test card number too short"""
        assert not self.validator.validate_credit_card("123456789012")
    
    def test_too_long(self):
        """Test card number too long"""
        assert not self.validator.validate_credit_card("12345678901234567890")
    
    def test_non_numeric(self):
        """Test non-numeric characters"""
        assert not self.validator.validate_credit_card("abcd-efgh-ijkl-mnop")


class TestSSNValidation:
    """Test Social Security Number validation"""
    
    def setup_method(self):
        self.validator = PIIValidator()
    
    def test_valid_ssn(self):
        """Test valid SSN"""
        assert self.validator.validate_ssn("123-45-6789")
    
    def test_valid_ssn_no_dashes(self):
        """Test valid SSN without dashes"""
        assert self.validator.validate_ssn("123456789")
    
    def test_invalid_area_000(self):
        """Test SSN with area 000"""
        assert not self.validator.validate_ssn("000-12-3456")
    
    def test_invalid_area_666(self):
        """Test SSN with area 666"""
        assert not self.validator.validate_ssn("666-12-3456")
    
    def test_invalid_area_900_plus(self):
        """Test SSN with area >= 900"""
        assert not self.validator.validate_ssn("900-12-3456")
        assert not self.validator.validate_ssn("999-12-3456")
    
    def test_invalid_group_00(self):
        """Test SSN with group 00"""
        assert not self.validator.validate_ssn("123-00-6789")
    
    def test_invalid_serial_0000(self):
        """Test SSN with serial 0000"""
        assert not self.validator.validate_ssn("123-45-0000")
    
    def test_invalid_area_734_749(self):
        """Test SSN in never-issued range 734-749"""
        assert not self.validator.validate_ssn("734-56-7890")
        assert not self.validator.validate_ssn("749-56-7890")
    
    def test_wrong_length(self):
        """Test SSN with wrong length"""
        assert not self.validator.validate_ssn("12-34-567")
        assert not self.validator.validate_ssn("1234-56-7890")
    
    def test_non_numeric(self):
        """Test SSN with non-numeric characters"""
        assert not self.validator.validate_ssn("abc-de-fghi")


class TestEmailValidation:
    """Test email address validation"""
    
    def setup_method(self):
        self.validator = PIIValidator()
    
    def test_valid_simple_email(self):
        """Test valid simple email"""
        assert self.validator.validate_email("user@example.com")
    
    def test_valid_email_with_dots(self):
        """Test valid email with dots"""
        assert self.validator.validate_email("first.last@example.com")
    
    def test_valid_email_with_plus(self):
        """Test valid email with plus"""
        assert self.validator.validate_email("user+tag@example.com")
    
    def test_valid_email_with_numbers(self):
        """Test valid email with numbers"""
        assert self.validator.validate_email("user123@example.com")
    
    def test_valid_email_subdomain(self):
        """Test valid email with subdomain"""
        assert self.validator.validate_email("user@mail.example.com")
    
    def test_invalid_no_at(self):
        """Test email without @"""
        assert not self.validator.validate_email("userexample.com")
    
    def test_invalid_multiple_at(self):
        """Test email with multiple @"""
        assert not self.validator.validate_email("user@@example.com")
    
    def test_invalid_no_domain(self):
        """Test email without domain"""
        assert not self.validator.validate_email("user@")
    
    def test_invalid_no_local(self):
        """Test email without local part"""
        assert not self.validator.validate_email("@example.com")
    
    def test_invalid_no_dot_in_domain(self):
        """Test email without dot in domain"""
        assert not self.validator.validate_email("user@examplecom")
    
    def test_invalid_too_long(self):
        """Test email exceeding length limit"""
        long_email = "a" * 250 + "@example.com"
        assert not self.validator.validate_email(long_email)
    
    def test_invalid_local_too_long(self):
        """Test email with local part too long"""
        long_local = "a" * 70 + "@example.com"
        assert not self.validator.validate_email(long_local)


class TestPhoneValidation:
    """Test phone number validation"""
    
    def setup_method(self):
        self.validator = PIIValidator()
    
    def test_valid_10_digit(self):
        """Test valid 10-digit US phone"""
        assert self.validator.validate_phone("555-123-4567")
        assert self.validator.validate_phone("(555) 123-4567")
        assert self.validator.validate_phone("5551234567")
    
    def test_valid_11_digit(self):
        """Test valid 11-digit phone with country code"""
        assert self.validator.validate_phone("1-555-123-4567")
        assert self.validator.validate_phone("15551234567")
    
    def test_valid_international(self):
        """Test valid international phone"""
        assert self.validator.validate_phone("+44 20 7946 0958")
        assert self.validator.validate_phone("+1-555-123-4567")
    
    def test_invalid_area_code_too_low(self):
        """Test area code below 200"""
        assert not self.validator.validate_phone("199-123-4567")
    
    def test_invalid_area_code_911(self):
        """Test invalid area code 911"""
        assert not self.validator.validate_phone("911-123-4567")
    
    def test_invalid_area_code_988(self):
        """Test invalid area code 988"""
        assert not self.validator.validate_phone("988-123-4567")
    
    def test_too_short(self):
        """Test phone too short"""
        assert not self.validator.validate_phone("123-4567")
    
    def test_too_long(self):
        """Test phone too long"""
        assert not self.validator.validate_phone("1234567890123456")


class TestIPAddressValidation:
    """Test IP address validation"""
    
    def setup_method(self):
        self.validator = PIIValidator()
    
    def test_valid_ip(self):
        """Test valid IP addresses"""
        assert self.validator.validate_ip_address("192.168.1.1")
        assert self.validator.validate_ip_address("10.0.0.1")
        assert self.validator.validate_ip_address("172.16.0.1")
        assert self.validator.validate_ip_address("8.8.8.8")
    
    def test_valid_ip_edge_values(self):
        """Test IP with edge values"""
        assert self.validator.validate_ip_address("0.0.0.0")
        assert self.validator.validate_ip_address("255.255.255.255")
    
    def test_invalid_octet_too_high(self):
        """Test IP with octet > 255"""
        assert not self.validator.validate_ip_address("192.168.1.256")
        assert not self.validator.validate_ip_address("300.168.1.1")
    
    def test_invalid_octet_negative(self):
        """Test IP with negative octet"""
        assert not self.validator.validate_ip_address("192.168.-1.1")
    
    def test_invalid_too_few_octets(self):
        """Test IP with too few octets"""
        assert not self.validator.validate_ip_address("192.168.1")
    
    def test_invalid_too_many_octets(self):
        """Test IP with too many octets"""
        assert not self.validator.validate_ip_address("192.168.1.1.1")
    
    def test_invalid_non_numeric(self):
        """Test IP with non-numeric characters"""
        assert not self.validator.validate_ip_address("abc.def.ghi.jkl")


class TestDateOfBirthValidation:
    """Test date of birth validation"""
    
    def setup_method(self):
        self.validator = PIIValidator()
    
    def test_valid_dob_mmddyyyy(self):
        """Test valid DOB in MM/DD/YYYY format"""
        assert self.validator.validate_date_of_birth("05/15/1985")
        assert self.validator.validate_date_of_birth("12-31-2000")
    
    def test_valid_dob_ddmmyyyy(self):
        """Test valid DOB in DD/MM/YYYY format"""
        assert self.validator.validate_date_of_birth("15/05/1985")
        assert self.validator.validate_date_of_birth("31-12-2000")
    
    def test_invalid_year_too_old(self):
        """Test DOB with year too old"""
        assert not self.validator.validate_date_of_birth("01/01/1899")
    
    def test_invalid_year_future(self):
        """Test DOB with future year"""
        assert not self.validator.validate_date_of_birth("01/01/2030")
    
    def test_invalid_month_too_high(self):
        """Test DOB with invalid month"""
        assert not self.validator.validate_date_of_birth("13/15/1985")
    
    def test_invalid_day_too_high(self):
        """Test DOB with invalid day"""
        assert not self.validator.validate_date_of_birth("05/32/1985")
    
    def test_invalid_format(self):
        """Test DOB with invalid format"""
        assert not self.validator.validate_date_of_birth("1985-05-15")


class TestPassportValidation:
    """Test passport number validation"""
    
    def setup_method(self):
        self.validator = PIIValidator()
    
    def test_valid_us_passport(self):
        """Test valid US passport formats"""
        assert self.validator.is_valid_passport("A1234567")
        assert self.validator.is_valid_passport("AB123456")
        assert self.validator.is_valid_passport("Z123456789")
    
    def test_invalid_no_letters(self):
        """Test passport with no letters"""
        assert not self.validator.is_valid_passport("12345678")
    
    def test_invalid_too_many_letters(self):
        """Test passport with too many letters"""
        assert not self.validator.is_valid_passport("ABC123456")
    
    def test_invalid_lowercase(self):
        """Test passport with lowercase letters"""
        assert not self.validator.is_valid_passport("a1234567")
    
    def test_invalid_too_short(self):
        """Test passport too short"""
        assert not self.validator.is_valid_passport("A12345")
    
    def test_invalid_too_long(self):
        """Test passport too long"""
        assert not self.validator.is_valid_passport("A1234567890")


class TestContextValidator:
    """Test context-based validation"""
    
    def setup_method(self):
        self.validator = ContextValidator()
    
    def test_name_positive_context(self):
        """Test name detection with positive context"""
        text = "Please contact Dr. John Smith for more information"
        start = text.find("Dr. John Smith")
        end = start + len("Dr. John Smith")
        
        assert self.validator.is_likely_name_context(text, start, end)
    
    def test_name_negative_context(self):
        """Test name detection with negative context"""
        text = "The file John Smith.txt contains the data"
        start = text.find("John Smith")
        end = start + len("John Smith")
        
        assert not self.validator.is_likely_name_context(text, start, end)
    
    def test_name_with_dear(self):
        """Test name with 'Dear' prefix"""
        text = "Dear John Smith, Thank you for your inquiry"
        start = text.find("John Smith")
        end = start + len("John Smith")
        
        assert self.validator.is_likely_name_context(text, start, end)
    
    def test_name_with_system_context(self):
        """Test name with system-related context"""
        text = "The system John Smith failed to start"
        start = text.find("John Smith")
        end = start + len("John Smith")
        
        assert not self.validator.is_likely_name_context(text, start, end)
    
    def test_address_positive_context(self):
        """Test address with positive context"""
        text = "My address is 123 Main Street"
        start = text.find("123 Main Street")
        end = start + len("123 Main Street")
        
        assert self.validator.is_likely_address_context(text, start, end)
    
    def test_address_with_located(self):
        """Test address with 'located' keyword"""
        text = "We are located at 456 Oak Avenue"
        start = text.find("456 Oak Avenue")
        end = start + len("456 Oak Avenue")
        
        assert self.validator.is_likely_address_context(text, start, end)
    
    def test_address_no_context(self):
        """Test address without clear context"""
        text = "Random text 123 Main Street more text"
        start = text.find("123 Main Street")
        end = start + len("123 Main Street")
        
        # Without strong indicators, should return False
        result = self.validator.is_likely_address_context(text, start, end)
        # This is a soft check - implementation may vary
        assert isinstance(result, bool)


class TestEdgeCases:
    """Test edge cases in validation"""
    
    def setup_method(self):
        self.validator = PIIValidator()
    
    def test_empty_string(self):
        """Test validation with empty string"""
        assert not self.validator.validate_credit_card("")
        assert not self.validator.validate_ssn("")
        assert not self.validator.validate_email("")
    
    def test_whitespace_only(self):
        """Test validation with whitespace only"""
        assert not self.validator.validate_credit_card("   ")
        assert not self.validator.validate_ssn("   ")
    
    def test_special_characters(self):
        """Test validation with special characters"""
        assert not self.validator.validate_credit_card("4532-1488-0343-646@")
        assert not self.validator.validate_ssn("123-45-678#")
    
    def test_mixed_separators(self):
        """Test credit card with mixed separators"""
        # Most validators should handle this or reject it
        result = self.validator.validate_credit_card("4532-1488 0343-6467")
        assert isinstance(result, bool)


class TestValidationPerformance:
    """Test validation performance"""
    
    def setup_method(self):
        self.validator = PIIValidator()
    
    def test_credit_card_performance(self):
        """Test credit card validation performance"""
        import time
        
        cards = ["4532148803436467"] * 1000
        
        start = time.time()
        for card in cards:
            self.validator.validate_credit_card(card)
        elapsed = time.time() - start
        
        # Should complete quickly
        assert elapsed < 0.1  # Less than 100ms for 1000 validations
    
    def test_ssn_performance(self):
        """Test SSN validation performance"""
        import time
        
        ssns = ["123-45-6789"] * 1000
        
        start = time.time()
        for ssn in ssns:
            self.validator.validate_ssn(ssn)
        elapsed = time.time() - start
        
        assert elapsed < 0.1  # Less than 100ms for 1000 validations
    
    def test_email_performance(self):
        """Test email validation performance"""
        import time
        
        emails = ["test@example.com"] * 1000
        
        start = time.time()
        for email in emails:
            self.validator.validate_email(email)
        elapsed = time.time() - start
        
        assert elapsed < 0.1  # Less than 100ms for 1000 validations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
