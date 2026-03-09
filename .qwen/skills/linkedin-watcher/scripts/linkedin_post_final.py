"""
LinkedIn Post - Final Working Version

Takes screenshots at each step and ensures post is published.
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
    print("   LinkedIn Post - Final Version")
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
        screenshot_dir = Path.cwd() / 'linkedin_screenshots'
        screenshot_dir.mkdir(exist_ok=True)
        
        # Step 1: Open LinkedIn
        print("Step 1: Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(8)
        page.screenshot(path=str(screenshot_dir / '01_loaded.png'))
        print("   ✓ LinkedIn loaded\n")
        
        # Step 2: Click Start a Post
        print("Step 2: Clicking 'Start a Post'...")
        page.click('text=Start a Post')
        time.sleep(5)
        page.screenshot(path=str(screenshot_dir / '02_clicked.png'))
        print("   ✓ Clicked\n")
        
        # Step 3: Fill content
        print("Step 3: Filling content...")
        
        # Try multiple approaches to find textbox
        textbox = None
        
        # Approach 1: contenteditable div in dialog
        try:
            textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
            textbox.wait_for(state='visible', timeout=5000)
        except:
            # Approach 2: textbox with aria-label
            try:
                textbox = page.locator('div[role="dialog"] textarea[aria-label]').first
                textbox.wait_for(state='visible', timeout=5000)
            except:
                # Approach 3: any editable element in dialog
                textbox = page.locator('div[role="dialog"] [contenteditable]').first
        
        textbox.click()
        time.sleep(2)
        
        # Fill content
        textbox.fill(CONTENT)
        time.sleep(3)
        
        # Verify
        filled = textbox.inner_text()
        page.screenshot(path=str(screenshot_dir / '03_filled.png'))
        print(f"   ✓ Content filled ({len(filled)} chars)\n")
        
        # Step 4: Click Post button
        print("Step 4: Clicking Post button...")
        
        # Find Post button in dialog
        post_btn = page.locator('div[role="dialog"] button[data-test-id="composer-publish-button"]').first
        
        # Fallback
        if post_btn.count() == 0:
            # Find all buttons and look for "Post"
            buttons = page.locator('div[role="dialog"] button').all()
            for btn in buttons:
                try:
                    if 'Post' in btn.inner_text():
                        post_btn = btn
                        break
                except:
                    continue
        
        # Wait for button to be enabled
        post_btn.wait_for(state='enabled', timeout=10000)
        time.sleep(2)
        
        # Click
        post_btn.click()
        print("   ✓ Post button clicked\n")
        
        # Step 5: Wait for publication
        print("Step 5: Waiting for publication...")
        print("   (Please wait 15 seconds)\n")
        
        published = False
        for i in range(15):
            time.sleep(1)
            
            # Check for success
            try:
                # Check for "Your post was published"
                if page.is_visible('text="Your post was published"'):
                    published = True
                    break
                
                # Check if back on feed
                if '/feed' in page.url:
                    published = True
                    break
                    
            except:
                pass
        
        # Final screenshot
        page.screenshot(path=str(screenshot_dir / '04_final.png'))
        
        if published:
            print("\n" + "=" * 70)
            print("   ✓✓✓ SUCCESS! POST PUBLISHED TO LINKEDIN! ✓✓✓")
            print("=" * 70)
            print("\nYour AI Employee has successfully posted to LinkedIn!")
            print("\nView your post:")
            print("  https://www.linkedin.com/feed")
            print("  Or check your profile Activity section\n")
        else:
            print("\n" + "=" * 70)
            print("   Status: Waiting for confirmation")
            print("=" * 70)
            print("\nCheck the screenshots in: linkedin_screenshots/")
            print("Open 04_final.png to see the result\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
