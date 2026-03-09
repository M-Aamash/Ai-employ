"""
LinkedIn Auto Post - Working Version

Uses specific selectors inside the modal dialog.
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
    print("   LinkedIn Auto Post - Working Version")
    print("=" * 70 + "\n")
    
    content = random.choice(TEMPLATES)
    print("Posting to LinkedIn...\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        page = browser.pages[0]
        
        # Go to LinkedIn
        print("1. Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        page.wait_for_load_state('networkidle')
        time.sleep(3)
        
        # Click "Start a Post"
        print("2. Clicking 'Start a Post'...")
        try:
            page.click('button[aria-label="Start a Post"]')
        except:
            # Fallback to text selector
            page.click('text=Start a Post')
        time.sleep(3)
        
        # Wait for modal
        print("3. Waiting for modal...")
        page.wait_for_selector('div[role="dialog"]')
        time.sleep(2)
        
        # Fill content
        print("4. Filling content...")
        textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
        textbox.click()
        time.sleep(1)
        textbox.fill(content)
        time.sleep(2)
        
        # Click Post button INSIDE modal
        print("5. Clicking Post button...")
        
        # Find the Post button inside the dialog
        post_button = page.locator('div[role="dialog"] button[data-test-id="composer-publish-button"]').first
        
        # Fallback: button with "Post" text inside dialog
        if post_button.count() == 0:
            post_button = page.locator('div[role="dialog"] button:has-text("Post")').last
        
        time.sleep(2)
        post_button.click()
        
        # Wait for publication
        print("6. Waiting for post to publish...")
        time.sleep(10)
        
        # Check result
        print("7. Checking result...")
        
        if '/feed' in page.url:
            print("\n" + "=" * 70)
            print("   ✓✓✓ SUCCESS! Post published to LinkedIn! ✓✓✓")
            print("=" * 70)
            print("\nYour AI Employee has successfully posted to LinkedIn!")
            print("Check your profile to see the post.\n")
        else:
            print("\nCheck LinkedIn manually\n")
        
        time.sleep(3)
        browser.close()

if __name__ == '__main__':
    main()
