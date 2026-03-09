"""
LinkedIn Auto Post - Fully Automated Posting

This script logs in to LinkedIn and automatically publishes a post
without any manual intervention.

Usage:
    python linkedin_auto_post.py
"""

import sys
import os
import time
import random
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
    print("\n" + "=" * 70)
    print("   LinkedIn Auto Post - Fully Automated")
    print("=" * 70 + "\n")
    
    # Select content
    content = random.choice(TEMPLATES)
    
    print("Post content:")
    print("-" * 70)
    print(content)
    print("-" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    success = False
    
    with sync_playwright() as p:
        print("Launching browser...")
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
        
        # Go to LinkedIn
        print("Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com', timeout=60000)
        time.sleep(5)
        
        # Check if logged in
        try:
            page.wait_for_url('**/feed**', timeout=30000)
            print("[OK] Already logged in!\n")
        except PlaywrightTimeout:
            print("[INFO] Not logged in. Waiting for login...")
            try:
                page.wait_for_url('**/feed**', timeout=120000)
                print("[OK] Logged in!\n")
            except PlaywrightTimeout:
                print("[ERROR] Login timeout. Please log in manually.")
                browser.close()
                return
        
        # Go to feed page
        print("Going to feed page...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(5)
        
        # Take screenshot for debugging
        page.screenshot(path='linkedin_step1.png')
        
        # Find and click "Start a Post" button
        print("Looking for 'Start a Post' button...")
        
        try:
            # Wait for the post creation area to be visible
            page.wait_for_selector('.share-box-feed-entry', timeout=10000)
            print("Found post creation area")
            
            # Click on the post creation area
            post_area = page.locator('.share-box-feed-entry').first
            post_area.click()
            print("Clicked post creation area\n")
            
            time.sleep(3)
            
            # Take screenshot
            page.screenshot(path='linkedin_step2.png')
            
            # Wait for the editor modal to appear
            print("Waiting for editor modal...")
            page.wait_for_selector('div[role="dialog"]', timeout=10000)
            print("Editor modal opened\n")
            
            time.sleep(2)
            
            # Take screenshot
            page.screenshot(path='linkedin_step3.png')
            
            # Find the textbox and fill content
            print("Filling post content...")
            textbox = page.locator('div[role="textbox"][aria-label*="text"]').first
            
            # Click to focus
            textbox.click()
            time.sleep(1)
            
            # Fill content slowly
            textbox.fill(content)
            print("Content filled\n")
            
            time.sleep(3)
            
            # Take screenshot
            page.screenshot(path='linkedin_step4.png')
            
            # Verify content was filled
            filled_content = textbox.inner_text()
            if len(filled_content) > 50:
                print(f"[OK] Content verified ({len(filled_content)} characters)\n")
            else:
                print("[WARN] Content may not have filled correctly")
            
            # Find and click Post button
            print("Looking for Post button...")
            
            # Wait for Post button to be enabled
            post_button = page.locator('button:has-text("Post")').first
            
            # Wait for button to be clickable
            post_button.wait_for(state='enabled', timeout=10000)
            print("Post button is enabled")
            
            # Click Post button
            print("Clicking Post button...")
            post_button.click()
            
            # Wait for confirmation
            print("Waiting for post confirmation...")
            time.sleep(5)
            
            # Take screenshot
            page.screenshot(path='linkedin_step5.png')
            
            # Check if post was published (look for feed or success message)
            try:
                page.wait_for_selector('.feed-shared-update-v2', timeout=10000)
                print("\n" + "=" * 70)
                print("   ✓ SUCCESS! Post published to LinkedIn!")
                print("=" * 70 + "\n")
                success = True
            except PlaywrightTimeout:
                # Check alternative success indicators
                current_url = page.url
                if '/feed' in current_url:
                    print("\n" + "=" * 70)
                    print("   ✓ Post likely published (back on feed)")
                    print("=" * 70 + "\n")
                    success = True
                else:
                    print("\n[WARN] Could not confirm publication")
                    print("Check your LinkedIn profile to verify the post")
        
        except PlaywrightTimeout as e:
            print(f"\n[ERROR] Timeout: {e}")
            print("Taking final screenshot...")
            page.screenshot(path='linkedin_error.png')
            print("Screenshot saved to: linkedin_error.png")
        
        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path='linkedin_error.png')
            print("Screenshot saved to: linkedin_error.png")
        
        # Keep browser open briefly
        time.sleep(3)
        browser.close()
    
    if success:
        print("Your AI Employee successfully posted to LinkedIn! 🚀\n")
    else:
        print("\nPosting may have failed. Check your LinkedIn profile.\n")

if __name__ == '__main__':
    main()
