"""
PII Validator Module
Advanced validation logic for specific PII types
"""

import re
from typing import Optional


class PIIValidator:
    """Validates detected PII to reduce false positives"""
    
    @staticmethod
    def validate_credit_card(card_number: str) -> bool:
        """
        Validate credit card using Luhn algorithm
        
        Args:
            card_number: Credit card number (may contain spaces/dashes)
            
        Returns:
            True if valid, False otherwise
        """
        # Remove all non-digit characters
        digits = [int(d) for d in card_number if d.isdigit()]
        
        if len(digits) < 13 or len(digits) > 19:
            return False
        
        # Luhn algorithm
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:  # Every second digit from right
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        
        return checksum % 10 == 0
    
    @staticmethod
    def validate_ssn(ssn: str) -> bool:
        """
        Validate Social Security Number against official rules
        
        Args:
            ssn: SSN (may contain dashes/spaces)
            
        Returns:
            True if valid, False otherwise
        """
        # Remove all non-digit characters
        clean_ssn = re.sub(r'[\s\-]', '', ssn)
        
        # Must be exactly 9 digits
        if len(clean_ssn) != 9 or not clean_ssn.isdigit():
            return False
        
        area = int(clean_ssn[:3])
        group = int(clean_ssn[3:5])
        serial = int(clean_ssn[5:])
        
        # Invalid area numbers
        if area == 0 or area == 666 or area >= 900:
            return False
        
        # Invalid group or serial
        if group == 0 or serial == 0:
            return False
        
        # Additional checks for known invalid ranges
        # (SSA has never issued SSNs with area 734-749)
        if 734 <= area <= 749:
            return False
        
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format
        
        Args:
            email: Email address
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation (already done by regex, this adds extra checks)
        if len(email) > 254:  # RFC 5321
            return False
        
        parts = email.split('@')
        if len(parts) != 2:
            return False
        
        local, domain = parts
        
        # Local part checks
        if len(local) == 0 or len(local) > 64:
            return False
        
        # Domain checks
        if len(domain) == 0 or len(domain) > 253:
            return False
        
        # Must have at least one dot in domain
        if '.' not in domain:
            return False
        
        # Domain parts shouldn't be empty
        domain_parts = domain.split('.')
        if any(len(part) == 0 for part in domain_parts):
            return False
        
        return True
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number
        
        Args:
            phone: Phone number
            
        Returns:
            True if likely valid, False otherwise
        """
        # Extract digits
        digits = ''.join(c for c in phone if c.isdigit())
        
        # US phone numbers
        if len(digits) == 10:
            area_code = int(digits[:3])
            # Invalid area codes
            if area_code < 200 or area_code in [911, 988]:
                return False
            return True
        
        # International (with country code)
        if 11 <= len(digits) <= 15:
            return True
        
        return False
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """
        Validate IPv4 address
        
        Args:
            ip: IP address
            
        Returns:
            True if valid, False otherwise
        """
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            except ValueError:
                return False
        
        return True
    
    @staticmethod
    def validate_date_of_birth(dob: str) -> bool:
        """
        Validate date of birth (basic range check)
        
        Args:
            dob: Date string
            
        Returns:
            True if likely valid, False otherwise
        """
        # Extract year
        parts = re.split(r'[/\-]', dob)
        if len(parts) != 3:
            return False
        
        try:
            # Try to identify year (either first or last position)
            year = None
            for part in parts:
                if len(part) == 4:
                    year = int(part)
                    break
            
            if year is None:
                return False
            
            # Year should be between 1900 and current year
            if year < 1900 or year > 2025:
                return False
            
            # Basic month/day validation
            for part in parts:
                if len(part) <= 2:
                    val = int(part)
                    if val < 1 or val > 31:
                        return False
            
            return True
            
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_passport(passport: str) -> bool:
        """
        Validate passport number format
        
        Args:
            passport: Passport number
            
        Returns:
            True if format is valid, False otherwise
        """
        # US passports: 1-2 letters followed by 6-9 digits
        if re.match(r'^[A-Z]{1,2}\d{6,9}$', passport):
            return True
        return False


class ContextValidator:
    """Validates PII based on surrounding context"""
    
    @staticmethod
    def is_likely_name_context(text: str, start: int, end: int) -> bool:
        """
        Check if context around detected text suggests it's a name
        
        Args:
            text: Full text
            start: Start position of potential name
            end: End position of potential name
            
        Returns:
            True if context suggests name, False otherwise
        """
        # Look at words before and after
        before = text[max(0, start-20):start].lower()
        after = text[end:min(len(text), end+20)].lower()
        
        # Positive indicators
        positive_keywords = [
            'name', 'called', 'contact', 'from', 'by', 'to',
            'dear', 'sincerely', 'regards', 'attn', 'attention'
        ]
        
        # Negative indicators (suggests it's not a name)
        negative_keywords = [
            'file', 'folder', 'document', 'system', 'server',
            'application', 'program', 'code', 'variable'
        ]
        
        context = before + ' ' + after
        
        # Check for positive indicators
        has_positive = any(kw in context for kw in positive_keywords)
        
        # Check for negative indicators
        has_negative = any(kw in context for kw in negative_keywords)
        
        if has_negative:
            return False
        
        return True
    
    @staticmethod
    def is_likely_address_context(text: str, start: int, end: int) -> bool:
        """
        Check if context suggests an address
        
        Args:
            text: Full text
            start: Start position
            end: End position
            
        Returns:
            True if likely an address, False otherwise
        """
        before = text[max(0, start-30):start].lower()
        after = text[end:min(len(text), end+30)].lower()
        
        address_keywords = [
            'address', 'located', 'live', 'office', 'building',
            'suite', 'floor', 'unit', 'apt', 'apartment'
        ]
        
        context = before + ' ' + after
        return any(kw in context for kw in address_keywords)
