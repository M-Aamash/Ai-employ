"""
LinkedIn Post - Fixed Version

Handles Post settings popup, clicks Connections only, then publishes.
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
    print("   LinkedIn Post - Fixed (Connections Only)")
    print("=" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    screenshot_dir = Path.cwd() / 'linkedin_post_fixed'
    screenshot_dir.mkdir(exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        page = browser.pages[0]
        
        # ===== STEP 1: Open LinkedIn =====
        print("Step 1: Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000, wait_until='domcontentloaded')
        time.sleep(8)
        print("   ✓ Loaded\n")
        
        # ===== STEP 2: Click Start a Post =====
        print("Step 2: Clicking 'Start a Post'...")
        page.click('text=Start a Post')
        time.sleep(5)
        print("   ✓ Composer opened\n")
        
        # ===== STEP 3: Fill Content =====
        print("Step 3: Filling content...")
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.click()
        time.sleep(2)
        textbox.fill(CONTENT)
        time.sleep(5)
        print(f"   ✓ Content filled\n")
        
        page.screenshot(path=str(screenshot_dir / '01_content_filled.png'))
        
        # ===== STEP 4: Handle Post Settings Popup =====
        print("Step 4: Looking for Post settings...")
        time.sleep(3)
        
        # Check if Post settings popup appears
        try:
            # Look for "Anyone" or "Post settings" button
            settings_selectors = [
                'button:has-text("Anyone")',
                'button:has-text("Post settings")',
                'button[aria-label*="visibility"]'
            ]
            
            settings_btn = None
            for selector in settings_selectors:
                try:
                    elements = page.locator(selector)
                    if elements.count() > 0:
                        settings_btn = elements.first
                        print(f"   ✓ Found settings: {selector}")
                        break
                except:
                    continue
            
            if settings_btn:
                print("   Clicking Post settings...")
                settings_btn.click()
                time.sleep(3)
                
                # ===== STEP 5: Click Connections Only =====
                print("\nStep 5: Clicking 'Connections only'...")
                
                try:
                    # Look for "Connections" option in dropdown
                    connections_selectors = [
                        'text=Connections',
                        'text=Connections only',
                        'button:has-text("Connections")',
                        '[role="option"]:has-text("Connections")'
                    ]
                    
                    for selector in connections_selectors:
                        try:
                            elements = page.locator(selector)
                            if elements.count() > 0:
                                elements.first.click()
                                print(f"   ✓ Clicked: {selector}")
                                time.sleep(2)
                                break
                        except:
                            continue
                    
                    print("   ✓ Connections only selected\n")
                    
                except Exception as e:
                    print(f"   ⚠ Could not select Connections: {e}\n")
                    
        except Exception as e:
            print(f"   ⚠ No settings popup: {e}\n")
        
        page.screenshot(path=str(screenshot_dir / '02_settings_done.png'))
        
        # ===== STEP 6: Click Post Button =====
        print("Step 6: Publishing post...")
        
        # Find Post button
        post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
        
        # Wait for it to be enabled
        time.sleep(3)
        
        # Click Post
        post_btn.click()
        print("   ✓ Post button clicked\n")
        
        # ===== STEP 7: Wait for Publication =====
        print("Step 7: Waiting for publication...")
        
        published = False
        for i in range(25):
            time.sleep(1)
            
            # Check for success
            try:
                if '/feed' in page.url:
                    published = True
                    print(f"   ✓ Back on feed ({i+1}s)")
                    break
                    
                if page.is_visible('text="Your post was published"'):
                    published = True
                    print(f"   ✓ Publication confirmed ({i+1}s)")
                    break
                    
            except:
                pass
        
        page.screenshot(path=str(screenshot_dir / '03_final.png'))
        
        # ===== RESULT =====
        print("\n" + "=" * 70)
        
        if published:
            print("   ✓✓✓ SUCCESS! POST PUBLISHED TO LINKEDIN! ✓✓✓")
            print("=" * 70)
            print("\nYour post is now live on LinkedIn!")
            print("\nView your post:")
            print("  https://www.linkedin.com/feed")
            print("\nOr check your profile Activity section\n")
        else:
            print("   ⚠ CHECK MANUALLY")
            print("=" * 70)
            print("\nCheck the screenshot:")
            print(f"  {screenshot_dir / '03_final.png'}")
            print("\nIf the post dialog is still open:")
            print("  1. Make sure 'Connections' is selected in Post settings")
            print("  2. Click the blue 'Post' button manually\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
ain()
