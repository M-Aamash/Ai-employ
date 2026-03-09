"""
LinkedIn Post - Direct Post (No Settings Popup)

Posts directly like a human would - no "Post settings" popup.
Uses natural timing and keyboard interactions.
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
    print("   LinkedIn Post - Direct Post (Human-like)")
    print("=" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        
        page = browser.pages[0]
        
        # Remove automation detection
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)
        
        # ===== STEP 1: Open LinkedIn =====
        print("Step 1: Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(8)  # Natural delay
        print("   ✓ Done\n")
        
        # ===== STEP 2: Click "Start a Post" =====
        print("Step 2: Clicking 'Start a Post'...")
        
        # Use text selector (most reliable)
        page.click('text=Start a Post')
        time.sleep(3)  # Natural delay
        print("   ✓ Done\n")
        
        # ===== STEP 3: Fill Content =====
        print("Step 3: Filling content...")
        
        # Find textbox
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        
        # Click to focus (like human)
        textbox.click()
        time.sleep(2)
        
        # Fill content (use fill for reliability)
        textbox.fill(CONTENT)
        time.sleep(5)  # Wait for LinkedIn to detect content
        
        # Press Enter twice (like human finishing typing)
        textbox.press('Enter')
        time.sleep(0.5)
        textbox.press('Enter')
        time.sleep(3)
        
        print(f"   ✓ Content filled ({len(CONTENT)} chars)\n")
        
        # ===== STEP 4: Click Post Directly =====
        print("Step 4: Clicking 'Post' (direct publish)...")
        
        # Wait for Post button to be ready (LinkedIn enables it after content detected)
        time.sleep(2)
        
        # Find Post button
        post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
        
        # Scroll into view (like human would)
        post_btn.scroll_into_view_if_needed()
        time.sleep(1)
        
        # Click Post button
        post_btn.click()
        print("   ✓ Post button clicked\n")
        
        # ===== STEP 5: Wait for Publication =====
        print("Step 5: Waiting for publication...")
        
        published = False
        for i in range(30):
            time.sleep(1)
            
            try:
                # Check for "View post" (definitive confirmation)
                if page.is_visible('text="View post"'):
                    published = True
                    print(f"   ✓ 'View post' confirmed! ({i+1}s)\n")
                    break
                
                # Check for "Your post was published"
                if page.is_visible('text="Your post was published"'):
                    published = True
                    print(f"   ✓ Published! ({i+1}s)\n")
                    break
                
                # Check if back on feed with our content
                if '/feed' in page.url and i > 5:
                    content_check = page.content()
                    if 'AI-powered' in content_check or 'AI Employee' in content_check:
                        published = True
                        print(f"   ✓ Post visible in feed! ({i+1}s)\n")
                        break
                        
            except:
                pass
        
        # ===== FINAL RESULT =====
        print("=" * 70)
        
        if published:
            print("   ✓✓✓ SUCCESSFUL! ✓✓✓")
            print("=" * 70)
            print("\nYour post has been PUBLISHED to LinkedIn!")
            print("\nView: https://www.linkedin.com/feed\n")
        else:
            print("   ⚠ CHECK MANUALLY")
            print("=" * 70)
            print("\nCheck your LinkedIn feed\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
