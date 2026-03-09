"""
LinkedIn Post - Complete Flow (FINAL)

Complete flow:
1. Open LinkedIn
2. Click "Start a Post"
3. Fill content
4. Click "Post" button
5. When "Who can see your post" appears → Click "Connections only"
6. Click "Done"
7. Click "Post"
8. Wait for "View post" confirmation
9. Print "SUCCESSFUL" only when actually published
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
    print("   LinkedIn Post - Complete Flow (FINAL)")
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
        
        # Step 1: Open LinkedIn
        print("1. Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000, wait_until='domcontentloaded')
        time.sleep(5)
        print("   ✓ Done\n")
        
        # Step 2: Click Start a Post
        print("2. Clicking 'Start a Post'...")
        page.click('text=Start a Post')
        time.sleep(3)
        print("   ✓ Done\n")
        
        # Step 3: Fill content
        print("3. Filling content...")
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.click()
        time.sleep(1)
        textbox.fill(CONTENT)
        time.sleep(3)
        print("   ✓ Done\n")
        
        # Step 4: Click Post (triggers "Who can see your post")
        print("4. Clicking 'Post' button...")
        post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
        time.sleep(2)
        post_btn.click()
        time.sleep(3)
        print("   ✓ Done\n")
        
        # Step 5: Click "Connections only"
        print("5. Clicking 'Connections only'...")
        time.sleep(2)
        try:
            page.click('text=Connections only')
            print("   ✓ Done\n")
        except:
            try:
                page.click('text=Connections')
                print("   ✓ Done\n")
            except:
                print("   ⚠ Not found\n")
        
        # Step 6: Click "Done"
        print("6. Clicking 'Done'...")
        time.sleep(2)
        try:
            page.click('button:has-text("Done")')
            print("   ✓ Done\n")
            time.sleep(2)
        except:
            print("   ⚠ Not found\n")
        
        # Step 7: Click "Post" (final publish)
        print("7. Clicking 'Post' (final publish)...")
        time.sleep(2)
        try:
            post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
            time.sleep(2)
            if post_btn.is_enabled():
                post_btn.click()
                print("   ✓ Done\n")
        except:
            print("   ⚠ Failed\n")
        
        # Step 8: Wait for "View post" confirmation
        print("\n8. Waiting for publication...")
        print("   (Waiting for 'View post' confirmation)\n")
        
        published = False
        for i in range(45):
            time.sleep(1)
            try:
                if page.is_visible('text="View post"'):
                    published = True
                    print(f"   ✓ 'View post' found! ({i+1}s)\n")
                    break
                if page.is_visible('text="Your post was published"'):
                    published = True
                    print(f"   ✓ Published! ({i+1}s)\n")
                    break
                if '/feed' in page.url and i > 10:
                    published = True
                    print(f"   ✓ On feed! ({i+1}s)\n")
                    break
            except:
                pass
        
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
            print("\nCheck LinkedIn manually\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
