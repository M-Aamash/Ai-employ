"""
Gmail Watcher - Monitor Gmail for important messages.

This watcher uses the Gmail API to monitor for new and important emails.
When detected, it creates action files in the Obsidian vault for Qwen Code
to process.

Usage:
    python gmail_watcher.py --vault /path/to/vault --interval 120

First Run (Authorize):
    python gmail_watcher.py --vault /path/to/vault --authorize

This will open a browser for Gmail API authorization.
Credentials file (credentials.json) should be in project root.
"""

import argparse
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
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
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    from base64 import urlsafe_b64decode
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

from base_watcher import BaseWatcher


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    """Gmail API watcher implementation."""
    
    def __init__(
        self,
        vault_path: str,
        credentials_path: str = None,
        token_path: str = None,
        label: str = 'INBOX',
        query: str = 'is:unread is:important',
        check_interval: int = 120
    ):
        """
        Initialize Gmail watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to credentials.json
            token_path: Path to token.json
            label: Gmail label to monitor
            query: Gmail search query
            check_interval: Seconds between checks
        """
        super().__init__(vault_path, check_interval)

        # Paths - look for credentials.json in project root by default
        # Script is at: .qwen/skills/gmail-watcher/scripts/gmail_watcher.py
        # Project root is 4 levels up
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        self.credentials_path = Path(credentials_path) if credentials_path else project_root / 'credentials.json'
        self.token_path = Path(token_path) if token_path else project_root / 'gmail_token.json'
        
        # If credentials not found in project root, try current working directory
        if not self.credentials_path.exists():
            cwd_creds = Path.cwd() / 'credentials.json'
            if cwd_creds.exists():
                self.credentials_path = cwd_creds
                self.logger.info(f'Found credentials in cwd: {self.credentials_path}')
        
        # Gmail settings
        self.label = label
        self.query = query
        
        # Gmail service
        self.service = None
        self.creds = None
        
        self.logger.info(f'Gmail query: {self.query}')
        self.logger.info(f'Credentials: {self.credentials_path}')
        self.logger.info(f'Token: {self.token_path}')
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API.
        
        Returns:
            True if authentication successful
        """
        self.creds = None
        
        # Load existing token
        if self.token_path.exists():
            try:
                self.creds = Credentials.from_authorized_user_file(
                    self.token_path, SCOPES
                )
                self.logger.info('Loaded existing token')
            except Exception as e:
                self.logger.warning(f'Failed to load token: {e}')
                self.token_path.unlink()
        
        # Refresh or get new credentials
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired:
                try:
                    self.creds.refresh(Request())
                    self.logger.info('Refreshed expired token')
                except RefreshError:
                    self.logger.warning('Token refresh failed, re-authorizing')
                    self.creds = None
            
            if not self.creds:
                if not self.credentials_path.exists():
                    self.logger.error(f'Credentials file not found: {self.credentials_path}')
                    self.logger.error('Place credentials.json in project root')
                    self.logger.error('Download from: https://console.cloud.google.com/apis/credentials')
                    return False
                
                try:
                    self.logger.info('Starting OAuth authorization flow...')
                    self.logger.info('Opening browser for authorization...')
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                    
                    # Save token
                    self.token_path.write_text(self.creds.to_json())
                    self.logger.info(f'Token saved to: {self.token_path}')
                    self.logger.info('✓ Authorization successful!')
                    
                except Exception as e:
                    self.logger.error(f'Authentication failed: {e}')
                    return False
        
        # Build service
        try:
            self.service = build('gmail', 'v1', credentials=self.creds)
            self.logger.info('Gmail service initialized')
            return True
        except Exception as e:
            self.logger.error(f'Failed to build service: {e}')
            return False
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Gmail for new messages.
        
        Returns:
            List of message dictionaries
        """
        messages = []
        
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Search for messages
            self.logger.debug(f'Searching: {self.query}')
            results = self.service.users().messages().list(
                userId='me',
                labelIds=[self.label],
                q=self.query,
                maxResults=10
            ).execute()
            
            message_list = results.get('messages', [])
            
            # Filter out already processed
            new_messages = [
                m for m in message_list 
                if m['id'] not in self.processed_ids
            ]
            
            if new_messages:
                self.logger.info(f'Found {len(new_messages)} new message(s)')
                
                # Get full message details
                for msg in new_messages:
                    try:
                        full_msg = self.service.users().messages().get(
                            userId='me',
                            id=msg['id'],
                            format='full'
                        ).execute()
                        
                        messages.append(self._parse_message(full_msg))
                        self.processed_ids.add(msg['id'])
                    
                    except Exception as e:
                        self.logger.error(f'Error fetching message {msg["id"]}: {e}')
            
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            
            # Try to re-authenticate
            self.service = None
        
        return messages
    
    def _parse_message(self, message: Dict) -> Dict[str, Any]:
        """
        Parse Gmail message into dictionary.
        
        Args:
            message: Gmail API message object
            
        Returns:
            Parsed message dictionary
        """
        payload = message.get('payload', {})
        headers = {h['name']: h['value'] for h in payload.get('headers', [])}
        
        # Get body
        body = ''
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        elif 'body' in payload and 'data' in payload['body']:
            body = urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        # Get attachments info
        attachments = []
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename'):
                    attachments.append({
                        'filename': part['filename'],
                        'size': part['body'].get('size', 0)
                    })
        
        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'from': headers.get('From', 'Unknown'),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', 'No Subject'),
            'date': headers.get('Date', ''),
            'body': body,
            'attachments': attachments,
            'labels': message.get('labelIds', []),
            'snippet': message.get('snippet', '')
        }
    
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create action file for detected email.

        Args:
            item: Email data dictionary

        Returns:
            Path to created action file
        """
        # Helper to sanitize Unicode characters - encode to ASCII
        def sanitize_text(text):
            if not text:
                return ""
            # Encode to ASCII, ignoring non-ASCII characters
            return text.encode('ascii', 'ignore').decode('ascii')
        
        # Extract sender name
        from_name = item['from'].split('<')[0].strip()
        safe_from = self.sanitize_filename(from_name.lower().replace(' ', '_'))

        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"EMAIL_{safe_from}_{timestamp}.md"
        filepath = self.needs_action / filename

        # Format body with proper line breaks and sanitize
        body_lines = item['body'].split('\n')
        sanitized_lines = []
        for line in body_lines[:50]:
            safe_line = sanitize_text(line)
            sanitized_lines.append(f"> {safe_line}")
        formatted_body = '\n'.join(sanitized_lines)
        if len(body_lines) > 50:
            formatted_body += f"\n> ... ({len(body_lines) - 50} more lines)"

        # Create markdown content with sanitized fields
        # Sanitize labels too
        safe_labels = [sanitize_text(label) for label in item['labels']]
        
        content = f'''---
type: email
from: {sanitize_text(item['from'])}
to: {sanitize_text(item['to'])}
subject: {sanitize_text(item['subject'])}
received: {datetime.now().isoformat()}
priority: high
status: pending
message_id: <{item['id']}@gmail.com>
labels: [{', '.join(safe_labels)}]
---

# Email Message

## Subject
{sanitize_text(item['subject'])}

## From
{sanitize_text(item['from'])}

## To
{sanitize_text(item['to'])}

## Received
{item['date']}

## Email Content

{formatted_body}

## Attachments

{self._format_attachments(item['attachments'])}

## Suggested Actions

- [ ] Read and understand the email
- [ ] Determine appropriate response
- [ ] Draft reply (requires approval)
- [ ] Attach files if needed
- [ ] Send via Email MCP
- [ ] Mark email as read in Gmail
- [ ] Move to Done when complete

## Notes

<!-- Add any additional context or notes here -->

---
*Created by Gmail Watcher*
'''

        # Write file with UTF-8 encoding
        filepath.write_text(content, encoding='utf-8')
        
        # Log the action
        self._log_action('email_received', item['from'], filepath, {
            'subject': item['subject'],
            'message_id': item['id']
        })
        
        return filepath
    
    def _format_attachments(self, attachments: List[Dict]) -> str:
        """Format attachments list for markdown."""
        if not attachments:
            return "None"

        lines = []
        for att in attachments:
            lines.append(f"- [Attachment] {att['filename']} ({att['size']} bytes)")
        return '\n'.join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Gmail Watcher')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=120, help='Check interval (default: 120s)')
    parser.add_argument('--credentials', help='Path to credentials.json')
    parser.add_argument('--token', help='Path to token.json')
    parser.add_argument('--label', default='INBOX', help='Gmail label to monitor')
    parser.add_argument('--query', default='is:unread is:important', help='Gmail search query')
    parser.add_argument('--authorize', action='store_true', help='Run authorization flow')
    parser.add_argument('--verbose', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Create watcher
    watcher = GmailWatcher(
        vault_path=args.vault,
        credentials_path=args.credentials,
        token_path=args.token,
        label=args.label,
        query=args.query,
        check_interval=args.interval
    )
    
    if args.authorize:
        print("\n" + "=" * 60)
        print("   Gmail API Authorization")
        print("=" * 60 + "\n")
        print("This will open a browser window for Gmail API authorization.")
        print("Please sign in with your Google account and grant permissions.\n")
        
        if watcher.authenticate():
            print("\n[OK] Authorization successful!")
            print(f"  Token saved to: {watcher.token_path}")
            print("\nYou can now start the watcher:")
            print(f"  python gmail_watcher.py --vault {args.vault}")
        else:
            print("\n[FAIL] Authorization failed")
            print("\nTroubleshooting:")
            print("  1. Ensure credentials.json is in project root")
            print("  2. Verify Gmail API is enabled in Google Cloud Console")
            print("  3. Check that OAuth consent screen is configured")
            return 1
    else:
        # Run watcher
        if args.verbose:
            watcher.logger.setLevel(logging.DEBUG)
        watcher.run()


if __name__ == '__main__':
    import logging
    main()
