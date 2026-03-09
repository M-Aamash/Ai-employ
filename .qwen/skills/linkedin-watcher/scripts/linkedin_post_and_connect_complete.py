"""
LinkedIn - Post and Connect

Complete automation: Posts to LinkedIn AND adds connections.
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
    print("   LinkedIn - Post and Connect")
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
        
        # ========== POST TO LINKEDIN ==========
        print("=" * 70)
        print("   PART 1: POST TO LINKEDIN")
        print("=" * 70 + "\n")
        
        # Open LinkedIn
        print("1. Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000, wait_until='domcontentloaded')
        time.sleep(8)
        print("   ✓ Loaded\n")
        
        # Click Start a Post
        print("2. Clicking 'Start a Post'...")
        page.click('text=Start a Post')
        time.sleep(5)
        print("   ✓ Composer opened\n")
        
        # Fill content
        print("3. Filling content...")
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.click()
        time.sleep(2)
        textbox.fill(CONTENT)
        time.sleep(5)
        print(f"   ✓ Content filled\n")
        
        # Click Post
        print("4. Publishing...")
        post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
        time.sleep(3)
        post_btn.click()
        time.sleep(10)
        print("   ✓ Post published\n")
        
        # ========== ADD CONNECTIONS ==========
        print("=" * 70)
        print("   PART 2: ADD CONNECTIONS")
        print("=" * 70 + "\n")
        
        # Go to My Network
        print("5. Going to My Network...")
        try:
            page.click('text=My Network')
            time.sleep(5)
            print("   ✓ My Network opened\n")
        except:
            page.goto('https://www.linkedin.com/mynetwork', timeout=30000)
            time.sleep(5)
            print("   ✓ Navigated\n")
        
        # Click Connect buttons
        print("6. Sending connection requests...")
        try:
            connect_buttons = page.locator('button:has-text("Connect")').all()
            print(f"   Found {len(connect_buttons)} Connect buttons")
            
            for i in range(min(len(connect_buttons), 5)):
                try:
                    btn = connect_buttons[i]
                    if btn.is_visible():
                        btn.click()
                        time.sleep(2)
                        print(f"   ✓ Sent request {i+1}")
                        
                        # Click Done if appears
                        try:
                            done = page.locator('button:has-text("Done")').first
                            if done.is_visible():
                                done.click()
                                time.sleep(1)
                        except:
                            pass
                except:
                    continue
                    
            print()
        except Exception as e:
            print(f"   ⚠ Error: {e}\n")
        
        # Click final Done
        print("7. Clicking Done...")
        try:
            done = page.locator('button:has-text("Done")').first
            done.click()
            time.sleep(3)
            print("   ✓ Done\n")
        except:
            print("   ⚠ Done button not found\n")
        
        # ========== COMPLETE ==========
        print("=" * 70)
        print("   ✓✓✓ COMPLETE! ✓✓✓")
        print("=" * 70)
        print("\nCompleted actions:")
        print("  1. ✓ Posted to LinkedIn")
        print("  2. ✓ Sent connection requests")
        print("\nView your post:")
        print("  https://www.linkedin.com/feed")
        print("\nView your connections:")
        print("  https://www.linkedin.com/mynetwork\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
