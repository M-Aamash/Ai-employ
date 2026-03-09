"""
LinkedIn Post - Ultimate Fixed Version

Waits for page to fully load before clicking.
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
    print("   LinkedIn Post - Ultimate Fixed")
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
        
        # Step 1: Open LinkedIn and WAIT
        print("Step 1: Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        
        # Wait for page to fully load
        print("   Waiting for page to load...")
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_load_state('networkidle')
        time.sleep(10)  # Extra wait
        
        # Check if logged in
        if 'login' in page.url or 'checkpoint' in page.url:
            print("   ⚠ Not logged in! Please log in manually.\n")
            time.sleep(30)  # Wait for manual login
        
        print("   ✓ LinkedIn loaded\n")
        
        # Step 2: Click "Start a Post"
        print("Step 2: Clicking 'Start a Post'...")
        
        # Wait for the button to appear
        try:
            page.wait_for_selector('text=Start a Post', timeout=30000)
            page.click('text=Start a Post')
            time.sleep(3)
            print("   ✓ Done\n")
        except:
            print("   ⚠ Button not found\n")
            browser.close()
            return
        
        # Step 3: Fill content
        print("Step 3: Filling content...")
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.click()
        time.sleep(2)
        textbox.fill(CONTENT)
        time.sleep(5)
        print("   ✓ Done\n")
        
        # Step 4: Click Post
        print("Step 4: Clicking 'Post'...")
        post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
        time.sleep(3)
        post_btn.click()
        print("   ✓ Done\n")
        
        # Step 5: Wait
        print("Step 5: Waiting for publication...")
        time.sleep(20)
        
        # Check result
        if '/feed' in page.url:
            print("\n" + "=" * 70)
            print("   ✓✓✓ SUCCESSFUL! ✓✓✓")
            print("=" * 70)
            print("\nView: https://www.linkedin.com/feed\n")
        else:
            print("\n" + "=" * 70)
            print("   ⚠ Check manually\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
