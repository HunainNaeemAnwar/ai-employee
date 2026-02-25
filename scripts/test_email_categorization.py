#!/usr/bin/env python3
"""
Test Email Categorization

Tests the Gmail watcher's email categorization logic.

Usage:
    python scripts/test_email_categorization.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from watchers.gmail import GmailWatcher


def test_email_categorization():
    """Test email type detection."""
    print("🧪 Testing Email Categorization")
    print("=" * 60)
    
    watcher = GmailWatcher(vault_path="/tmp")
    
    test_cases = [
        # (subject, body, labels, expected_type)
        (
            "Invoice #1234 - Payment Due",
            "Please find attached invoice for services rendered.",
            [],
            "invoice"
        ),
        (
            "URGENT: Deadline Tomorrow",
            "We need this ASAP or we'll miss the deadline.",
            [],
            "urgent"
        ),
        (
            "Weekly Newsletter",
            "Check out our latest deals! Click here to unsubscribe.",
            ["CATEGORY_PROMOTIONS"],
            "promotional"
        ),
        (
            "Quick question",
            "Hi, can we schedule a meeting?",
            [],
            "general"
        ),
        (
            "Payment confirmation",
            "Your bill has been paid successfully.",
            [],
            "invoice"
        ),
        (
            "Meeting reminder",
            "Just a reminder about our meeting tomorrow.",
            ["IMPORTANT"],
            "general"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for subject, body, labels, expected in test_cases:
        email_data = {
            "subject": subject,
            "body": body,
            "labels": labels
        }
        
        result = watcher.detect_type(email_data)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status} Test: '{subject[:30]}...'")
        print(f"   Expected: {expected}")
        print(f"   Got: {result}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


def test_priority_calculation():
    """Test email priority calculation."""
    print("\n🧪 Testing Priority Calculation")
    print("=" * 60)
    
    watcher = GmailWatcher(vault_path="/tmp")
    
    test_cases = [
        # (subject, body, labels, expected_priority)
        (
            "URGENT: ASAP help needed",
            "This is very urgent and important.",
            ["IMPORTANT", "STARRED"],
            "high"
        ),
        (
            "Important meeting",
            "Please attend the important meeting.",
            ["IMPORTANT"],
            "medium"
        ),
        (
            "Regular email",
            "Just a regular email.",
            [],
            "low"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for subject, body, labels, expected in test_cases:
        email_data = {
            "subject": subject,
            "body": body,
            "labels": labels
        }
        
        result = watcher.calculate_priority(email_data)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status} Test: '{subject[:30]}...'")
        print(f"   Expected: {expected}")
        print(f"   Got: {result}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


def test_hitl_detection():
    """Test HITL requirement detection."""
    print("\n🧪 Testing HITL Detection")
    print("=" * 60)
    
    watcher = GmailWatcher(vault_path="/tmp")
    
    test_cases = [
        # (from_addr, body, subject, expected_hitl)
        (
            "unknown@gmail.com",
            "Short message",
            "Hello",
            True  # Unknown sender
        ),
        (
            "known@knownclient.com",
            "Short message",
            "Hello",
            False  # Known sender, short body
        ),
        (
            "known@knownclient.com",
            "x" * 1001,
            "Hello",
            True  # Long body
        ),
        (
            "known@knownclient.com",
            "Short message",
            "Payment invoice attached",
            True  # Payment related
        ),
        (
            "known@knownclient.com",
            "Check this link: https://example.com",
            "Hello",
            True  # Contains link
        ),
    ]
    
    passed = 0
    failed = 0
    
    for from_addr, body, subject, expected in test_cases:
        email_data = {
            "from": from_addr,
            "body": body,
            "subject": subject
        }
        
        result = watcher.check_hitl_required(email_data)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status} Test: '{from_addr[:30]}...'")
        print(f"   Expected HITL: {expected}")
        print(f"   Got: {result}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


def main():
    """Run all categorization tests."""
    print("\n" + "=" * 60)
    print("📧 Email Categorization Test Suite")
    print("=" * 60 + "\n")
    
    type_passed = test_email_categorization()
    priority_passed = test_priority_calculation()
    hitl_passed = test_hitl_detection()
    
    print("\n" + "=" * 60)
    print("📊 Overall Results")
    print("=" * 60)
    
    all_passed = type_passed and priority_passed and hitl_passed
    
    if all_passed:
        print("✅ All tests PASSED!")
    else:
        print("❌ Some tests FAILED")
        if not type_passed:
            print("   - Email type detection")
        if not priority_passed:
            print("   - Priority calculation")
        if not hitl_passed:
            print("   - HITL detection")
    
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
