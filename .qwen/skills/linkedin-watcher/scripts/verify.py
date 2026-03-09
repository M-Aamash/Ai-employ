#!/usr/bin/env python3
"""
Verify LinkedIn Watcher is ready.
"""

import sys
import os
from pathlib import Path

# Set console encoding to UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

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
            browser = p.chromium.launch(headless=True)
            browser.close()
            return True, "Chromium browser available"
    except Exception as e:
        return False, f"Browser check failed: {e}"

def check_base_watcher():
    """Check if base watcher module is available."""
    base_watcher = Path(__file__).parent / 'base_watcher.py'
    if base_watcher.exists():
        return True, "Base watcher module available"
    return False, "Base watcher module not found"

def check_vault():
    """Check if vault exists."""
    # Try multiple possible paths
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault',
        Path(__file__).parent.parent.parent.parent.parent / 'AI_Employee_Vault',
        Path.cwd() / 'AI_Employee_Vault'
    ]
    
    for vault_path in possible_paths:
        if vault_path.exists() and vault_path.is_dir():
            return True, "AI_Employee_Vault found"
    
    return False, "AI_Employee_Vault not found"

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("   LinkedIn Watcher Verification")
    print("=" * 60 + "\n")

    checks = []
    all_passed = True

    # Check 1: Playwright
    passed, msg = check_playwright()
    symbol = "[OK]" if passed else "[FAIL]"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed

    # Check 2: Browser
    passed, msg = check_browser()
    symbol = "[OK]" if passed else "[FAIL]"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed

    # Check 3: Base watcher
    passed, msg = check_base_watcher()
    symbol = "[OK]" if passed else "[FAIL]"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed

    # Check 4: Vault
    passed, msg = check_vault()
    symbol = "[OK]" if passed else "[FAIL]"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed

    print("\n" + "=" * 60 + "\n")

    if all_passed:
        print("SUCCESS: LinkedIn Watcher is ready!")
        print("\nNext Steps:")
        print("  1. First-time login (visible mode):")
        print("     python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault --visible")
        print("\n  2. Post business content:")
        print("     python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault --action post")
        print("\n  3. Monitor for leads:")
        print("     python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault --action monitor")
        print("\n  4. Start continuous watching:")
        print("     python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault")
    else:
        print("INCOMPLETE: Please address the failed checks above.")
        print("\nTo install Playwright:")
        print("  pip install playwright")
        print("  python -m playwright install chromium")

    print("\n" + "=" * 60 + "\n")

    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
