"""
Gmail Watcher

Monitors Gmail for new unread messages and creates action files in the Needs_Action folder.
Uses the Gmail API to fetch messages.

Setup:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Download credentials.json to the credentials/ folder
4. Run once to authorize: python gmail_watcher.py --auth
"""

import os
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from email.parser import Parser

from base_watcher import BaseWatcher

# Optional Gmail imports (handle gracefully if not installed)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Gmail API libraries not installed. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new unread messages and creates action files.
    """
    
    # Scopes required for Gmail API
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, vault_path: str, credentials_path: str = None, check_interval: int = 120):
        """
        Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail credentials JSON file
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        
        if not GMAIL_AVAILABLE:
            raise ImportError("Gmail API libraries not available. Please install required packages.")
        
        # Default credentials path
        if credentials_path is None:
            credentials_path = Path(__file__).parent.parent / 'credentials' / 'gmail_credentials.json'
        
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(__file__).parent.parent / 'credentials' / 'gmail_token.json'
        self.service = None
        self._last_check_time = None
        
        # Keywords that indicate high priority
        self.priority_keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'billing',
            'important', 'action required', 'deadline', 'emergency'
        ]
        
    def authenticate(self):
        """
        Perform OAuth authentication and save token.
        Run this once to authorize the application.
        """
        creds = None
        
        # Load existing token if available
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        # If no valid credentials, perform OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    print(f"Error: Credentials file not found at {self.credentials_path}")
                    print("Please download credentials.json from Google Cloud Console")
                    return False
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Authentication successful")
        return True
    
    def _get_service(self):
        """Get or create Gmail API service."""
        if self.service is None:
            creds = None
            
            # Try to load existing token
            if self.token_path.exists():
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    self.logger.error("No valid credentials. Run with --auth flag first.")
                    return None
            
            self.service = build('gmail', 'v1', credentials=creds)
        
        return self.service
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check Gmail for new unread messages.
        
        Returns:
            List of message dictionaries
        """
        service = self._get_service()
        if service is None:
            return []
        
        try:
            # Fetch unread messages from last 24 hours
            results = service.users().messages().list(
                userId='me',
                q='is:unread newer_than:1d',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            new_messages = []
            
            for msg in messages:
                msg_id = msg['id']
                
                # Skip already processed
                if msg_id in self.processed_ids:
                    continue
                
                # Fetch full message
                message = service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()
                
                # Parse message
                parsed = self._parse_message(message)
                if parsed:
                    new_messages.append(parsed)
                    self.processed_ids.add(msg_id)
            
            self._last_check_time = datetime.now()
            return new_messages
            
        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []
    
    def _parse_message(self, message: Dict) -> Optional[Dict]:
        """
        Parse a Gmail message into a dictionary.
        
        Args:
            message: Raw Gmail message dict
            
        Returns:
            Parsed message dict or None
        """
        try:
            payload = message.get('payload', {})
            headers = {h['name']: h['value'] for h in payload.get('headers', [])}
            
            # Get body
            body = ""
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part:
                        body = base64.urlsafe_b64decode(part['data']).decode('utf-8')
                        break
            elif 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            
            # Determine priority
            subject = headers.get('Subject', '').lower()
            from_email = headers.get('From', '')
            priority = 'high' if any(kw in subject for kw in self.priority_keywords) else 'normal'
            
            return {
                'id': message['id'],
                'from': from_email,
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', ''),
                'body': body[:2000] if body else '',  # Truncate long bodies
                'priority': priority,
                'snippet': message.get('snippet', '')
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing message: {e}")
            return None
    
    def create_action_file(self, message: Dict) -> Optional[Path]:
        """
        Create a markdown action file for the message.
        
        Args:
            message: Parsed message dictionary
            
        Returns:
            Path to created file or None
        """
        try:
            # Create filename
            safe_subject = self.sanitize_filename(message['subject'][:50])
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"EMAIL_{timestamp}_{safe_subject}.md"
            filepath = self.needs_action / filename
            
            # Determine suggested actions based on content
            suggested_actions = ["- [ ] Read and process email"]
            if 'invoice' in message['subject'].lower() or 'payment' in message['subject'].lower():
                suggested_actions.extend([
                    "- [ ] Check accounting records",
                    "- [ ] Prepare response or invoice",
                    "- [ ] Flag for payment processing if needed"
                ])
            if message['priority'] == 'high':
                suggested_actions.insert(0, "- [ ] **URGENT**: Respond within 24 hours")
            
            content = f"""---
type: email
message_id: {message['id']}
from: {message['from']}
to: {message['to']}
subject: {message['subject']}
received: {self.get_timestamp()}
priority: {message['priority']}
status: unread
---

# Email: {message['subject']}

## Metadata
- **From**: {message['from']}
- **To**: {message['to']}
- **Date**: {message['date']}
- **Priority**: {message['priority']}

## Content

{message['body'] if message['body'] else message['snippet']}

## Suggested Actions

{chr(10).join(suggested_actions)}

## Notes

_Add your notes here_

---
*Created by Gmail Watcher*
"""
            
            filepath.write_text(content, encoding='utf-8')
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None


def main():
    """Main entry point for Gmail Watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('--vault', type=str, default='../AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--credentials', type=str, default=None,
                       help='Path to Gmail credentials JSON')
    parser.add_argument('--interval', type=int, default=120,
                       help='Check interval in seconds')
    parser.add_argument('--auth', action='store_true',
                       help='Run authentication flow')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    
    if not vault_path.exists():
        print(f"Error: Vault not found at {vault_path}")
        return
    
    watcher = GmailWatcher(
        vault_path=str(vault_path),
        credentials_path=args.credentials,
        check_interval=args.interval
    )
    
    if args.auth:
        print("Starting Gmail authentication...")
        if watcher.authenticate():
            print("Authentication successful! Token saved.")
        else:
            print("Authentication failed.")
    else:
        watcher.run()


if __name__ == '__main__':
    main()
