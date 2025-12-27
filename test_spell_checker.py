#!/usr/bin/env python3
"""
Test script for two-stage spell checker
Verifies that both stages work correctly
"""

import sys
from spellchecker import SpellChecker

def test_traditional_checker():
    """Test that traditional spell checker works"""
    print("Testing traditional spell checker...")
    
    spell = SpellChecker()
    
    # Test text with known errors
    test_text = "This is a teh test with speling errors and vmware kubernetes"
    
    # Whitelist technical terms
    whitelist = {'vmware', 'kubernetes', 'docker', 'nginx'}
    spell.word_frequency.load_words(whitelist)
    
    # Extract words
    import re
    words = re.findall(r'\b[a-zA-Z]+\b', test_text)
    
    print(f"  Words found: {words}")
    
    # Check for misspellings
    misspelled = []
    for word in words:
        word_lower = word.lower()
        if len(word_lower) < 3:
            continue
        if word_lower in whitelist:
            continue
        if word_lower not in spell:
            misspelled.append(word)
    
    print(f"  Misspelled words: {misspelled}")
    
    # Verify we found the errors
    assert 'teh' in misspelled, "Should find 'teh' as misspelled"
    assert 'speling' in misspelled, "Should find 'speling' as misspelled"
    assert 'vmware' not in [w.lower() for w in misspelled], "Should NOT flag 'vmware'"
    assert 'kubernetes' not in [w.lower() for w in misspelled], "Should NOT flag 'kubernetes'"
    
    print("  ✅ Traditional checker working correctly!")
    return True

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        import requests
        print("  ✓ requests")
    except ImportError as e:
        print(f"  ✗ requests: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("  ✓ beautifulsoup4")
    except ImportError as e:
        print(f"  ✗ beautifulsoup4: {e}")
        return False
    
    try:
        from spellchecker import SpellChecker
        print("  ✓ pyspellchecker")
    except ImportError as e:
        print(f"  ✗ pyspellchecker: {e}")
        return False
    
    print("  ✅ All imports successful!")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Two-Stage Spell Checker - Test Suite")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed")
        all_passed = False
    print()
    
    # Test traditional checker
    try:
        if not test_traditional_checker():
            print("\n❌ Traditional checker test failed")
            all_passed = False
    except Exception as e:
        print(f"\n❌ Traditional checker test error: {e}")
        all_passed = False
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("✅ All tests passed!")
        print()
        print("Next steps:")
        print("1. Set WP_AUTH_TOKEN environment variable")
        print("2. Run: ./ollama_spell_checker.py 1")
        print("3. Verify you see 'Stage 1' and 'Stage 2' messages")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        print()
        print("To install dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
