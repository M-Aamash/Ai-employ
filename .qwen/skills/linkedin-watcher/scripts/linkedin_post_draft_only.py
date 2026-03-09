"""
LinkedIn Post - Start a Post → Done → Post (FIXED)

Fixed flow based on screenshot:
1. Click "Start a Post"
2. Fill content
3. Click "Post"
4. Click "Connections only"
5. Click "Done" (it's enabled!)
6. Click "Post" (final publish)
7. Wait for "View post" confirmation
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
    print("   LinkedIn Post - Start a Post → Done → Post (FIXED)")
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
            page.wait_for_selector('text=Start a Post', timeout=30000)
            page.click('text=Start a Post')
            print("   ✓ Done\n")
            time.sleep(5)
        except:
            print("   ⚠ 'Start a Post' not found\n")
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
        except:
            print("   ⚠ Error\n")
            browser.close()
            return
        
        # Step 4: Click "Post"
        print("Step 4: Clicking 'Post'...")
        try:
            post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
            time.sleep(3)
            post_btn.click()
            print("   ✓ Done\n")
            time.sleep(5)
        except:
            print("   ⚠ Error\n")
        
        # Step 5: Click "Connections only"
        print("Step 5: Clicking 'Connections only'...")
        time.sleep(3)
        try:
            page.click('text=Connections only')
            print("   ✓ Done\n")
            time.sleep(5)  # Wait for Done button to enable
        except:
            print("   ⚠ Not found\n")
        
        # Step 6: Click "Done" (IT'S ENABLED NOW!)
        print("Step 6: Clicking 'Done'...")
        time.sleep(3)
        try:
            # Wait for Done button to be enabled (blue)
            done_btn = page.locator('button:has-text("Done")').first
            done_btn.wait_for(state='enabled', timeout=10000)
            done_btn.click()
            print("   ✓ Done\n")
            time.sleep(3)
        except:
            print("   ⚠ Done not enabled\n")
        
        # Step 7: Click "Post" (final publish)
        print("Step 7: Clicking 'Post' (final publish)...")
        time.sleep(3)
        try:
            post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
            time.sleep(2)
            if post_btn.is_enabled():
                post_btn.click()
                print("   ✓ Done\n")
            else:
                print("   ⚠ Post disabled\n")
        except:
            print("   ⚠ Could not click\n")
        
        # Step 8: Wait for publication
        print("\nStep 8: Waiting for publication...")
        print("   (Waiting for 'View post'...)\n")
        
        published = False
        for i in range(60):
            time.sleep(1)
            try:
                if page.is_visible('text="View post"'):
                    published = True
                    print(f"   ✓ 'View post' confirmed! ({i+1}s)\n")
                    break
                if page.is_visible('text="Your post was published"'):
                    published = True
                    print(f"   ✓ Published! ({i+1}s)\n")
                    break
                if '/feed' in page.url and i > 20:
                    if 'AI-powered' in page.content():
                        published = True
                        print(f"   ✓ Post visible! ({i+1}s)\n")
                        break
            except:
                pass
        
        # Screenshot
        page.screenshot(path='linkedin_draft_final.png')
        
        # Result
        print("=" * 70)
        if published:
            print("   ✓✓✓ SUCCESSFUL! ✓✓✓")
            print("=" * 70)
            print("\nYour post has been PUBLISHED!")
            print("\nView: https://www.linkedin.com/feed\n")
        else:
            print("   ⚠ CHECK MANUALLY")
            print("=" * 70 + "\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
