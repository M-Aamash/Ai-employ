"""
LinkedIn Post - Simple and Working

Opens LinkedIn, you click Start a Post, then script fills and posts automatically.
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
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Install: pip install playwright")
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
    print("   LinkedIn Auto Post - Simple")
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
        
        # Go to LinkedIn
        print("Opening LinkedIn...")
        page.goto('https://www.linkedin.com', timeout=60000)
        time.sleep(8)  # Wait for page load
        
        print("\n" + "=" * 70)
        print("INSTRUCTIONS:")
        print("=" * 70)
        print("1. If not logged in, log in to LinkedIn now")
        print("2. Click 'Start a Post' at top of feed")
        print("3. Script will auto-fill and post in 10 seconds...")
        print("=" * 70 + "\n")
        
        # Wait for user to click "Start a Post"
        time.sleep(10)
        
        # Check if modal is open
        print("Looking for post editor...")
        
        try:
            # Find textbox inside modal
            textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
            textbox.click()
            time.sleep(1)
            
            # Fill content
            print("Filling content...")
            textbox.fill(content)
            time.sleep(2)
            
            # Find Post button inside modal
            print("Finding Post button...")
            post_button = page.locator('div[role="dialog"] button[data-test-id="composer-publish-button"]').first
            
            # Fallback
            if post_button.count() == 0:
                # Get all buttons in dialog and find the right one
                dialog_buttons = page.locator('div[role="dialog"] button').all()
                for btn in dialog_buttons:
                    if 'Post' in btn.inner_text():
                        post_button = btn
                        break
            
            time.sleep(2)
            print("Clicking Post...")
            post_button.click()
            
            # Wait for post to publish
            print("Waiting for publication...")
            time.sleep(8)
            
            print("\n" + "=" * 70)
            print("   ✓ Post should be published!")
            print("=" * 70 + "\n")
            
        except Exception as e:
            print(f"\nError: {e}")
            print("\nManual posting:")
            print("1. Click 'Start a Post'")
            print("2. Paste this content:")
            print(content)
            print("3. Click 'Post'")
        
        time.sleep(3)
        browser.close()

if __name__ == '__main__':
    main()
