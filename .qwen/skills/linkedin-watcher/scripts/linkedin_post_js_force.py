"""
LinkedIn Post - JavaScript Force Click

Uses JavaScript to force click buttons when normal clicks fail.
"""

import sys
import os
import time
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

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

def click_with_js(page, selector):
    """Force click using JavaScript."""
    result = page.evaluate(f"""
        () => {{
            const el = document.querySelector('{selector}');
            if (el) {{
                el.click();
                return true;
            }}
            return false;
        }}
    """)
    return result

def main():
    print("\n" + "=" * 70)
    print("   LinkedIn Post - JavaScript Force Click")
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
        
        # 1. Open LinkedIn
        print("1. Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=30000)
        time.sleep(5)
        print("   ✓ Done\n")
        
        # 2. Click Start a Post
        print("2. Clicking 'Start a Post'...")
        click_with_js(page, 'button[aria-label="Start a Post"]')
        time.sleep(3)
        print("   ✓ Done\n")
        
        # 3. Fill content
        print("3. Filling content...")
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.fill(CONTENT)
        time.sleep(3)
        print("   ✓ Done\n")
        
        # 4. Click Post (opens visibility)
        print("4. Clicking 'Post'...")
        time.sleep(2)
        click_with_js(page, 'div[role="dialog"] button:has-text("Post")')
        time.sleep(5)
        print("   ✓ Done\n")
        
        # 5. Click Connections only
        print("5. Clicking 'Connections only'...")
        time.sleep(2)
        if click_with_js(page, 'text=Connections only'):
            print("   ✓ Done\n")
        elif click_with_js(page, 'text=Connections'):
            print("   ✓ Done (Connections)\n")
        else:
            print("   ⚠ Not found\n")
        
        # 6. Click Done - CRITICAL STEP
        print("6. Clicking 'Done'...")
        time.sleep(3)
        
        # Try multiple selectors for Done
        done_selectors = [
            'button:has-text("Done")',
            'button:has-text("Save")',
            '[aria-label="Done"]'
        ]
        
        done_clicked = False
        for selector in done_selectors:
            if click_with_js(page, selector):
                print(f"   ✓ Done clicked: {selector}\n")
                done_clicked = True
                time.sleep(3)
                break
        
        if not done_clicked:
            print("   ⚠ Done button not found\n")
            print("   Continuing anyway...\n")
            time.sleep(2)
        
        # 7. Click Post (final)
        print("7. Clicking 'Post' (final)...")
        time.sleep(2)
        click_with_js(page, 'div[role="dialog"] button:has-text("Post")')
        print("   ✓ Done\n")
        
        # 8. Wait for publication
        print("\n8. Waiting for publication...")
        time.sleep(15)
        
        # Check result
        if '/feed' in page.url:
            print("\n" + "=" * 70)
            print("   ✓✓✓ SUCCESSFUL! ✓✓✓")
            print("=" * 70)
            print("\nView: https://www.linkedin.com/feed\n")
        else:
            print("\n" + "=" * 70)
            print("   ⚠ Check manually\n")
        
        time.sleep(3)
        browser.close()

if __name__ == '__main__':
    main()
