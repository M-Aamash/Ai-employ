#!/usr/bin/env python3
"""
Verify WhatsApp Watcher is ready.
"""

import sys
from pathlib import Path

def check_playwright():
    """Check if Playwright is installed."""
    try:
        import playwright
        return True, "Playwright installed"
    except ImportError:
        return False, "Playwright not installed"

def check_browser():
    """Check if Chromium browser is installed."""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Try to launch browser
            browser = p.chromium.launch(headless=True)
            browser.close()
            return True, "Chromium browser available"
    except Exception as e:
        return False, f"Browser check failed: {e}"

def check_dependencies():
    """Check if all dependencies are available."""
    try:
        import base_watcher
        return True, "Dependencies available"
    except ImportError as e:
        return False, f"Missing dependency: {e}"

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("   WhatsApp Watcher Verification")
    print("=" * 60 + "\n")
    
    checks = []
    all_passed = True
    
    # Check 1: Playwright
    passed, msg = check_playwright()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Check 2: Browser
    passed, msg = check_browser()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Check 3: Dependencies
    passed, msg = check_dependencies()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    print("\n" + "=" * 60 + "\n")
    
    if all_passed:
        print("SUCCESS: WhatsApp Watcher is ready!")
        print("\nFirst Run Instructions:")
        print("  1. Run with --visible flag: python scripts/whatsapp_watcher.py --vault ./vault --visible")
        print("  2. Scan the QR code with your phone")
        print("  3. Subsequent runs will use saved session")
        print("\nUsage:")
        print("  python scripts/whatsapp_watcher.py --vault /path/to/vault --interval 30")
    else:
        print("INCOMPLETE: Please address the failed checks above.")
        print("\nTo install Playwright:")
        print("  pip install playwright")
        print("  playwright install chromium")
    
    print("\n" + "=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
