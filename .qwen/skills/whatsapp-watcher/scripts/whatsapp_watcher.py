"""
WhatsApp Watcher - Monitor WhatsApp Web for urgent messages.

This watcher uses Playwright to automate WhatsApp Web and monitor for messages
containing specific keywords. When detected, it creates action files in the
Obsidian vault for Claude Code to process.

Usage:
    python whatsapp_watcher.py --vault /path/to/vault --interval 30

Note: First run requires manual QR code scan to authenticate.
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from base_watcher import BaseWatcher


class WhatsAppWatcher(BaseWatcher):
    """WhatsApp Web watcher implementation."""
    
    def __init__(
        self,
        vault_path: str,
        session_path: str = None,
        keywords: List[str] = None,
        check_interval: int = 30,
        headless: bool = True
    ):
        """
        Initialize WhatsApp watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session
            keywords: List of keywords to watch for
            check_interval: Seconds between checks
            headless: Run browser in headless mode
        """
        super().__init__(vault_path, check_interval)
        
        # Session path - default to user home
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = Path.home() / '.whatsapp_session'
        
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Keywords to watch for
        self.keywords = keywords or ['urgent', 'asap', 'invoice', 'payment', 'help']
        self.headless = headless
        
        self.logger.info(f'Watching keywords: {self.keywords}')
        self.logger.info(f'Session path: {self.session_path}')
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check WhatsApp Web for new messages with keywords.
        
        Returns:
            List of message dictionaries
        """
        messages = []
        
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
                
                # Navigate to WhatsApp Web
                self.logger.debug('Navigating to WhatsApp Web')
                page.goto('https://web.whatsapp.com', timeout=60000)
                
                # Wait for chat list to load
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                except PlaywrightTimeout:
                    self.logger.warning('Chat list not loaded - possibly showing QR code')
                    browser.close()
                    return []  # Return empty - user needs to scan QR
                
                # Find all chat items with unread messages
                self.logger.debug('Looking for unread messages')
                unread_chats = page.query_selector_all('[aria-label*="unread"]')
                
                for chat in unread_chats:
                    try:
                        # Extract chat info
                        chat_text = chat.inner_text()
                        lines = chat_text.split('\n')
                        
                        # First line is usually contact name
                        contact_name = lines[0] if lines else 'Unknown'
                        
                        # Rest is message preview
                        message_text = '\n'.join(lines[1:]) if len(lines) > 1 else ''
                        
                        # Check for keywords
                        message_lower = message_text.lower()
                        matched_keywords = [
                            kw for kw in self.keywords 
                            if kw.lower() in message_lower
                        ]
                        
                        if matched_keywords:
                            # Generate unique ID from message content
                            msg_id = f"{contact_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            
                            messages.append({
                                'id': msg_id,
                                'contact': contact_name,
                                'message': message_text,
                                'keywords': matched_keywords,
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            self.logger.info(
                                f"Match found: {contact_name} - {matched_keywords}"
                            )
                    
                    except Exception as e:
                        self.logger.debug(f'Error processing chat: {e}')
                        continue
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f'Error checking WhatsApp: {e}')
        
        return messages
    
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create action file for detected message.
        
        Args:
            item: Message data dictionary
            
        Returns:
            Path to created action file
        """
        # Create markdown content
        content = f'''---
type: whatsapp
from: {item['contact']}
received: {item['timestamp']}
priority: high
status: pending
keywords: [{', '.join(item['keywords'])}]
message_id: {item['id']}
---

# WhatsApp Message

## From
{item['contact']}

## Received
{item['timestamp']}

## Message Content
{item['message']}

## Matched Keywords
{', '.join(item['keywords'])}

## Suggested Actions

- [ ] Read and understand the message
- [ ] Determine appropriate response
- [ ] Draft reply (requires approval)
- [ ] Send response via WhatsApp
- [ ] Move to Done when complete

## Notes

<!-- Add any additional context or notes here -->

---
*Created by WhatsApp Watcher*
'''
        
        # Create filename
        safe_contact = self.sanitize_filename(item['contact'].lower().replace(' ', '_'))
        filename = f"WHATSAPP_{safe_contact}_{item['id'].split('_')[-1]}.md"
        filepath = self.needs_action / filename
        
        # Write file
        filepath.write_text(content, encoding='utf-8')
        
        # Log the action
        self._log_action('whatsapp_message', item['contact'], filepath)
        
        return filepath
    
    def _log_action(self, action_type: str, target: str, filepath: Path):
        """Log action to JSON log file."""
        log_entry = {
            'timestamp': self.get_timestamp(),
            'action_type': action_type,
            'actor': 'whatsapp_watcher',
            'target': target,
            'filepath': str(filepath),
            'result': 'created'
        }
        
        log_file = self.logs_path / f'{self.get_today_date()}.json'
        
        # Append to log file
        if log_file.exists():
            logs = json.loads(log_file.read_text())
        else:
            logs = []
        
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='WhatsApp Watcher')
    parser.add_argument(
        '--vault',
        required=True,
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Check interval in seconds (default: 30)'
    )
    parser.add_argument(
        '--session',
        help='Path to browser session storage'
    )
    parser.add_argument(
        '--keywords',
        help='Comma-separated keywords to watch'
    )
    parser.add_argument(
        '--visible',
        action='store_true',
        help='Run browser in visible mode (for QR scan)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Parse keywords
    keywords = None
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(',')]
    
    # Create watcher
    watcher = WhatsAppWatcher(
        vault_path=args.vault,
        session_path=args.session,
        keywords=keywords,
        check_interval=args.interval,
        headless=not args.visible
    )
    
    if args.verbose:
        watcher.logger.setLevel(logging.DEBUG)
    
    # Run watcher
    watcher.run()


if __name__ == '__main__':
    import logging
    main()
