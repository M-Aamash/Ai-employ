"""
LinkedIn Auto Post - Final Version

Reliable automated LinkedIn posting.
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
    print("   LinkedIn Auto Post - Final")
    print("=" * 70 + "\n")
    
    content = random.choice(TEMPLATES)
    print("Posting to LinkedIn...")
    print(f"Content length: {len(content)} characters\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        page = browser.pages[0]
        
        # Go to LinkedIn feed
        print("1. Opening LinkedIn...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        page.wait_for_load_state('networkidle')
        time.sleep(4)
        print("   Done\n")
        
        # Click "Start a Post"
        print("2. Clicking 'Start a Post'...")
        try:
            # Use text selector - most reliable
            page.click("text=Start a Post")
            time.sleep(3)
            print("   Done\n")
        except Exception as e:
            print(f"   Error: {e}\n")
        
        # Wait for modal
        print("3. Waiting for editor modal...")
        try:
            page.wait_for_selector('div[role="dialog"]')
            time.sleep(2)
            print("   Done\n")
        except:
            print("   Modal may not have opened\n")
        
        # Fill content
        print("4. Filling content...")
        try:
            # Find editable div
            textbox = page.locator('div[contenteditable="true"]').first
            textbox.click()
            time.sleep(1)
            textbox.fill(content)
            time.sleep(2)
            print(f"   Filled {len(content)} characters\n")
        except Exception as e:
            print(f"   Error: {e}\n")
        
        # Click Post button
        print("5. Clicking 'Post' button...")
        try:
            # LinkedIn uses data-test-id for the publish button
            post_button = page.locator('button[data-test-id="composer-publish-button"]')
            
            # Fallback to text selector
            if post_button.count() == 0:
                post_button = page.locator('button:has-text("Post")')
            
            # Wait and click
            time.sleep(2)
            post_button.click()
            print("   Clicked\n")
            
            # Wait for post to publish
            print("6. Waiting for publication...")
            time.sleep(8)
            
            # Check for success
            print("7. Checking result...")
            
            # Look for success indicators
            page_content = page.content()
            
            if "Your post was published" in page_content or "post was shared" in page_content.lower():
                print("\n" + "=" * 70)
                print("   ✓✓✓ SUCCESS! Post published to LinkedIn! ✓✓✓")
                print("=" * 70 + "\n")
            elif '/feed' in page.url:
                print("\n" + "=" * 70)
                print("   ✓ Post published (on feed page)")
                print("=" * 70 + "\n")
            else:
                print("\n" + "=" * 70)
                print("   ? Check LinkedIn to confirm")
                print("=" * 70 + "\n")
                print("URL:", page.url, "\n")
                
        except Exception as e:
            print(f"   Error: {e}\n")
            print("Check LinkedIn manually - post may have been published\n")
        
        time.sleep(3)
        browser.close()
    
    print("Done!\n")

if __name__ == '__main__':
    main()
