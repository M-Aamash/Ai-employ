"""
LinkedIn Post - Start a Post Button Version

Uses "Start a Post" button instead of "Start a Post".
Complete flow:
1. Open LinkedIn
2. Click "Start a Post"
3. Fill content
4. Click "Post"
5. Click "Connections only"
6. Click "Done"
7. Click "Post" (final publish)
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
    print("   LinkedIn Post - Start a Post Button Version")
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
        
        # ===== STEP 1: Open LinkedIn =====
        print("Step 1: Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(10)
        print("   ✓ Done\n")
        
        # ===== STEP 2: Click "Start a Post" =====
        print("Step 2: Clicking 'Start a Post'...")
        
        # Try "Start a Post" first, fallback to "Start a Post"
        draft_clicked = False
        
        # Try multiple Start a Post selectors
        draft_selectors = [
            'text=Start a Post',
            'button:has-text("Start a Post")',
            'button:has-text("Drafts")',
            '[aria-label*="Start a Post"]',
            'text=Drafts'
        ]
        
        for selector in draft_selectors:
            try:
                page.wait_for_selector(selector, timeout=5000)
                page.click(selector, timeout=5000)
                print(f"   ✓ Clicked: {selector}\n")
                draft_clicked = True
                time.sleep(5)
                break
            except:
                continue
        
        # Fallback to "Start a Post" if Start a Post not found
        if not draft_clicked:
            print("   ⚠ 'Start a Post' not found, trying 'Start a Post'...")
            try:
                page.wait_for_selector('text=Start a Post', timeout=10000)
                page.click('text=Start a Post', timeout=5000)
                print("   ✓ Clicked: Start a Post\n")
                draft_clicked = True
                time.sleep(5)
            except:
                print("   ⚠ Could not find post button\n")
        
        if not draft_clicked:
            print("   ⚠ No post button found. LinkedIn may have changed their UI.\n")
            browser.close()
            return
        
        # ===== STEP 3: Fill Content =====
        print("Step 3: Filling content...")
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.click()
        time.sleep(2)
        textbox.fill(CONTENT)
        time.sleep(5)
        print(f"   ✓ Done\n")
        
        # ===== STEP 4: Click "Post" (opens settings) =====
        print("Step 4: Clicking 'Post' button...")
        post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
        time.sleep(3)
        post_btn.click()
        time.sleep(5)
        print("   ✓ Done\n")
        
        # ===== STEP 5: Click "Connections only" =====
        print("Step 5: Clicking 'Connections only'...")
        time.sleep(2)
        try:
            page.click('text=Connections only')
            print("   ✓ Done\n")
            time.sleep(3)
        except:
            try:
                page.click('text=Connections')
                print("   ✓ Done (Connections)\n")
                time.sleep(3)
            except:
                print("   ⚠ Not found\n")
        
        # ===== STEP 6: Click "Done" =====
        print("Step 6: Clicking 'Done'...")
        time.sleep(3)
        try:
            page.click('button:has-text("Done")')
            print("   ✓ Done\n")
            time.sleep(3)
        except:
            print("   ⚠ Done button not found\n")
            time.sleep(2)
        
        # ===== STEP 7: Click "Post" (Final Publish) =====
        print("Step 7: Clicking 'Post' (final publish)...")
        time.sleep(3)
        try:
            post_btn = page.locator('div[role="dialog"] button').filter(has_text='Post').first
            time.sleep(2)
            if post_btn.is_enabled():
                post_btn.click()
                print("   ✓ Done\n")
            else:
                print("   ⚠ Post button disabled\n")
        except:
            print("   ⚠ Could not click Post\n")
        
        # ===== STEP 8: Wait for "View post" Confirmation =====
        print("\nStep 8: Waiting for publication...")
        print("   (Waiting for 'View post' link...)\n")
        
        published = False
        for i in range(45):
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
                
                # Check if on feed with our content
                if '/feed' in page.url and i > 10:
                    content_check = page.content()
                    if 'AI-powered' in content_check:
                        published = True
                        print(f"   ✓ Post visible! ({i+1}s)\n")
                        break
                        
            except:
                pass
        
        # ===== FINAL RESULT =====
        print("=" * 70)
        
        if published:
            print("   ✓✓✓ SUCCESSFUL! ✓✓✓")
            print("=" * 70)
            print("\nYour post has been PUBLISHED to LinkedIn!")
            print("\nView your post:")
            print("  https://www.linkedin.com/feed")
            print("\nOr check your Activity section:\n")
            print("  https://www.linkedin.com/in/your-profile/details/recent-activity/\n")
        else:
            print("   ⚠ NOT CONFIRMED")
            print("=" * 70)
            print("\nCheck LinkedIn manually.\n")
        
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    main()
