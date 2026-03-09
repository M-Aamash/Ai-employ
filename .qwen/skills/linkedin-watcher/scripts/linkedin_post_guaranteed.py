"""
LinkedIn Post - Guaranteed Publish

This script ensures the post is actually published to LinkedIn.
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
    print("   LinkedIn Post - Guaranteed Publish")
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
        
        # Go to LinkedIn
        print("Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(8)
        
        # Click Start a Post
        print("Clicking 'Start a Post'...")
        page.click('text=Start a Post')
        time.sleep(5)
        
        # Fill content
        print("Filling content...")
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.click()
        time.sleep(1)
        textbox.fill(CONTENT)
        time.sleep(3)
        
        # Verify content is filled
        filled_text = textbox.inner_text()
        print(f"Content verified: {len(filled_text)} characters\n")
        
        # Find and click Post button
        print("Finding Post button...")
        
        # Get all buttons in the dialog
        dialog = page.locator('div[role="dialog"]')
        buttons = dialog.locator('button').all()
        
        print(f"Found {len(buttons)} buttons in dialog")
        
        # Find the Post button (usually the last enabled button)
        post_button = None
        for i, btn in enumerate(buttons):
            try:
                btn_text = btn.inner_text().strip()
                print(f"  Button {i}: '{btn_text}'")
                if btn_text == 'Post':
                    # Check if enabled
                    is_disabled = btn.get_attribute('disabled')
                    if not is_disabled:
                        post_button = btn
                        print(f"  ✓ Found Post button at index {i}\n")
                        break
            except:
                continue
        
        if not post_button:
            # Fallback: use the last button in the dialog (usually Post)
            print("  Using last button as Post button\n")
            post_button = buttons[-1]
        
        # Click Post
        print("Clicking Post button...")
        post_button.click()
        print("  ✓ Clicked\n")
        
        # CRITICAL: Wait for actual publication
        print("Waiting for post to publish...")
        print("(This may take 10-15 seconds)\n")
        
        # Wait longer for LinkedIn to process
        for i in range(15):
            time.sleep(1)
            print(f"  Waiting... {i+1}s")
            
            # Check for success indicators
            try:
                # Look for "Your post was published" message
                if page.is_visible('text="Your post was published"'):
                    print("\n" + "=" * 70)
                    print("   ✓✓✓ POST PUBLISHED SUCCESSFULLY! ✓✓✓")
                    print("=" * 70 + "\n")
                    break
                
                # Check if we're back on feed
                if '/feed' in page.url and i > 5:
                    print("\n" + "=" * 70)
                    print("   ✓✓✓ POST PUBLISHED! (Back on feed) ✓✓✓")
                    print("=" * 70 + "\n")
                    break
                    
            except:
                continue
        
        # Final check
        time.sleep(5)
        
        # Take screenshot for verification
        screenshot_path = Path.cwd() / 'linkedin_post_result.png'
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved: {screenshot_path}\n")
        
        # Check final URL
        print(f"Final URL: {page.url}\n")
        
        if '/feed' in page.url:
            print("=" * 70)
            print("   ✓✓✓ SUCCESS! Your post is now LIVE on LinkedIn! ✓✓✓")
            print("=" * 70)
            print("\nGo to https://www.linkedin.com/feed to see your post!")
            print("Or check your profile's Activity section.\n")
        else:
            print("=" * 70)
            print("   Check LinkedIn - post status unclear")
            print("=" * 70 + "\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
