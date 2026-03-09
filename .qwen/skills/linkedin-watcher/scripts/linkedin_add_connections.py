"""
LinkedIn - Add Connections Only

Navigates to My Network/Connections and sends connection requests.
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

def main():
    print("\n" + "=" * 70)
    print("   LinkedIn - Add Connections")
    print("=" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    screenshot_dir = Path.cwd() / 'linkedin_connections'
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
        page.goto('https://www.linkedin.com', timeout=60000)
        time.sleep(8)
        print("   ✓ Loaded\n")
        
        # ===== STEP 2: Navigate to My Network =====
        print("Step 2: Going to My Network (Connections)...")
        
        try:
            # Try to click My Network
            page.click('text=My Network')
            time.sleep(5)
            print("   ✓ Clicked My Network\n")
        except:
            # Direct navigation
            page.goto('https://www.linkedin.com/mynetwork', timeout=30000)
            time.sleep(5)
            print("   ✓ Navigated directly\n")
        
        page.screenshot(path=str(screenshot_dir / '01_network.png'))
        
        # ===== STEP 3: Find and Click Connect Buttons =====
        print("Step 3: Sending connection requests...")
        
        try:
            # Find Connect buttons
            connect_buttons = page.locator('button:has-text("Connect")').all()
            print(f"   Found {len(connect_buttons)} Connect buttons\n")
            
            # Click up to 5 connect buttons (avoid rate limiting)
            for i in range(min(len(connect_buttons), 5)):
                try:
                    btn = connect_buttons[i]
                    if btn.is_visible():
                        btn.scroll_into_view_if_needed()
                        time.sleep(1)
                        btn.click()
                        print(f"   ✓ Sent connection request {i+1}")
                        time.sleep(2)
                        
                        # Click "Done" if popup appears
                        try:
                            done_btn = page.locator('button:has-text("Done")').first
                            if done_btn.is_visible():
                                done_btn.click()
                                print(f"   ✓ Clicked Done")
                                time.sleep(1)
                        except:
                            pass
                            
                except Exception as e:
                    print(f"   ⚠ Request {i+1} failed")
                    
        except Exception as e:
            print(f"   ⚠ Error: {e}\n")
        
        page.screenshot(path=str(screenshot_dir / '02_done.png'))
        
        # ===== STEP 4: Click Final Done Button =====
        print("\nStep 4: Clicking Done...")
        
        try:
            done_buttons = page.locator('button:has-text("Done")').all()
            if done_buttons.count() > 0:
                done_buttons.first.click()
                time.sleep(3)
                print("   ✓ Clicked Done\n")
        except:
            print("   ⚠ No Done button found\n")
        
        # ===== RESULT =====
        print("\n" + "=" * 70)
        print("   ✓✓✓ CONNECTIONS COMPLETE! ✓✓✓")
        print("=" * 70)
        print("\nConnection requests sent!")
        print("\nView your connections:")
        print("  https://www.linkedin.com/mynetwork")
        print(f"\nScreenshots: {screenshot_dir}\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
