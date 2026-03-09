"""
LinkedIn Post - Click Done Properly

Fixed to properly click "Done" button after selecting "Connections only"
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
    print("   LinkedIn Post - Click Done Properly")
    print("=" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    screenshot_dir = Path.cwd() / 'linkedin_with_done'
    screenshot_dir.mkdir(exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        page = browser.pages[0]
        
        # Step 1: Open LinkedIn
        print("Step 1: Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000, wait_until='domcontentloaded')
        time.sleep(5)
        print("   ✓ Done\n")
        
        # Step 2: Click Start a Post
        print("Step 2: Clicking 'Start a Post'...")
        page.click('text=Start a Post')
        time.sleep(3)
        print("   ✓ Done\n")
        
        # Step 3: Fill content
        print("Step 3: Filling content...")
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.click()
        time.sleep(1)
        textbox.fill(CONTENT)
        time.sleep(3)
        print("   ✓ Done\n")
        
        page.screenshot(path=str(screenshot_dir / '01_content.png'))
        
        # Step 4: Click Post (triggers "Who can see your post")
        print("Step 4: Clicking 'Post' button...")
        post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
        time.sleep(2)
        post_btn.click()
        time.sleep(5)  # Wait for popup
        print("   ✓ Done\n")
        
        page.screenshot(path=str(screenshot_dir / '02_popup.png'))
        
        # Step 5: Click "Connections only"
        print("Step 5: Clicking 'Connections only'...")
        time.sleep(2)
        
        connections_clicked = False
        try:
            page.click('text=Connections only')
            connections_clicked = True
            print("   ✓ Clicked 'Connections only'\n")
        except:
            try:
                page.click('text=Connections')
                connections_clicked = True
                print("   ✓ Clicked 'Connections'\n")
            except:
                print("   ⚠ Could not find Connections option\n")
        
        page.screenshot(path=str(screenshot_dir / '03_connections.png'))
        
        # Step 6: Click "Done" - CRITICAL STEP
        print("Step 6: Clicking 'Done' button...")
        print("   (Waiting for Done button to appear...)\n")
        
        # Wait for Done button with multiple attempts
        done_clicked = False
        for attempt in range(5):
            time.sleep(2)
            print(f"   Attempt {attempt + 1}...")
            
            try:
                # Try multiple selectors for Done button
                done_selectors = [
                    'button:has-text("Done")',
                    'button:has-text("Save")',
                    '[aria-label="Done"]',
                    'button[data-test-id="done-button"]'
                ]
                
                for selector in done_selectors:
                    try:
                        elements = page.locator(selector)
                        if elements.count() > 0:
                            elements.first.scroll_into_view_if_needed()
                            time.sleep(1)
                            elements.first.click()
                            print(f"   ✓ Clicked: {selector}\n")
                            done_clicked = True
                            break
                    except:
                        continue
                
                if done_clicked:
                    break
                    
            except Exception as e:
                print(f"   ⚠ Attempt {attempt + 1} failed\n")
        
        if done_clicked:
            print("   ✓ 'Done' button clicked successfully!\n")
            time.sleep(3)
        else:
            print("   ⚠ Could not find 'Done' button\n")
            print("   Trying to proceed anyway...\n")
        
        page.screenshot(path=str(screenshot_dir / '04_done.png'))
        
        # Step 7: Click "Post" (final publish)
        print("Step 7: Clicking 'Post' (final publish)...")
        time.sleep(3)
        
        try:
            post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
            time.sleep(2)
            if post_btn.is_enabled():
                post_btn.click()
                print("   ✓ Post button clicked\n")
            else:
                print("   ⚠ Post button disabled\n")
        except:
            print("   ⚠ Could not click Post\n")
        
        page.screenshot(path=str(screenshot_dir / '05_post_clicked.png'))
        
        # Step 8: Wait for publication
        print("\nStep 8: Waiting for publication...")
        print("   (Waiting for 'View post' confirmation)\n")
        
        published = False
        for i in range(45):
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
                if '/feed' in page.url and i > 10:
                    content = page.content()
                    if 'AI-powered' in content or 'AI Employee' in content:
                        published = True
                        print(f"   ✓ Post visible! ({i+1}s)\n")
                        break
            except:
                pass
        
        page.screenshot(path=str(screenshot_dir / '06_final.png'))
        
        # Final result
        print("=" * 70)
        if published:
            print("   ✓✓✓ SUCCESSFUL! ✓✓✓")
            print("=" * 70)
            print("\nYour post has been PUBLISHED to LinkedIn!")
            print("\nView: https://www.linkedin.com/feed\n")
        else:
            print("   ⚠ NOT CONFIRMED")
            print("=" * 70)
            print("\nCheck screenshots:")
            print(f"   {screenshot_dir}\n")
            print("If dialog is still open, click 'Post' manually\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
