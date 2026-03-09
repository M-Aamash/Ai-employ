"""
Gmail Token Verification

Verifies the Gmail token is valid and working.
"""

import os
import pickle
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8'

def main():
    print("\n" + "=" * 70)
    print("   Gmail Token Verification")
    print("=" * 70 + "\n")
    
    # Token path
    vault_path = Path.cwd() / 'AI_Employee_Vault'
    token_file = vault_path / '.gmail' / '.gmail_token.pkl'
    
    print(f"Token file: {token_file}\n")
    
    # Check if token exists
    if not token_file.exists():
        print("Token not found!\n")
        print("Run authentication first:")
        print("  python authenticate_gmail.py\n")
        return
    
    # Load token
    print("Loading token...")
    try:
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        print("OK - Token loaded\n")
    except Exception as e:
        print(f"Failed to load token: {e}\n")
        return
    
    # Check if valid
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            print("Token expired, refreshing...")
            try:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                print("OK - Token refreshed\n")
                
                # Save refreshed token
                with open(token_file, 'wb') as f:
                    pickle.dump(creds, f)
                print("Token saved\n")
            except Exception as e:
                print(f"Refresh failed: {e}\n")
                print("Re-authenticate:")
                print("  python authenticate_gmail.py\n")
                return
        else:
            print("Token invalid\n")
            print("Re-authenticate:")
            print("  python authenticate_gmail.py\n")
            return
    
    # Test Gmail connection
    print("Testing Gmail connection...")
    try:
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        
        print("=" * 70)
        print("   GMAIL CONNECTED!")
        print("=" * 70)
        print(f"\nEmail: {profile['emailAddress']}")
        print(f"Total messages: {profile['messagesTotal']}")
        print(f"Unread: {profile.get('messagesUnread', 'N/A')}\n")
        print("Gmail Watcher is ready to use:\n")
        print("  python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --interval 120\n")
        
    except Exception as e:
        print(f"Connection failed: {e}\n")
        print("Re-authenticate:")
        print("  python authenticate_gmail.py\n")

if __name__ == '__main__':
    main()
