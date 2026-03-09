"""
LinkedIn Manual Login Helper

This script opens a browser window for you to manually log in to LinkedIn.
Once logged in, the session is saved for future automated operations.

Usage:
    python linkedin_login.py
    
Steps:
    1. Script opens browser
    2. You log in to LinkedIn manually
    3. Wait for "Session saved" message
    4. Close browser
    5. Future automated scripts will use saved session
"""

import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright")
    sys.exit(1)

def main():
    print("\n" + "=" * 60)
    print("   LinkedIn Manual Login Helper")
    print("=" * 60 + "\n")
    print("A browser window will open.")
    print("Please log in to LinkedIn manually.")
    print("Once logged in, wait for 'Session saved' message.\n")
    print("Opening browser in 3 seconds...")
    
    import time
    time.sleep(3)
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("\nOpening browser...")
    
    with sync_playwright() as p:
        # Launch browser with persistent context
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,  # Visible browser
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        
        page = browser.pages[0]
        
        # Navigate to LinkedIn
        print("Navigate to: https://www.linkedin.com/login")
        page.goto('https://www.linkedin.com/login', timeout=60000)
        
        print("\n" + "=" * 60)
        print("LOGIN INSTRUCTIONS:")
        print("=" * 60)
        print("1. Enter your email/phone and password")
        print("2. Complete any verification")
        print("3. Wait until you see your LinkedIn feed")
        print("4. DO NOT close the browser")
        print("5. Script will detect login and save session")
        print("=" * 60 + "\n")
        
        # Wait for login (up to 5 minutes)
        print("Waiting for login... (up to 5 minutes)")
        max_wait = 300  # 5 minutes
        wait_interval = 2  # Check every 2 seconds
        elapsed = 0
        
        while elapsed < max_wait:
            try:
                # Check if we're on the feed (logged in)
                current_url = page.url
                
                if 'feed' in current_url or '/myhome/' in current_url:
                    print("\n[OK] Login detected!")
                    print(f"Current URL: {current_url}")
                    print("\nSession saved to:", session_path)
                    print("\nYou can now close the browser.")
                    print("Future automated scripts will use this session.\n")
                    
                    # Wait a bit for cookies to settle
                    page.wait_for_timeout(3000)
                    break
                
                # Check if still on login page
                if 'login' in current_url:
                    elapsed += wait_interval
                    page.wait_for_timeout(wait_interval * 1000)
                    continue
                    
            except Exception as e:
                elapsed += wait_interval
                page.wait_for_timeout(wait_interval * 1000)
        
        if elapsed >= max_wait:
            print("\n[WARN] Login timeout. Please try again.")
            print("Make sure you completed the login in the browser.\n")
        
        browser.close()
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Test automated posting:")
    print("   python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault --action post")
    print("\n2. Monitor for leads:")
    print("   python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault --action monitor")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    main()
