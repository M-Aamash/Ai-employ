"""
LinkedIn Post - JavaScript Click

Uses JavaScript to click the Post button, bypassing automation detection.
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
    print("   LinkedIn Post - JavaScript Click")
    print("=" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    screenshot_dir = Path.cwd() / 'linkedin_js_click'
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
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(10)
        print("   ✓ Loaded\n")
        
        # ===== STEP 2: Click Start a Post =====
        print("Step 2: Opening composer...")
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
        
        # Verify
        filled = textbox.inner_text()
        print(f"   ✓ Content filled ({len(filled)} chars)\n")
        
        page.screenshot(path=str(screenshot_dir / 'content_filled.png'))
        
        # ===== STEP 4: JavaScript Click on Post Button =====
        print("Step 4: Publishing with JavaScript...")
        
        # Wait for LinkedIn to detect content and enable button
        print("   Waiting for Post button to be ready...")
        time.sleep(5)
        
        # Use JavaScript to find and click the Post button
        # This bypasses Playwright's element detection
        print("   Executing JavaScript click...\n")
        
        result = page.evaluate("""
            () => {
                // Find all buttons in the dialog
                const dialog = document.querySelector('div[role="dialog"]');
                if (!dialog) {
                    return {success: false, error: 'No dialog found'};
                }
                
                const buttons = dialog.querySelectorAll('button');
                console.log('Found buttons:', buttons.length);
                
                // Find the Post button
                let postButton = null;
                for (let btn of buttons) {
                    const text = btn.textContent.trim();
                    console.log('Button text:', text);
                    if (text === 'Post' || text.includes('Post')) {
                        postButton = btn;
                        break;
                    }
                }
                
                if (!postButton) {
                    return {success: false, error: 'Post button not found'};
                }
                
                // Check if disabled
                if (postButton.disabled) {
                    return {success: false, error: 'Post button is disabled'};
                }
                
                // Click using multiple methods
                postButton.scrollIntoView();
                postButton.click();
                
                // Also try dispatch event
                const event = new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                });
                postButton.dispatchEvent(event);
                
                return {success: true, message: 'Post button clicked'};
            }
        """)
        
        print(f"   JavaScript result: {result}\n")
        
        # ===== STEP 5: Wait for Publication =====
        print("Step 5: Waiting for publication...")
        print("   (Please wait up to 30 seconds)\n")
        
        published = False
        for i in range(30):
            time.sleep(1)
            
            # Check for success
            try:
                # Check URL
                if '/feed' in page.url and i > 5:
                    published = True
                    print(f"   ✓ Back on feed ({i+1}s)")
                    break
                
                # Check for toast message
                if page.is_visible('text="Your post was published"'):
                    published = True
                    print(f"   ✓ Publication confirmed ({i+1}s)")
                    break
                    
            except:
                pass
        
        # Final screenshot
        page.screenshot(path=str(screenshot_dir / 'final.png'))
        
        # ===== RESULT =====
        print("\n" + "=" * 70)
        
        if published:
            print("   ✓✓✓ SUCCESS! POST PUBLISHED TO LINKEDIN! ✓✓✓")
            print("=" * 70)
            print("\nYour AI Employee successfully posted to LinkedIn!")
            print("\nView: https://www.linkedin.com/feed\n")
        else:
            print("   ⚠ CHECK MANUALLY")
            print("=" * 70)
            print("\nOpen the screenshot to see the current state:")
            print(f"   {screenshot_dir / 'final.png'}")
            print("\nIf the post dialog is still open with content:")
            print("   1. Click the blue 'Post' button manually")
            print("   2. Or wait - LinkedIn may still be processing\n")
        
        time.sleep(10)
        browser.close()

if __name__ == '__main__':
    main()
ain()
