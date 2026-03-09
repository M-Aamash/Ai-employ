#!/usr/bin/env python3
"""
Verify Gmail Watcher is ready.
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

def check_google_api():
    """Check if Google API client is installed."""
    try:
        from googleapiclient.discovery import build
        return True, "Google API client installed"
    except ImportError:
        return False, "Google API client not installed"

def check_credentials():
    """Check if credentials file exists."""
    # Check in multiple possible locations
    project_root = Path(__file__).parent.parent.parent.parent
    possible_paths = [
        project_root / 'credentials.json',
        project_root.parent / 'credentials.json',
        Path.cwd() / 'credentials.json',
        Path.home() / 'credentials.json'
    ]
    
    for creds_path in possible_paths:
        if creds_path.exists():
            return True, f"credentials.json found ({creds_path.parent})"
    
    return False, "credentials.json not found in project root"

def check_base_watcher():
    """Check if base watcher module is available."""
    base_watcher = Path(__file__).parent / 'base_watcher.py'
    if base_watcher.exists():
        return True, "Base watcher module available"
    return False, "Base watcher module not found"

def check_vault():
    """Check if vault exists."""
    # Try multiple possible paths
    project_root = Path(__file__).parent.parent.parent.parent
    possible_paths = [
        project_root / 'AI_Employee_Vault',
        project_root.parent / 'AI_Employee_Vault',
        Path.cwd() / 'AI_Employee_Vault'
    ]
    
    for vault_path in possible_paths:
        if vault_path.exists() and vault_path.is_dir():
            return True, "AI_Employee_Vault found"
    
    return False, "AI_Employee_Vault not found"

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("   Gmail Watcher Verification")
    print("=" * 60 + "\n")
    
    checks = []
    all_passed = True
    
    # Check 1: Google API
    passed, msg = check_google_api()
    symbol = "[OK]" if passed else "[FAIL]"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Check 2: Credentials
    passed, msg = check_credentials()
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
        print("SUCCESS: Gmail Watcher is ready!")
        print("\nNext Steps:")
        print("  1. Authorize Gmail API:")
        print("     python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --authorize")
        print("\n  2. Start watching:")
        print("     python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --interval 120")
        print("\n  3. Process emails with Qwen Code:")
        print("     qwen --cd ./AI_Employee_Vault")
    else:
        print("INCOMPLETE: Please address the failed checks above.")
        print("\nTo install Google API client:")
        print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        print("\nTo get credentials:")
        print("  1. Visit https://console.cloud.google.com/")
        print("  2. Create project and enable Gmail API")
        print("  3. Create OAuth 2.0 credentials (Desktop app)")
        print("  4. Download credentials.json to project root")
    
    print("\n" + "=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
