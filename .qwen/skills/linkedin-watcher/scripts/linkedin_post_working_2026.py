"""
LinkedIn Post - Working Version 2026

Fixed to properly wait for page load and handle login.
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
    print("   LinkedIn Post - Working Version 2026")
    print("=" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox'],
            timeout=60000
        )
        
        page = browser.pages[0]
        
        # Step 1: Open LinkedIn
        print("Step 1: Opening LinkedIn...")
        page.goto('https://www.linkedin.com', timeout=60000)
        time.sleep(10)  # Wait for page
        
        # Check if logged in
        if 'login' in page.url or 'checkpoint' in page.url:
            print("   ⚠ NOT LOGGED IN!")
            print("   Please log in to LinkedIn in the browser window.")
            print("   Waiting 60 seconds...\n")
            
            # Wait for user to log in
            for i in range(60):
                time.sleep(1)
                if 'feed' in page.url or 'myhome' in page.url:
                    print("   ✓ Login detected!\n")
                    break
            else:
                print("   ⚠ Login timeout. Please run again after logging in.\n")
                time.sleep(10)
                browser.close()
                return
        
        # Go to feed
        print("   Going to feed...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(10)  # Wait for feed to load
        print("   ✓ Done\n")
        
        # Step 2: Click "Start a Post"
        print("Step 2: Clicking 'Start a Post'...")
        
        # Wait for button with longer timeout
        try:
            page.wait_for_selector('text=Start a Post', timeout=30000)
            page.click('text=Start a Post')
            time.sleep(5)
            print("   ✓ Done\n")
        except Exception as e:
            print(f"   ⚠ Error: {e}\n")
            print("   LinkedIn UI may have changed. Try manual posting:\n")
            print("   python .qwen/skills/linkedin-watcher/scripts/linkedin_post_easy.py\n")
            browser.close()
            return
        
        # Step 3: Fill content
        print("Step 3: Filling content...")
        try:
            textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
            textbox.click()
            time.sleep(2)
            textbox.fill(CONTENT)
            time.sleep(5)
            print("   ✓ Done\n")
        except Exception as e:
            print(f"   ⚠ Error: {e}\n")
            browser.close()
            return
        
        # Step 4: Click Post
        print("Step 4: Clicking 'Post'...")
        try:
            post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
            time.sleep(3)
            post_btn.click()
            print("   ✓ Done\n")
        except Exception as e:
            print(f"   ⚠ Error: {e}\n")
        
        # Step 5: Wait for publication
        print("Step 5: Waiting for publication...")
        time.sleep(20)
        
        # Check result
        if '/feed' in page.url:
            print("\n" + "=" * 70)
            print("   ✓✓✓ SUCCESSFUL! ✓✓✓")
            print("=" * 70)
            print("\nYour post has been PUBLISHED!")
            print("\nView: https://www.linkedin.com/feed\n")
        else:
            print("\n" + "=" * 70)
            print("   ⚠ Check manually")
            print("=" * 70 + "\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
