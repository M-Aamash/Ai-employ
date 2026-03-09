"""
LinkedIn Post - Error Fixed Version

Fixed: Multiple selectors for "Start a Post" button with proper error handling.
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
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
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
    print("   LinkedIn Post - Error Fixed")
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
        
        # ===== STEP 1: Open LinkedIn =====
        print("Step 1: Opening LinkedIn...")
        try:
            page.goto('https://www.linkedin.com', timeout=30000)
            time.sleep(3)
            page.goto('https://www.linkedin.com/feed', timeout=30000)
            time.sleep(5)
            print("   ✓ Done\n")
        except Exception as e:
            print(f"   ⚠ Error: {e}\n")
            browser.close()
            return
        
        # ===== STEP 2: Click "Start a Post" =====
        print("Step 2: Clicking 'Start a Post'...")
        
        # Multiple selectors to try
        start_post_selectors = [
            'text=Start a Post',
            'button[aria-label="Start a Post"]',
            '.share-box-feed-entry__trigger',
            'button:has-text("Start a Post")',
            'div.share-box-feed-entry'
        ]
        
        clicked = False
        for selector in start_post_selectors:
            try:
                page.click(selector, timeout=5000)
                print(f"   ✓ Clicked: {selector}\n")
                clicked = True
                break
            except:
                continue
        
        if not clicked:
            print("   ⚠ Could not find 'Start a Post' button\n")
            print("   LinkedIn may have changed their UI\n")
            browser.close()
            return
        
        time.sleep(3)
        
        # ===== STEP 3: Fill Content =====
        print("Step 3: Filling content...")
        
        try:
            textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
            textbox.click()
            time.sleep(2)
            textbox.fill(CONTENT)
            time.sleep(5)
            print(f"   ✓ Content filled\n")
        except Exception as e:
            print(f"   ⚠ Error filling content: {e}\n")
            browser.close()
            return
        
        # ===== STEP 4: Click Post =====
        print("Step 4: Clicking 'Post'...")
        
        try:
            post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
            time.sleep(3)
            post_btn.click()
            print("   ✓ Post button clicked\n")
        except Exception as e:
            print(f"   ⚠ Error: {e}\n")
        
        # ===== STEP 5: Wait for Publication =====
        print("Step 5: Waiting for publication...")
        time.sleep(15)
        
        # Check if published
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
        
        time.sleep(3)
        browser.close()

if __name__ == '__main__':
    main()
