"""
LinkedIn Post - Login and Post in same session

This script logs in to LinkedIn and immediately posts content
in the same browser session to avoid session persistence issues.

Usage:
    python linkedin_post.py [--content "Your post content"]
"""

import sys
import os
from pathlib import Path

# Set console encoding to UTF-8 for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Playwright not installed. Run: pip install playwright")
    sys.exit(1)

# Business post templates
TEMPLATES = [
    """🚀 Exciting news! We're helping businesses automate their operations with AI-powered solutions.

Our AI employees work 24/7 to:
✅ Handle customer inquiries
✅ Process invoices automatically  
✅ Manage communications
✅ Generate business insights

Ready to transform your business? Let's talk!

#AI #Automation #Business #Innovation #DigitalTransformation""",

    """💡 Did you know? Businesses save 85% on operational costs by implementing AI automation.

Our clients see results in:
📈 Increased productivity
⏰ Time savings (40+ hours/week)
💰 Reduced operational costs
🎯 Better customer satisfaction

Want to learn how AI can help your business? DM me!

#BusinessGrowth #AI #Productivity #Entrepreneurship""",

    """📊 Case Study: 30-Day Results

Client: Professional Services Firm
Challenge: Overwhelmed team, slow response times

Solution: AI Employee Implementation

Results:
• Response time: 24hrs → 5 minutes
• Lead conversion: +45%
• Team productivity: +60%
• Customer satisfaction: 95%

Want similar results? Let's talk!

#CaseStudy #BusinessSuccess #AI #Automation #ROI""",
]

def main():
    import argparse
    import random
    import time
    
    parser = argparse.ArgumentParser(description='Post to LinkedIn')
    parser.add_argument('--content', help='Custom content to post')
    parser.add_argument('--template', type=int, choices=[1,2,3], help='Select template (1-3)')
    args = parser.parse_args()
    
    # Get content
    if args.content:
        content = args.content
    elif args.template:
        content = TEMPLATES[args.template - 1]
    else:
        content = random.choice(TEMPLATES)
    
    print("\n" + "=" * 60)
    print("   LinkedIn Post")
    print("=" * 60 + "\n")
    print("Content to post:\n")
    print(content)
    print("\n" + "=" * 60 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("Opening LinkedIn...")
    
    with sync_playwright() as p:
        # Launch browser with persistent context
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,  # Visible for login
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        
        page = browser.pages[0]
        
        # Navigate to LinkedIn
        page.goto('https://www.linkedin.com', timeout=60000)
        
        # Wait for login (up to 2 minutes)
        print("Waiting for login... (up to 2 minutes)")
        try:
            page.wait_for_url('**/feed**', timeout=120000)
            print("[OK] Logged in!\n")
        except PlaywrightTimeout:
            print("[WARN] Login timeout. You may need to log in manually in the browser.")
            time.sleep(10)  # Give extra time
        
        # Navigate to post creation
        print("Creating post...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(3)  # Wait for page to load
        
        try:
            # Click "Start a Post" - try multiple selectors
            print("Clicking 'Start a Post'...")
            clicked = False
            
            # Try selector 1: aria-label
            try:
                start_post = page.locator('button[aria-label="Start a Post"]').first
                if start_post.count() > 0:
                    start_post.click(timeout=5000)
                    clicked = True
                    print("Clicked using aria-label selector")
            except:
                pass
            
            # Try selector 2: div with specific role
            if not clicked:
                try:
                    start_post = page.locator('div[id="feed-shared-start-a-post"]').first
                    if start_post.count() > 0:
                        start_post.click(timeout=5000)
                        clicked = True
                        print("Clicked using id selector")
                except:
                    pass
            
            # Try selector 3: button with text
            if not clicked:
                try:
                    start_post = page.locator('button:has-text("Start a Post")').first
                    if start_post.count() > 0:
                        start_post.click(timeout=5000)
                        clicked = True
                        print("Clicked using text selector")
                except:
                    pass
            
            # Try selector 4: generic start post button
            if not clicked:
                try:
                    start_post = page.locator('.share-box-feed-entry').first
                    if start_post.count() > 0:
                        start_post.click(timeout=5000)
                        clicked = True
                        print("Clicked using class selector")
                except:
                    pass
            
            if not clicked:
                print("[WARN] Could not auto-click 'Start a Post' button")
                print("Please click 'Start a Post' manually in the browser window")
                print("Waiting 30 seconds for manual action...")
                time.sleep(30)
            
            # Wait for editor
            print("Waiting for editor...")
            page.wait_for_selector('div[role="textbox"]', timeout=15000)
            print("Editor opened...")
            
            # Fill content
            textbox = page.locator('div[role="textbox"]').first
            textbox.fill(content)
            print("Content filled...")
            
            # Wait a moment for text to register
            time.sleep(2)
            
            # Click Post button
            print("Posting...")
            post_button = page.locator('button:has-text("Post")').first
            post_button.click(timeout=5000)
            
            # Wait for confirmation
            try:
                page.wait_for_selector('.feed-shared-update-v2', timeout=15000)
                print("\n" + "=" * 60)
                print("   SUCCESS! Post published to LinkedIn!")
                print("=" * 60 + "\n")
            except PlaywrightTimeout:
                print("\n[WARN] Could not confirm post, but it may have been published.")
                print("Check your LinkedIn feed to verify.\n")
            
        except Exception as e:
            print(f"\n[ERROR] Failed to post: {e}\n")
            print("You can post manually by:")
            print("1. Go to https://www.linkedin.com/feed")
            print("2. Click 'Start a Post'")
            print("3. Copy/paste the content shown above")
            print("4. Click 'Post'\n")
        
        # Keep browser open for a moment
        print("Closing browser in 5 seconds...")
        time.sleep(5)
        browser.close()
    
    print("\nDone!\n")

if __name__ == '__main__':
    main()
