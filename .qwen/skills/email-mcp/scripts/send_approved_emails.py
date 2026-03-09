"""
Send Approved Emails

Processes approved emails from Pending_Approval folder and sends them via Email MCP.

Usage:
    python send_approved_emails.py
"""

import sys
import os
import json
import pickle
import base64
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set UTF-8 encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    print("Installing Gmail API dependencies...")
    os.system('pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib')
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build


class ApprovedEmailSender:
    """Send approved emails from Pending_Approval folder."""
    
    def __init__(self, vault_path=None):
        """Initialize sender."""
        self.vault_path = Path(vault_path) if vault_path else Path.cwd() / 'AI_Employee_Vault'
        self.approved_path = self.vault_path / 'Approved'
        self.done_path = self.vault_path / 'Done'
        self.logs_path = self.vault_path / 'Logs'
        
        for path in [self.approved_path, self.done_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Load Gmail token
        self.token_path = self.vault_path / '.gmail' / '.gmail_token.pkl'
        self.service = self._init_gmail_service()
    
    def _init_gmail_service(self):
        """Initialize Gmail API service."""
        if not self.token_path.exists():
            print(f"Token not found: {self.token_path}")
            print("Run: python authenticate_gmail.py")
            return None
        
        try:
            with open(self.token_path, 'rb') as f:
                creds = pickle.load(f)
            
            service = build('gmail', 'v1', credentials=creds)
            print("OK - Gmail service initialized\n")
            return service
        except Exception as e:
            print(f"Failed to initialize Gmail: {e}")
            return None
    
    def send_email(self, to, subject, body, cc=None):
        """Send email via Gmail API."""
        if not self.service:
            return None
        
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return sent_message
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return None
    
    def _parse_frontmatter(self, content):
        """Parse YAML frontmatter from markdown."""
        import re
        match = re.search(r'^---\s*\n(.*?)\n---\s*$', content, re.DOTALL | re.MULTILINE)
        if match:
            fm_text = match.group(1)
            frontmatter = {}
            for line in fm_text.split('\n'):
                line = line.strip()
                if ':' in line and not line.startswith('#'):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    frontmatter[key] = value
            return frontmatter
        return {}
    
    def _is_outgoing_email(self, metadata):
        """Check if this is an outgoing email approval (not incoming)."""
        # Outgoing emails have 'action: send_email' in approval requests
        action_type = metadata.get('action', '')
        file_type = metadata.get('type', '')
        
        # Debug: print what we found
        print(f"  DEBUG - type: {file_type}, action: {action_type}")
        
        # If it's an approval request for sending, process it
        if action_type == 'send_email':
            return True
        
        # If it's a regular email (from Gmail Watcher), skip it
        if file_type == 'email':
            return False
        
        # Default: if it has 'to' field and action, treat as outgoing
        if metadata.get('to') and action_type:
            return True
        
        return False
    
    def process_approved(self):
        """Process all approved emails."""
        print("=" * 70)
        print("   Processing Approved Emails")
        print("=" * 70 + "\n")
        
        if not self.service:
            print("ERROR: Gmail service not initialized\n")
            return
        
        # Find approved files
        approved_files = list(self.approved_path.glob('APPROVAL_*.md'))
        
        if not approved_files:
            print("No approved emails to send.\n")
            return
        
        print(f"Found {len(approved_files)} approved email(s)\n")
        
        sent_count = 0
        failed_count = 0
        
        for approved_file in approved_files:
            print(f"Processing: {approved_file.name}")
            
            try:
                content = approved_file.read_text(encoding='utf-8')
                metadata = self._parse_frontmatter(content)
                
                # Check if this is an outgoing email approval
                if not self._is_outgoing_email(metadata):
                    print(f"  SKIPPED - This is an incoming email (not an approval request)")
                    print(f"  Move to Done/ folder manually if processed\n")
                    continue
                
                to = metadata.get('to', '')
                subject = metadata.get('subject', '')
                
                # Extract email body from content (everything after frontmatter)
                body_start = content.find('---\n', 3)  # Skip first ---
                if body_start == -1:
                    body_start = content.find('---', 3)
                
                if body_start > 0:
                    # Find the second ---
                    body_end = content.find('---', body_start + 3)
                    if body_end > 0:
                        body = content[body_start:body_end].strip()
                    else:
                        body = content[body_start:].strip()
                else:
                    body = content
                
                # If no body found, create one from metadata
                if not body or len(body) < 10:
                    body = f"Dear {to},\n\nThis is an automated email.\n\nBest regards"
                
                # Send email
                result = self.send_email(to, subject, body)
                
                if result:
                    print(f"  OK - Sent to: {to}")
                    print(f"  OK - Message ID: {result['id']}\n")
                    
                    # Move to Done
                    done_file = self.done_path / approved_file.name
                    approved_file.rename(done_file)
                    
                    # Log
                    self._log_action('email_sent', {
                        'to': to,
                        'subject': subject,
                        'message_id': result['id'],
                        'file': approved_file.name
                    })
                    
                    sent_count += 1
                else:
                    print(f"  FAILED - Could not send\n")
                    failed_count += 1
                    
            except Exception as e:
                print(f"  ERROR - {e}\n")
                failed_count += 1
        
        # Summary
        print("=" * 70)
        print(f"   Sent: {sent_count} | Failed: {failed_count}")
        print("=" * 70 + "\n")
    
    def _log_action(self, action_type, details):
        """Log action to JSON log file."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'approved_email_sender',
            'details': details
        }
        
        log_file = self.logs_path / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text(encoding='utf-8'))
            except:
                logs = []
        
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding='utf-8')


def main():
    """Main entry point."""
    print("\n")
    sender = ApprovedEmailSender()
    sender.process_approved()


if __name__ == '__main__':
    main()
