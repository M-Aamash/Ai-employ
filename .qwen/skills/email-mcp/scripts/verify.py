#!/usr/bin/env python3
"""
Verify Email MCP is ready.
"""

import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        return True, "Email dependencies installed"
    except ImportError as e:
        return False, f"Missing dependency: {e}"

def check_gmail_api():
    """Check if Gmail API is configured (optional)."""
    creds = Path('token.json')
    if creds.exists():
        return True, "Gmail API configured (token.json found)"
    return False, "Gmail API not configured (will use SMTP)"

def check_smtp_config():
    """Check if SMTP is configured."""
    env_file = Path('.env')
    if env_file.exists():
        content = env_file.read_text()
        if 'SMTP_HOST' in content and 'SMTP_USER' in content:
            return True, "SMTP configuration found in .env"
    return False, "SMTP not configured in .env"

def check_server_script():
    """Check if server script exists."""
    script = Path('scripts/email_mcp_server.py')
    if script.exists():
        return True, "Email MCP server script found"
    return False, "Email MCP server script not found"

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("   Email MCP Verification")
    print("=" * 60 + "\n")
    
    checks = []
    all_passed = True
    
    # Check 1: Dependencies
    passed, msg = check_dependencies()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Check 2: Gmail API (optional)
    passed, msg = check_gmail_api()
    symbol = "✓" if passed else "○"
    print(f"{symbol} {msg}")
    checks.append(passed)  # Don't fail if Gmail API not configured
    
    # Check 3: SMTP config
    passed, msg = check_smtp_config()
    symbol = "✓" if passed else "○"
    print(f"{symbol} {msg}")
    # Don't fail - can be configured via command line
    
    # Check 4: Server script
    passed, msg = check_server_script()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    print("\n" + "=" * 60 + "\n")
    
    if all_passed:
        print("SUCCESS: Email MCP is ready!")
        print("\nConfiguration Options:")
        print("  1. Gmail API: Place token.json in project root")
        print("  2. SMTP: Add SMTP_HOST, SMTP_USER, SMTP_PASS to .env")
        print("\nUsage:")
        print("  # Start server")
        print("  python scripts/email_mcp_server.py --port 8810")
        print("\n  # With SMTP config")
        print("  python scripts/email_mcp_server.py --port 8810 --smtp-user you@email.com --smtp-pass password")
    else:
        print("INCOMPLETE: Please address the failed checks above.")
        print("\nTo install dependencies:")
        print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    
    print("\n" + "=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
