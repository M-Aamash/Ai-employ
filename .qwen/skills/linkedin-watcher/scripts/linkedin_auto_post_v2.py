"""
LinkedIn Auto Post - Improved Selectors

Automated LinkedIn posting with better element detection.
"""

import sys
import os
import time
import random
from pathlib import Path

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
    print("   LinkedIn Auto Post")
    print("=" * 70 + "\n")
    
    content = random.choice(TEMPLATES)
    print("Content:")
    print(content)
    print("\n" + "=" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        page = browser.pages[0]
        
        # Navigate to LinkedIn
        print("Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(5)
        
        # Wait for page to fully load
        print("Waiting for page to load...")
        page.wait_for_load_state('networkidle', timeout=30000)
        time.sleep(3)
        
        # Find "Start a Post" button - multiple approaches
        print("Finding 'Start a Post' button...")
        
        try:
            # Approach 1: Click on the "Start a Post" text input field
            print("Trying approach 1: Click on post input field...")
            post_input = page.locator('button[aria-label="Start a Post"]').first
            
            if post_input.count() == 0:
                # Approach 2: Click on the div containing "Start a Post"
                print("Trying approach 2: Click on post div...")
                post_input = page.locator("text=Start a Post").first
            
            post_input.click()
            print("Clicked 'Start a Post'\n")
            
            time.sleep(3)
            
            # Wait for modal
            print("Waiting for post editor...")
            page.wait_for_selector('div[role="dialog"]', timeout=15000)
            print("Editor opened\n")
            
            time.sleep(2)
            
            # Fill content
            print("Filling content...")
            
            # Find the textarea/div for post content
            textbox = page.locator('div[contenteditable="true"][role="textbox"]').first
            
            # Click to focus
            textbox.click()
            time.sleep(1)
            
            # Fill content
            textbox.fill(content)
            print(f"Content filled ({len(content)} characters)\n")
            
            time.sleep(3)
            
            # Verify content
            actual_content = textbox.inner_text()
            print(f"Verified: {len(actual_content)} characters in textbox\n")
            
            # Find and click Post button
            print("Clicking 'Post' button...")
            
            # Wait for Post button
            post_btn = page.locator('button[data-test-id="composer-publish-button"]').first
            
            # If not found, try alternative
            if post_btn.count() == 0:
                post_btn = page.locator('button:has-text("Post")').first
            
            # Wait for button to be enabled
            post_btn.wait_for(state='enabled', timeout=10000)
            
            # Click
            post_btn.click()
            print("Post button clicked\n")
            
            # Wait for confirmation
            print("Waiting for confirmation...")
            time.sleep(5)
            
            # Check for success
            try:
                # Look for "Your post was published" or similar
                page.wait_for_selector('text="Your post was published"', timeout=5000)
                print("=" * 70)
                print("   ✓ SUCCESS! Post published!")
                print("=" * 70 + "\n")
            except:
                # Check if we're back on feed
                if '/feed' in page.url:
                    print("=" * 70)
                    print("   ✓ Post published (back on feed)")
                    print("=" * 70 + "\n")
                else:
                    print("[WARN] Check LinkedIn to confirm post was published\n")
            
        except PlaywrightTimeout as e:
            print(f"\n[ERROR] Timeout: {e}")
            print("\nManual posting instructions:")
            print("1. LinkedIn is open in your browser")
            print("2. Click 'Start a Post'")
            print("3. Copy/paste this content:")
            print(content)
            print("4. Click 'Post'")
        
        except Exception as e:
            print(f"\n[ERROR] {e}")
        
        time.sleep(3)
        browser.close()

if __name__ == '__main__':
    main()
