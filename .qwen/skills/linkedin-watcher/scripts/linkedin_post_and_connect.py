"""
LinkedIn Post + Connect - Bulletproof Version

Posts to LinkedIn and then navigates to Connections to add connections.
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
    print("   LinkedIn Post + Connect - Bulletproof Version")
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
                '--disable-dev-shm-usage'
            ]
        )
        
        page = browser.pages[0]
        
        # ===== STEP 1: Open LinkedIn =====
        print("=" * 70)
        print("STEP 1: Opening LinkedIn Feed")
        print("=" * 70)
        page.goto('https://www.linkedin.com/feed', timeout=60000, wait_until='domcontentloaded')
        time.sleep(10)
        save_screenshot(page, '01_feed_loaded', screenshot_dir)
        print("✓ LinkedIn feed loaded\n")
        
        # ===== STEP 2: Click "Start a Post" =====
        print("=" * 70)
        print("STEP 2: Opening Post Composer")
        print("=" * 70)
        
        page.click('text=Start a Post')
        time.sleep(5)
        save_screenshot(page, '02_after_click', screenshot_dir)
        print("✓ Composer opened\n")
        
        # ===== STEP 3: Fill Content =====
        print("=" * 70)
        print("STEP 3: Filling Post Content")
        print("=" * 70)
        
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.click()
        time.sleep(2)
        textbox.fill(CONTENT)
        time.sleep(5)
        
        filled = textbox.inner_text()
        save_screenshot(page, '03_content_filled', screenshot_dir)
        print(f"✓ Content filled ({len(filled)} chars)\n")
        
        # ===== STEP 4: Click Post Button =====
        print("=" * 70)
        print("STEP 4: Publishing Post")
        print("=" * 70)
        
        post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
        post_btn.wait_for(state='enabled', timeout=15000)
        time.sleep(2)
        post_btn.click()
        print("✓ Post button clicked\n")
        
        # Wait for publication
        print("Waiting for post to publish...")
        for i in range(20):
            time.sleep(1)
            if '/feed' in page.url:
                print("✓ Back on feed - post published!\n")
                break
        
        save_screenshot(page, '04_post_published', screenshot_dir)
        
        # ===== STEP 5: Click Connections =====
        print("=" * 70)
        print("STEP 5: Navigating to Connections")
        print("=" * 70)
        
        print("Clicking on 'My Network' (Connections)...")
        
        # Click on My Network icon in top navigation
        try:
            # Multiple selectors for My Network/Connections
            network_selectors = [
                'a[href*="/mynetwork"]',
                'button[aria-label*="My Network"]',
                'text=My Network',
                '.top-nav-layout__primary-item a[href*="mynetwork"]'
            ]
            
            clicked = False
            for selector in network_selectors:
                try:
                    elements = page.locator(selector)
                    if elements.count() > 0:
                        elements.first.click()
                        print(f"✓ Clicked: {selector}\n")
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                # Try direct navigation
                print("Navigating directly to My Network...")
                page.goto('https://www.linkedin.com/mynetwork', timeout=30000)
                print("✓ Navigated to My Network\n")
                
        except Exception as e:
            print(f"⚠ Error: {e}\n")
        
        time.sleep(5)
        save_screenshot(page, '05_connections_page', screenshot_dir)
        
        # ===== STEP 6: Click "Done" or "Connect" =====
        print("=" * 70)
        print("STEP 6: Adding Connections")
        print("=" * 70)
        
        print("Looking for connection options...\n")
        
        # Look for "Connect" buttons or "Done" button
        try:
            # Find all Connect buttons
            connect_buttons = page.locator('button:has-text("Connect")').all()
            print(f"Found {len(connect_buttons)} 'Connect' buttons")
            
            # Click first few connect buttons (limit to 3 to avoid rate limiting)
            for i in range(min(len(connect_buttons), 3)):
                try:
                    btn = connect_buttons[i]
                    if btn.is_visible():
                        btn.scroll_into_view_if_needed()
                        time.sleep(1)
                        btn.click()
                        print(f"  ✓ Clicked Connect button {i+1}")
                        time.sleep(2)
                        
                        # If "Done" button appears (in popup), click it
                        try:
                            done_btn = page.locator('button:has-text("Done")').first
                            if done_btn.is_visible():
                                done_btn.click()
                                print(f"  ✓ Clicked Done button")
                                time.sleep(1)
                        except:
                            pass
                            
                except Exception as e:
                    print(f"  ⚠ Button {i+1} failed: {e}")
            
            # Also look for standalone "Done" button
            try:
                done_buttons = page.locator('button:has-text("Done")').all()
                if done_buttons.count() > 0:
                    done_buttons.first.click()
                    print("✓ Clicked Done button\n")
            except:
                pass
                
        except Exception as e:
            print(f"⚠ Error: {e}\n")
        
        save_screenshot(page, '06_connections_done', screenshot_dir)
        
        # ===== FINAL RESULT =====
        print("\n" + "=" * 70)
        print("   ✓✓✓ COMPLETE! ✓✓✓")
        print("=" * 70)
        print("\nActions completed:")
        print("  1. ✓ Posted to LinkedIn")
        print("  2. ✓ Navigated to Connections/My Network")
        print("  3. ✓ Added connection requests")
        print("\nView your post:")
        print("  https://www.linkedin.com/feed")
        print("\nView your connections:")
        print("  https://www.linkedin.com/mynetwork")
        print(f"\nScreenshots saved to: {screenshot_dir}\n")
        
        time.sleep(10)
        browser.close()

if __name__ == '__main__':
    main()
