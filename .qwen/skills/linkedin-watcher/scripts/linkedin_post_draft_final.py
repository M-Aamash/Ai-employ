"""
LinkedIn Post - Start a Post Button (Final)

Clicks "Start a Post" → Fill → Post → Connections only → Done → Post
Waits longer for confirmation.
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
    print("   LinkedIn Post - Start a Post Button (Final)")
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
        
        # Step 1: Open LinkedIn
        print("Step 1: Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(10)
        print("   ✓ Done\n")
        
        # Step 2: Click "Start a Post"
        print("Step 2: Clicking 'Start a Post'...")
        try:
            page.click('text=Start a Post')
            print("   ✓ Done\n")
            time.sleep(5)
        except:
            print("   ⚠ 'Start a Post' not found, trying 'Start a Post'...\n")
            try:
                page.click('text=Start a Post')
                print("   ✓ Done (Start a Post)\n")
                time.sleep(5)
            except:
                print("   ⚠ No button found\n")
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
        time.sleep(5)
        print("   ✓ Done\n")
        
        # Step 5: Connections only
        print("Step 5: Clicking 'Connections only'...")
        time.sleep(2)
        try:
            page.click('text=Connections only')
            print("   ✓ Done\n")
            time.sleep(3)
        except:
            print("   ⚠ Not found\n")
        
        # Step 6: Click Done
        print("Step 6: Clicking 'Done'...")
        time.sleep(3)
        try:
            page.click('button:has-text("Done")')
            print("   ✓ Done\n")
            time.sleep(3)
        except:
            print("   ⚠ Done not found\n")
        
        # Step 7: Click Post (final)
        print("Step 7: Clicking 'Post' (final)...")
        time.sleep(3)
        try:
            post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
            time.sleep(2)
            if post_btn.is_enabled():
                post_btn.click()
                print("   ✓ Done\n")
        except:
            print("   ⚠ Could not click\n")
        
        # Step 8: Wait longer for publication
        print("\nStep 8: Waiting for publication...")
        print("   (Waiting up to 60 seconds...)\n")
        
        published = False
        for i in range(60):
            time.sleep(1)
            try:
                # Check for "View post"
                if page.is_visible('text="View post"'):
                    published = True
                    print(f"   ✓ 'View post' found! ({i+1}s)\n")
                    break
                
                # Check for "Your post was published"
                if page.is_visible('text="Your post was published"'):
                    published = True
                    print(f"   ✓ Published! ({i+1}s)\n")
                    break
                
                # Check if on feed
                if '/feed' in page.url and i > 20:
                    content_check = page.content()
                    if 'AI-powered' in content_check or 'AI Employee' in content_check:
                        published = True
                        print(f"   ✓ Post visible! ({i+1}s)\n")
                        break
                        
            except:
                pass
        
        # Final screenshot
        screenshot_path = Path.cwd() / 'linkedin_final.png'
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved: {screenshot_path}\n")
        
        # Result
        print("=" * 70)
        if published:
            print("   ✓✓✓ SUCCESSFUL! ✓✓✓")
            print("=" * 70)
            print("\nYour post has been PUBLISHED to LinkedIn!")
            print("\nView: https://www.linkedin.com/feed\n")
        else:
            print("   ⚠ CHECK MANUALLY")
            print("=" * 70)
            print("\nCheck the screenshot or your LinkedIn feed.\n")
        
        time.sleep(10)
        browser.close()

if __name__ == '__main__':
    main()
