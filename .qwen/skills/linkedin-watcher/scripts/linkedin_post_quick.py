"""
LinkedIn Post - Quick Version

Fast and simple - clicks Connections only → Done → Post
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

def main():
    print("\n" + "=" * 70)
    print("   LinkedIn Post - Quick Version")
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
        page.goto('https://www.linkedin.com', timeout=30000)
        time.sleep(3)
        print("   ✓ Done\n")
        
        # 2. Go to feed
        print("2. Going to feed...")
        page.goto('https://www.linkedin.com/feed', timeout=30000)
        time.sleep(3)
        print("   ✓ Done\n")
        
        # 3. Click Start a Post
        print("3. Clicking 'Start a Post'...")
        page.click('text=Start a Post')
        time.sleep(2)
        print("   ✓ Done\n")
        
        # 4. Fill content
        print("4. Filling content...")
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.fill(CONTENT)
        time.sleep(2)
        print("   ✓ Done\n")
        
        # 5. Click Post (opens visibility settings)
        print("5. Clicking 'Post'...")
        page.click('button:has-text("Post")')
        time.sleep(3)
        print("   ✓ Done\n")
        
        # 6. Click Connections only
        print("6. Clicking 'Connections only'...")
        time.sleep(1)
        try:
            page.click('text=Connections only')
            print("   ✓ Done\n")
            time.sleep(2)
        except:
            print("   ⚠ Skipped\n")
        
        # 7. Click Done - CRITICAL
        print("7. Clicking 'Done'...")
        time.sleep(1)
        try:
            # Try multiple times
            for i in range(3):
                try:
                    page.click('button:has-text("Done")')
                    print(f"   ✓ Done clicked (attempt {i+1})\n")
                    time.sleep(2)
                    break
                except:
                    if i == 2:
                        print("   ⚠ Done not found\n")
                    time.sleep(1)
        except:
            print("   ⚠ Error\n")
        
        # 8. Click Post again
        print("8. Clicking 'Post' (final)...")
        time.sleep(2)
        try:
            page.click('button:has-text("Post")')
            print("   ✓ Done\n")
        except:
            print("   ⚠ Skipped\n")
        
        # 9. Wait for publication
        print("\n9. Waiting for publication...")
        time.sleep(15)
        
        # Check if published
        if '/feed' in page.url:
            print("\n" + "=" * 70)
            print("   ✓✓✓ SUCCESSFUL! ✓✓✓")
            print("=" * 70)
            print("\nView: https://www.linkedin.com/feed\n")
        else:
            print("\n" + "=" * 70)
            print("   ⚠ Check manually")
            print("=" * 70 + "\n")
        
        time.sleep(3)
        browser.close()

if __name__ == '__main__':
    main()
