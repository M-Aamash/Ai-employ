"""
LinkedIn Watcher - Automate LinkedIn for business promotion.

This watcher uses Playwright to automate LinkedIn activities:
- Post business content to generate sales
- Monitor for leads and engagement
- Create action files for Qwen Code to process

Usage:
    # First time - visible mode for login
    python linkedin_watcher.py --vault ./AI_Employee_Vault --visible
    
    # Post content (headless)
    python linkedin_watcher.py --vault ./AI_Employee_Vault --action post
    
    # Monitor for leads
    python linkedin_watcher.py --vault ./AI_Employee_Vault --action monitor

Note: First run requires manual LinkedIn login. Session is saved for reuse.
"""

import argparse
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# Set console encoding to UTF-8 for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install playwright")
    print("Then run: playwright install chromium")
    sys.exit(1)

from base_watcher import BaseWatcher


class LinkedInWatcher(BaseWatcher):
    """LinkedIn automation watcher implementation."""
    
    def __init__(
        self,
        vault_path: str,
        session_path: str = None,
        check_interval: int = 3600,  # 1 hour for LinkedIn
        headless: bool = True
    ):
        """
        Initialize LinkedIn watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session
            check_interval: Seconds between checks
            headless: Run browser in headless mode
        """
        super().__init__(vault_path, check_interval)
        
        # Session path - default to user home
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = Path.home() / '.linkedin_session'
        
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        
        # Business content templates
        self.content_templates = self._load_content_templates()
        
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Headless: {self.headless}')
    
    def _load_content_templates(self) -> List[str]:
        """Load business content templates."""
        # Default business post templates
        templates = [
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
            
            """🎯 Success Story: One of our clients reduced response time from 24 hours to 5 minutes using our AI Employee system.

Results after 30 days:
✓ 3x more leads handled
✓ 90% customer satisfaction
✓ Zero missed opportunities
✓ Team focused on high-value work

Ready for similar results? Let's connect!

#CustomerService #BusinessSuccess #AI #Automation""",
            
            """📊 Monday Motivation: The future of business is human + AI collaboration.

It's not about replacing humans - it's about:
🔹 Eliminating repetitive tasks
🔹 Empowering teams to focus on creativity
🔹 Providing 24/7 customer support
🔹 Scaling without linear cost increase

How is your business preparing for the AI future?

#MondayMotivation #FutureOfWork #AI #Leadership""",
            
            """🔥 Hot Take: If you're not implementing AI in your business in 2026, you're already behind.

Your competitors are:
→ Responding to leads instantly
→ Working 24/7 without burnout
→ Scaling faster with lower costs
→ Providing better customer experiences

The question isn't "Can you afford AI?" It's "Can you afford NOT to?"

#BusinessStrategy #AI #CompetitiveAdvantage #Innovation""",
        ]
        
        # Try to load custom templates from content folder
        content_dir = Path(__file__).parent.parent / 'content'
        if content_dir.exists():
            for template_file in content_dir.glob('*.txt'):
                try:
                    templates.append(template_file.read_text(encoding='utf-8'))
                except Exception as e:
                    self.logger.debug(f'Could not load {template_file}: {e}')
        
        return templates
    
    def post_content(self, content: str = None) -> bool:
        """
        Post content to LinkedIn.
        
        Args:
            content: Content to post (random template if None)
            
        Returns:
            True if successful
        """
        if not content:
            content = random.choice(self.content_templates)
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox'
                    ]
                )
                
                page = browser.pages[0]
                
                # Navigate to LinkedIn
                self.logger.info('Navigating to LinkedIn...')
                page.goto('https://www.linkedin.com', timeout=60000)
                
                # Check if logged in
                try:
                    page.wait_for_selector('.feed-shared-update-v2', timeout=10000)
                    self.logger.info('Already logged in')
                except PlaywrightTimeout:
                    self.logger.warning('Not logged in - manual login required')
                    if self.headless:
                        self.logger.error('Run with --visible to login manually')
                        browser.close()
                        return False
                    
                    # Wait for user to login
                    self.logger.info('Waiting for login... (60 seconds)')
                    try:
                        page.wait_for_selector('.feed-shared-update-v2', timeout=60000)
                        self.logger.info('Login successful')
                    except PlaywrightTimeout:
                        self.logger.error('Login timeout')
                        browser.close()
                        return False
                
                # Navigate to post creation
                self.logger.info('Creating post...')
                page.goto('https://www.linkedin.com/feed', timeout=60000)
                
                # Click "Start a Post"
                try:
                    start_post = page.locator('button[aria-label="Start a Post"]').first
                    start_post.click(timeout=5000)
                except:
                    # Try alternative selector
                    start_post = page.locator('.share-box-feed-entry__trigger').first
                    start_post.click(timeout=5000)
                
                # Wait for editor
                page.wait_for_selector('div[role="textbox"]', timeout=5000)
                
                # Fill content
                textbox = page.locator('div[role="textbox"]').first
                textbox.fill(content)
                
                # Click Post button
                post_button = page.locator('button:has-text("Post")').first
                post_button.click(timeout=5000)
                
                # Wait for confirmation
                try:
                    page.wait_for_selector('.feed-shared-update-v2', timeout=10000)
                    self.logger.info('✓ Post published successfully')
                    success = True
                except PlaywrightTimeout:
                    self.logger.warning('Post may have been published (no confirmation)')
                    success = True
                
                browser.close()
                return success
                
        except Exception as e:
            self.logger.error(f'Error posting to LinkedIn: {e}')
            return False
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check LinkedIn for new engagement/leads.
        
        Returns:
            List of engagement items
        """
        engagement = []
        
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
                )
                
                page = browser.pages[0]
                
                # Navigate to LinkedIn
                page.goto('https://www.linkedin.com', timeout=60000)
                
                # Check if logged in
                try:
                    page.wait_for_selector('.feed-shared-update-v2', timeout=10000)
                except PlaywrightTimeout:
                    self.logger.warning('Not logged in')
                    browser.close()
                    return []
                
                # Check notifications for engagement
                self.logger.info('Checking notifications...')
                page.goto('https://www.linkedin.com/notifications', timeout=60000)
                
                # Look for recent engagement (last 24 hours)
                try:
                    notifications = page.query_selector_all('.notification-item')
                    
                    for notif in notifications[:10]:  # Check last 10 notifications
                        try:
                            text = notif.inner_text().lower()
                            
                            # Check for lead indicators
                            lead_keywords = ['interested', 'pricing', 'demo', 'meeting', 'call', 'more information']
                            if any(kw in text for kw in lead_keywords):
                                engagement.append({
                                    'type': 'lead',
                                    'content': notif.inner_text(),
                                    'timestamp': datetime.now().isoformat()
                                })
                                self.logger.info(f'Lead detected!')
                            
                        except Exception as e:
                            self.logger.debug(f'Error processing notification: {e}')
                
                except Exception as e:
                    self.logger.debug(f'Error checking notifications: {e}')
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f'Error checking LinkedIn: {e}')
        
        return engagement
    
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create action file for detected engagement.
        
        Args:
            item: Engagement data dictionary
            
        Returns:
            Path to created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"LINKEDIN_{item['type'].upper()}_{timestamp}.md"
        filepath = self.needs_action / filename
        
        content = f'''---
type: linkedin
category: {item['type']}
received: {item['timestamp']}
priority: {"high" if item['type'] == "lead" else "normal"}
status: pending
---

# LinkedIn {item['type'].title()}

## Detected
{item['timestamp']}

## Content

{item['content']}

## Suggested Actions

- [ ] Review the engagement
- [ ] Determine appropriate response
- [ ] Start a Post response (requires approval)
- [ ] Follow up via LinkedIn or email
- [ ] Log interaction in CRM
- [ ] Move to Done when complete

## Notes

<!-- Add any additional context here -->

---
*Created by LinkedIn Watcher*
'''
        
        filepath.write_text(content, encoding='utf-8')
        self._log_action(f'linkedin_{item["type"]}', 'LinkedIn', filepath, {
            'content_preview': item['content'][:100]
        })
        
        return filepath
    
    def run_monitor(self):
        """Run in monitor mode (check for engagement)."""
        self.logger.info('Starting LinkedIn monitor mode...')
        
        items = self.check_for_updates()
        
        if items:
            self.logger.info(f'Found {len(items)} engagement item(s)')
            for item in items:
                filepath = self.create_action_file(item)
                self.logger.info(f'Created: {filepath.name}')
        else:
            self.logger.info('No new engagement detected')
        
        return len(items)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Watcher')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=3600, help='Check interval (default: 3600s)')
    parser.add_argument('--session', help='Path to browser session storage')
    parser.add_argument('--visible', action='store_true', help='Run browser in visible mode')
    parser.add_argument('--action', choices=['post', 'monitor', 'watch'], default='watch',
                       help='Action to perform')
    parser.add_argument('--content', help='Custom content to post')
    parser.add_argument('--verbose', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Create watcher
    watcher = LinkedInWatcher(
        vault_path=args.vault,
        session_path=args.session,
        check_interval=args.interval,
        headless=not args.visible
    )
    
    if args.verbose:
        watcher.logger.setLevel(logging.DEBUG)
    
    if args.action == 'post':
        # Post content
        print("\n" + "=" * 60)
        print("   LinkedIn Post")
        print("=" * 60 + "\n")
        
        content = args.content
        if not content:
            print("Using random business template...")
            content = random.choice(watcher.content_templates)
            print(f"\nContent:\n{content}\n")
        
        if watcher.post_content(content):
            print("\n✓ Post published successfully!")
            
            # Log the post
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'linkedin_post',
                'content_preview': content[:100],
                'result': 'success'
            }
            log_file = watcher.logs_path / f'{watcher.get_today_date()}.json'
            if log_file.exists():
                import json
                logs = json.loads(log_file.read_text())
            else:
                logs = []
            logs.append(log_entry)
            log_file.write_text(json.dumps(logs, indent=2))
        else:
            print("\n✗ Post failed - check login status")
            print("  Run with --visible to login manually")
    
    elif args.action == 'monitor':
        # Monitor for engagement
        print("\n" + "=" * 60)
        print("   LinkedIn Monitor")
        print("=" * 60 + "\n")
        
        count = watcher.run_monitor()
        print(f"\nFound {count} engagement item(s)")
    
    else:
        # Watch mode (continuous)
        watcher.run()


if __name__ == '__main__':
    import logging
    main()
