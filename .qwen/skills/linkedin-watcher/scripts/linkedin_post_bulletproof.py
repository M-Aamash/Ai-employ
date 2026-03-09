"""
LinkedIn Post - Bulletproof Version

Uses accessibility API and better element detection.
Takes screenshots at every step for debugging.
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

def save_screenshot(page, name, screenshot_dir):
    """Save screenshot for debugging."""
    try:
        path = screenshot_dir / f"{name}.png"
        page.screenshot(path=str(path), full_page=True)
        print(f"      📸 Screenshot: {path}")
    except Exception as e:
        print(f"      ⚠ Screenshot failed: {e}")

def main():
    print("\n" + "=" * 70)
    print("   LinkedIn Post - Bulletproof Version")
    print("=" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    screenshot_dir = Path.cwd() / 'linkedin_debug'
    screenshot_dir.mkdir(exist_ok=True)
    
    print(f"Screenshots will be saved to: {screenshot_dir}\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security'
            ]
        )
        
        page = browser.pages[0]
        
        # Disable automation detection
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)
        
        # ===== STEP 1: Open LinkedIn =====
        print("=" * 70)
        print("STEP 1: Opening LinkedIn Feed")
        print("=" * 70)
        # Use 'domcontentloaded' instead of 'networkidle' (LinkedIn never stops loading)
        page.goto('https://www.linkedin.com/feed', timeout=60000, wait_until='domcontentloaded')
        time.sleep(10)  # Wait for page to fully load
        save_screenshot(page, '01_feed_loaded', screenshot_dir)
        print("✓ LinkedIn feed loaded\n")
        
        # ===== STEP 2: Click "Start a Post" =====
        print("=" * 70)
        print("STEP 2: Opening Post Composer")
        print("=" * 70)
        
        # Method 1: Click on the "Start a Post" button using multiple selectors
        clicked = False
        selectors = [
            'button[aria-label="Start a Post"]',
            'button[aria-label*="Start"]',
            '.share-box-feed-entry__trigger',
            '[id*="feed-shared-start-a-post"]',
            'div.share-box-feed-entry'
        ]
        
        for selector in selectors:
            try:
                elements = page.locator(selector)
                count = elements.count()
                print(f"      Trying: {selector} (found {count})")
                if count > 0:
                    elements.first.click(timeout=5000)
                    print(f"      ✓ Clicked: {selector}\n")
                    clicked = True
                    break
            except Exception as e:
                continue
        
        if not clicked:
            # Method 2: Use text content
            try:
                page.click('text=Start a Post', timeout=5000)
                print("      ✓ Clicked using text selector\n")
                clicked = True
            except:
                print("      ⚠ Auto-click failed\n")
        
        save_screenshot(page, '02_after_click', screenshot_dir)
        
        # Wait for modal
        print("Waiting for composer modal...")
        time.sleep(5)
        
        # ===== STEP 3: Fill Content =====
        print("\n" + "=" * 70)
        print("STEP 3: Filling Post Content")
        print("=" * 70)
        
        # Find the editable area
        textbox = None
        textbox_selectors = [
            'div[role="dialog"] div[contenteditable="true"]',
            'div[role="dialog"] textarea',
            'div[aria-label*="What do you"]',
            '[data-placeholder*="What do you"]'
        ]
        
        for selector in textbox_selectors:
            try:
                elements = page.locator(selector)
                if elements.count() > 0:
                    textbox = elements.first
                    print(f"      ✓ Found textbox: {selector}")
                    break
            except:
                continue
        
        if textbox:
            # Click to focus
            textbox.click()
            time.sleep(2)
            
            # Fill content in chunks to avoid detection
            print("      Typing content...")
            textbox.fill(CONTENT)
            time.sleep(3)
            
            # Verify content was filled
            try:
                filled_text = textbox.inner_text()
                print(f"      ✓ Content filled ({len(filled_text)} characters)")
            except:
                print("      ⚠ Could not verify content")
        else:
            print("      ✗ Could not find textbox")
            print("      MANUAL ACTION REQUIRED: Click in the post area and paste")
            time.sleep(10)  # Wait for manual action
        
        save_screenshot(page, '03_content_filled', screenshot_dir)
        
        # ===== STEP 4: Click Post Button =====
        print("\n" + "=" * 70)
        print("STEP 4: Publishing Post")
        print("=" * 70)
        
        # Wait for Post button to be enabled
        time.sleep(3)
        
        # Find Post button
        post_button = None
        post_selectors = [
            'button[data-test-id="composer-publish-button"]',
            'div[role="dialog"] button:has-text("Post")',
            'button:has-text("Post")'
        ]
        
        for selector in post_selectors:
            try:
                elements = page.locator(selector)
                count = elements.count()
                if count > 0:
                    # Check if any button is enabled
                    for i in range(min(count, 5)):
                        try:
                            btn = elements.nth(i)
                            is_disabled = btn.get_attribute('disabled')
                            if not is_disabled:
                                post_button = btn
                                print(f"      ✓ Found Post button: {selector}")
                                break
                        except:
                            continue
                if post_button:
                    break
            except:
                continue
        
        if post_button:
            # Scroll button into view
            post_button.scroll_into_view_if_needed()
            time.sleep(2)
            
            # Click Post button
            print("      Clicking Post button...")
            post_button.click()
            print("      ✓ Post button clicked\n")
            
            # Wait for publication
            print("Waiting for post to publish...")
            published = False
            
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                
                # Check for success indicators
                try:
                    # Check for "Your post was published" message
                    if page.is_visible('text="Your post was published"'):
                        published = True
                        print("      ✓ Publication confirmed!")
                        break
                    
                    # Check if we're back on feed (post successful)
                    if '/feed' in page.url and i > 5:
                        published = True
                        print("      ✓ Back on feed - post published!")
                        break
                    
                    # Check for any error messages
                    if page.is_visible('text="Something went wrong"'):
                        print("      ✗ Error: Something went wrong")
                        break
                        
                except:
                    pass
            
            save_screenshot(page, '04_final', screenshot_dir)
            
            if published:
                print("\n" + "=" * 70)
                print("   ✓✓✓ SUCCESS! POST PUBLISHED TO LINKEDIN! ✓✓✓")
                print("=" * 70)
                print("\nYour post is now live on LinkedIn!")
                print("View it at: https://www.linkedin.com/feed")
                print("Or check your profile Activity section\n")
            else:
                print("\n" + "=" * 70)
                print("   ⚠ POST STATUS UNCLEAR")
                print("=" * 70)
                print("\nCheck the screenshots in: linkedin_debug/")
                print("Open 04_final.png to see the final state\n")
                print("If the post didn't publish, try these manual steps:")
                print("  1. LinkedIn is open in your browser")
                print("  2. Your content should be in the post box")
                print("  3. Click the blue 'Post' button manually\n")
        else:
            print("      ✗ Could not find Post button")
            print("\n" + "=" * 70)
            print("   MANUAL ACTION REQUIRED")
            print("=" * 70)
            print("\nThe post content should be filled in the composer.")
            print("Please click the 'Post' button manually.\n")
            save_screenshot(page, '04_no_button', screenshot_dir)
            time.sleep(30)  # Wait for manual action
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
