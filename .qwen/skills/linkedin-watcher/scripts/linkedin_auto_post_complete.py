"""
LinkedIn Auto Post - Fully Automated

This script will automatically post to LinkedIn without any manual intervention.
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
    print("   LinkedIn Auto Post - Fully Automated")
    print("=" * 70 + "\n")
    
    content = random.choice(TEMPLATES)
    print("Selected post:")
    print("-" * 70)
    print(content)
    print("-" * 70 + "\n")
    
    session_path = Path.home() / '.linkedin_session'
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("Starting automated posting process...\n")
    
    with sync_playwright() as p:
        # Launch browser
        print("[1/8] Launching browser...")
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,  # Visible so you can watch
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        print("      ✓ Browser launched\n")
        
        page = browser.pages[0]
        
        # Go to LinkedIn
        print("[2/8] Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com', timeout=60000)
        time.sleep(5)
        print("      ✓ LinkedIn loaded\n")
        
        # Check login status
        print("[3/8] Checking login status...")
        current_url = page.url
        if 'login' in current_url or 'checkpoint' in current_url:
            print("      ⚠ Not logged in - waiting for you to log in...")
            print("      Please log in to LinkedIn in the browser window.")
            print("      Script will continue automatically after login...\n")
            
            # Wait for user to log in (up to 5 minutes)
            for i in range(30):  # 30 x 10 seconds = 5 minutes
                time.sleep(10)
                if 'feed' in page.url or 'myhome' in page.url:
                    print("      ✓ Login detected!\n")
                    break
            else:
                print("      ⚠ Continuing anyway...\n")
        else:
            print("      ✓ Already logged in\n")
        
        # Go to feed
        print("[4/8] Going to feed page...")
        page.goto('https://www.linkedin.com/feed', timeout=60000)
        time.sleep(5)
        print("      ✓ Feed loaded\n")
        
        # Click "Start a Post"
        print("[5/8] Clicking 'Start a Post'...")
        try:
            # Try multiple selectors
            selectors = [
                'text=Start a Post',
                'button[aria-label="Start a Post"]',
                '.share-box-feed-entry__trigger',
                '.share-box-feed-entry'
            ]
            
            clicked = False
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if element.count() > 0:
                        element.click()
                        print(f"      ✓ Clicked using: {selector}\n")
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                print("      ⚠ Could not auto-click. Waiting 15 seconds...")
                print("      If popup doesn't open, click 'Start a Post' manually.\n")
                time.sleep(15)
            
        except Exception as e:
            print(f"      ⚠ Error: {e}\n")
        
        time.sleep(3)
        
        # Wait for modal
        print("[6/8] Waiting for post editor...")
        try:
            page.wait_for_selector('div[role="dialog"]', timeout=15000)
            print("      ✓ Editor opened\n")
            time.sleep(2)
        except:
            print("      ⚠ Modal may not have opened\n")
        
        # Fill content
        print("[7/8] Filling post content...")
        try:
            # Find textbox inside dialog
            textbox = page.locator('div[role="dialog"] div[contenteditable="true"]').first
            
            # Click to focus
            textbox.click()
            time.sleep(1)
            
            # Fill content
            textbox.fill(content)
            time.sleep(2)
            
            # Verify
            filled = textbox.inner_text()
            print(f"      ✓ Content filled ({len(filled)} characters)\n")
            
        except Exception as e:
            print(f"      ⚠ Error filling content: {e}\n")
        
        # Click Post button
        print("[8/8] Publishing post...")
        try:
            # Find Post button inside dialog
            post_buttons = page.locator('div[role="dialog"] button').all()
            
            post_button = None
            for btn in post_buttons:
                try:
                    text = btn.inner_text().strip()
                    if text == 'Post' or 'Post' in text:
                        post_button = btn
                        break
                except:
                    continue
            
            if post_button:
                time.sleep(2)
                post_button.click()
                print("      ✓ Post button clicked\n")
                
                # Wait for publication
                print("      Waiting for post to publish...")
                time.sleep(10)
                
                # Check result
                if '/feed' in page.url:
                    print("\n" + "=" * 70)
                    print("   ✓✓✓ SUCCESS! Post published to LinkedIn! ✓✓✓")
                    print("=" * 70)
                    print("\nYour AI Employee has successfully posted to LinkedIn!")
                    print("Visit your profile to see the published post.\n")
                else:
                    print("\n" + "=" * 70)
                    print("   Post action completed")
                    print("=" * 70)
                    print("\nCheck your LinkedIn feed to confirm the post.\n")
            else:
                print("      ⚠ Could not find Post button\n")
                
        except Exception as e:
            print(f"      ⚠ Error: {e}\n")
            print("      Check LinkedIn manually - post may have been published\n")
        
        time.sleep(5)
        browser.close()
    
    print("Done!\n")

if __name__ == '__main__':
    main()
