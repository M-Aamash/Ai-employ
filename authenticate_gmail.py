"""
Gmail Authentication - Generate Token

This script authenticates with Gmail API and generates the token file.
Run this ONCE to authorize the AI Employee to access your Gmail.

Usage:
    python authenticate_gmail.py
"""

import os
import pickle
from pathlib import Path
from typing import Optional

# Set encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Gmail API imports
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    print("Installing Gmail API dependencies...")
    os.system('pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib')
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.modify',
]

def main():
    print("\n" + "=" * 70)
    print("   Gmail Authentication - AI Employee")
    print("=" * 70 + "\n")
    
    # Paths
    vault_path = Path.cwd() / 'AI_Employee_Vault'
    gmail_folder = vault_path / '.gmail'
    gmail_folder.mkdir(parents=True, exist_ok=True)
    
    token_file = gmail_folder / '.gmail_token.pkl'
    credentials_file = Path.cwd() / 'credentials.json'
    
    print(f"Vault: {vault_path}")
    print(f"Token will be saved to: {token_file}")
    print(f"Credentials: {credentials_file}\n")
    
    # Check credentials
    if not credentials_file.exists():
        print("ERROR: credentials.json not found!\n")
        print("Download from:")
        print("  https://console.cloud.google.com/apis/credentials\n")
        print("Steps:")
        print("  1. Create OAuth 2.0 credentials")
        print("  2. Application type: Desktop app")
        print("  3. Download credentials.json")
        print("  4. Place in project root\n")
        return
    
    creds = None
    
    # Load existing token
    if token_file.exists():
        print("Loading existing token...")
        try:
            with open(token_file, 'rb') as f:
                creds = pickle.load(f)
            print("OK - Token loaded\n")
        except Exception as e:
            print(f"Failed to load token: {e}\n")
            token_file.unlink()
    
    # Authenticate if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("OK - Token refreshed\n")
                with open(token_file, 'wb') as f:
                    pickle.dump(creds, f)
                print(f"Token saved to: {token_file}\n")
                return
            except Exception as e:
                print(f"Refresh failed: {e}\n")
                creds = None
        
        if not creds:
            print("=" * 70)
            print("   AUTHENTICATING WITH GMAIL")
            print("=" * 70 + "\n")
            print("A browser window will open.")
            print("Please sign in with your Google account and grant permissions.\n")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file,
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
                
                print("\nOK - Authentication successful!\n")
                
                # Save token
                with open(token_file, 'wb') as f:
                    pickle.dump(creds, f)
                print(f"Token saved to: {token_file}\n")
                
                # Test connection
                from googleapiclient.discovery import build
                service = build('gmail', 'v1', credentials=creds)
                profile = service.users().getProfile().execute()
                
                print("=" * 70)
                print("   SUCCESS - GMAIL AUTHENTICATED!")
                print("=" * 70)
                print(f"\nConnected: {profile['emailAddress']}")
                print(f"Total emails: {profile['messagesTotal']}")
                print(f"Unread: {profile['messagesUnread']}\n")
                print("You can now use Gmail Watcher:")
                print("  python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault\n")
                
            except Exception as e:
                print(f"\nAuthentication failed: {e}\n")
                print("Please check:")
                print("  1. credentials.json is valid")
                print("  2. Gmail API is enabled")
                print("  3. OAuth consent screen is configured\n")
    else:
        print("Already authenticated!\n")
        # Test connection
        try:
            from googleapiclient.discovery import build
            service = build('gmail', 'v1', credentials=creds)
            profile = service.users().getProfile().execute()
            print("=" * 70)
            print("   GMAIL CONNECTED!")
            print("=" * 70)
            print(f"\nConnected: {profile['emailAddress']}")
            print(f"Total emails: {profile['messagesTotal']}\n")
        except:
            print("Token exists but connection failed. Re-authenticating...\n")
            main()

if __name__ == '__main__':
    main()
