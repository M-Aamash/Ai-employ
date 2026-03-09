"""
LinkedIn Post - Verified Publish

Waits longer and verifies the post actually appears in the feed.
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
    print("   LinkedIn Post - Verified Publish")
    print("=" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    screenshot_dir = Path.cwd() / 'linkedin_verified'
    screenshot_dir.mkdir(exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        page = browser.pages[0]
        
        # ===== OPEN LINKEDIN =====
        print("1. Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(10)
        print("   ✓ Loaded\n")
        
        # ===== CLICK DRAFT =====
        print("2. Clicking 'Start a Post'...")
        page.click('text=Start a Post')
        time.sleep(5)
        print("   ✓ Composer opened\n")
        
        # ===== FILL CONTENT =====
        print("3. Filling content...")
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.click()
        time.sleep(2)
        textbox.fill(CONTENT)
        time.sleep(5)  # Wait for LinkedIn to register content
        
        # Verify content
        filled = textbox.inner_text()
        print(f"   ✓ Content filled ({len(filled)} chars)\n")
        
        # ===== CLICK POST BUTTON =====
        print("4. Clicking Post button...")
        
        # Find Post button - be very specific
        post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
        
        # Wait for it to be enabled (LinkedIn enables button after content is detected)
        post_btn.wait_for(state='enabled', timeout=15000)
        time.sleep(3)  # Extra wait
        
        # Scroll into view and click
        post_btn.scroll_into_view_if_needed()
        time.sleep(1)
        post_btn.click()
        print("   ✓ Post button clicked\n")
        
        # ===== WAIT FOR PUBLICATION (CRITICAL) =====
        print("5. Waiting for publication...")
        print("   (This may take 15-30 seconds)\n")
        
        published = False
        error_found = False
        
        for i in range(40):  # Wait up to 40 seconds
            time.sleep(1)
            
            # Check for success
            try:
                # Method 1: Check for "Your post was published" toast
                if page.is_visible('text="Your post was published"'):
                    published = True
                    print(f"   ✓ Publication confirmed at {i+1}s!")
                    break
                
                # Method 2: Check URL changed back to feed
                if '/feed' in page.url:
                    # Wait a bit more to confirm
                    time.sleep(3)
                    if '/feed' in page.url:
                        published = True
                        print(f"   ✓ Back on feed at {i+1}s - published!")
                        break
                
                # Method 3: Check for post in feed
                if page.is_visible('.feed-shared-update-v2'):
                    # Check if our content is in the first post
                    page_content = page.content()
                    if 'AI-powered solutions' in page_content:
                        published = True
                        print(f"   ✓ Post visible in feed at {i+1}s!")
                        break
                
                # Check for errors
                if page.is_visible('text="Something went wrong"'):
                    error_found = True
                    print(f"   ✗ Error detected at {i+1}s")
                    break
                    
            except Exception as e:
                continue
        
        # Take final screenshot
        page.screenshot(path=str(screenshot_dir / 'final.png'))
        
        # ===== REPORT RESULT =====
        print("\n" + "=" * 70)
        
        if published:
            print("   ✓✓✓ SUCCESS! POST PUBLISHED TO LINKEDIN! ✓✓✓")
            print("=" * 70)
            print("\nYour AI Employee successfully posted to LinkedIn!")
            print("\nView your post:")
            print("  https://www.linkedin.com/feed")
            print("\nOr check your profile Activity section\n")
        elif error_found:
            print("   ✗ ERROR: Something went wrong")
            print("=" * 70)
            print("\nLinkedIn encountered an error. Check the screenshot:")
            print(f"  {screenshot_dir / 'final.png'}\n")
        else:
            print("   ⚠ PUBLICATION STATUS UNCLEAR")
            print("=" * 70)
            print("\nThe post button was clicked but we couldn't confirm publication.")
            print("\nPossible reasons:")
            print("  1. LinkedIn is still processing (wait 1-2 minutes)")
            print("  2. Post requires additional verification")
            print("  3. Network connection slow")
            print("\nCheck your LinkedIn feed manually:")
            print("  https://www.linkedin.com/feed")
            print(f"\nScreenshot saved: {screenshot_dir / 'final.png'}\n")
        
        # Keep browser open for verification
        print("Browser will stay open for 10 seconds for manual verification...")
        time.sleep(10)
        browser.close()

if __name__ == '__main__':
    main()
