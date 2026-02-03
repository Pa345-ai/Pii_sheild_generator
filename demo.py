#!/usr/bin/env python3
"""
Quick Demo Script
Test the PII-Shield engine locally
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pii_shield import PIIDetector
from pii_shield.patterns import PIIType


def print_banner():
    print("\n" + "="*80)
    print("                    PII-SHIELD ENGINE DEMO")
    print("          Enterprise PII Detection and Masking")
    print("="*80 + "\n")


def demo_basic_detection():
    print("Demo 1: Basic PII Detection")
    print("-" * 80)
    
    detector = PIIDetector()
    
    text = "Contact John Smith at john@example.com or call (555) 123-4567"
    print(f"Input: {text}\n")
    
    matches = detector.detect_all(text)
    
    print(f"✓ Detected {len(matches)} PII instances:")
    for match in matches:
        print(f"  • {match.pii_type}: '{match.value}' → '{match.masked_value}'")
    
    masked = detector.mask_text(text, matches)
    print(f"\n✓ Masked Output: {masked}")


def demo_credit_cards():
    print("\n\nDemo 2: Credit Card Detection & Validation")
    print("-" * 80)
    
    detector = PIIDetector()
    
    cards = [
        ("Visa: 4532-1488-0343-6467", "Valid"),
        ("Mastercard: 5425 2334 3010 9903", "Valid"),
        ("Invalid: 4532-1488-0343-6468", "Invalid - Luhn")
    ]
    
    for card_text, expected in cards:
        matches = detector.detect_all(card_text)
        cc_matches = [m for m in matches if m.pii_type == PIIType.CREDIT_CARD.value]
        
        if cc_matches:
            print(f"✓ {card_text} → {cc_matches[0].masked_value} ({expected})")
        else:
            print(f"✗ {card_text} → Not detected ({expected})")


def demo_comprehensive():
    print("\n\nDemo 3: Comprehensive Multi-PII Detection")
    print("-" * 80)
    
    detector = PIIDetector()
    
    text = """
    Dear Dr. Sarah Johnson,
    
    Your account information:
    Email: sarah.j@company.com
    Phone: (555) 234-5678
    SSN: 123-45-6789
    Card: 4532-1488-0343-6467
    Address: 123 Main Street
    """
    
    print("Original Text:")
    print(text)
    
    matches = detector.detect_all(text)
    
    print(f"\n✓ Detected {len(matches)} PII instances:")
    pii_types = {}
    for match in matches:
        if match.pii_type not in pii_types:
            pii_types[match.pii_type] = 0
        pii_types[match.pii_type] += 1
    
    for pii_type, count in sorted(pii_types.items()):
        print(f"  • {pii_type}: {count} instance(s)")
    
    masked = detector.mask_text(text, matches)
    print("\nMasked Text:")
    print(masked)


def demo_performance():
    print("\n\nDemo 4: Performance Benchmark")
    print("-" * 80)
    
    import time
    detector = PIIDetector()
    
    text = "Email: test@example.com, Phone: 555-1234, SSN: 123-45-6789" * 10
    
    iterations = 100
    start = time.time()
    
    for _ in range(iterations):
        matches = detector.detect_all(text)
    
    elapsed = time.time() - start
    avg_time = (elapsed / iterations) * 1000
    
    print(f"✓ Processed {iterations} texts")
    print(f"✓ Average time: {avg_time:.2f}ms per text")
    print(f"✓ Throughput: {len(text) * iterations / elapsed:,.0f} chars/second")


def main():
    print_banner()
    
    try:
        demo_basic_detection()
        demo_credit_cards()
        demo_comprehensive()
        demo_performance()
        
        print("\n" + "="*80)
        print("                    ALL DEMOS COMPLETED")
        print("="*80)
        print("\nNext Steps:")
        print("  1. Run tests: pytest tests/ -v")
        print("  2. Start API: uvicorn api.main:app --reload")
        print("  3. View docs: http://localhost:8000/docs")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
