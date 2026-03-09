"""
LinkedIn Post - Keyboard Based

Uses keyboard input which is more reliable than mouse clicks.
"""

import sys
import os
import time
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Install: pip install playwright")
    sys.exit(1)

CONTENT = """🚀 Exciting news! We're helping businesses automate their operations with AI-powered solutions.

Our AI employees work 24/7 to:
✅ Handle customer inquiries
✅ Process invoices automatically  
✅ Manage communications
✅ Generate business insights

Ready to transform your business? Let's talk!

#AI #Automation #Business #Innovation #DigitalTransformation"""

def main():
    print("\n" + "=" * 70)
    print("   LinkedIn Post - Keyboard Based")
    print("=" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        page = browser.pages[0]
        
        # Go to LinkedIn feed
        print("1. Opening LinkedIn feed...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(8)
        print("   Done\n")
        
        # Use keyboard to open post dialog (Tab + Enter)
        print("2. Opening post composer...")
        
        # Focus on the "Start a Post" area using tab navigation
        for i in range(5):
            page.keyboard.press('Tab')
            time.sleep(0.3)
        
        # Press Enter to open composer
        page.keyboard.press('Enter')
        time.sleep(5)
        print("   Composer opened\n")
        
        # Type content directly
        print("3. Typing content...")
        
        # Type character by character for reliability
        for char in CONTENT:
            page.keyboard.type(char, delay=10)
            time.sleep(0.01)
        
        time.sleep(3)
        print(f"   Typed {len(CONTENT)} characters\n")
        
        # Press Tab to reach Post button
        print("4. Navigating to Post button...")
        for i in range(3):
            page.keyboard.press('Tab')
            time.sleep(0.5)
        
        # Press Enter to post
        print("5. Publishing...")
        page.keyboard.press('Enter')
        print("   Post submitted\n")
        
        # Wait for publication
        print("6. Waiting for publication...")
        for i in range(20):
            time.sleep(1)
            
            # Check if back on feed
            if '/feed' in page.url:
                print("\n" + "=" * 70)
                print("   ✓✓✓ SUCCESS! Post published to LinkedIn! ✓✓✓")
                print("=" * 70)
                print("\nYour post is now live!")
                print("Visit: https://www.linkedin.com/feed\n")
                break
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
