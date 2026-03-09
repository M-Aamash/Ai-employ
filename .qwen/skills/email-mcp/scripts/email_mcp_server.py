"""
Email MCP Server - Send Emails via Gmail API

This MCP server allows sending emails through Gmail API.
Integrates with the AI Employee HITL workflow.

Usage:
    python email_mcp_server.py --port 8810
"""

import sys
import os
import json
import base64
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError:
    print("Installing Gmail API dependencies...")
    os.system('pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib')
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart


class EmailMCP:
    """Email MCP - Send emails via Gmail API."""
    
    def __init__(self, vault_path=None):
        """Initialize Email MCP."""
        self.vault_path = Path(vault_path) if vault_path else Path.cwd() / 'AI_Employee_Vault'
        self.logs_path = self.vault_path / 'Logs'
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
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
            import pickle
            with open(self.token_path, 'rb') as f:
                creds = pickle.load(f)
            
            service = build('gmail', 'v1', credentials=creds)
            print("Gmail service initialized")
            return service
        except Exception as e:
            print(f"Failed to initialize Gmail: {e}")
            return None
    
    def send_email(self, to, subject, body, cc=None, bcc=None, attachments=None):
        """
        Send email via Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            cc: CC recipient (optional)
            bcc: BCC recipient (optional)
            attachments: List of attachment file paths (optional)
            
        Returns:
            dict: Result with status and message_id
        """
        if not self.service:
            return {'status': 'error', 'message': 'Gmail service not initialized'}
        
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    self._attach_file(message, file_path)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            # Log the action
            self._log_action('email_sent', {
                'to': to,
                'subject': subject,
                'message_id': sent_message['id']
            })
            
            return {
                'status': 'success',
                'message_id': sent_message['id'],
                'thread_id': sent_message.get('threadId')
            }
            
        except Exception as e:
            error_msg = str(e)
            self._log_action('email_failed', {
                'to': to,
                'subject': subject,
                'error': error_msg
            })
            return {'status': 'error', 'message': error_msg}
    
    def _attach_file(self, message, file_path):
        """Attach file to email."""
        from email.mime.base import MIMEBase
        from email import encoders
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Attachment not found: {file_path}")
        
        with open(path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{path.name}"'
        )
        message.attach(part)
    
    def _log_action(self, action_type, details):
        """Log action to JSON log file."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'email_mcp',
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


class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP server."""
    
    email_mcp = None
    
    def do_POST(self):
        """Handle POST requests (MCP tool calls)."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            request = json.loads(post_data.decode('utf-8'))
            tool = request.get('tool')
            params = request.get('params', {})
            
            result = self._call_tool(tool, params)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8'))
    
    def _call_tool(self, tool, params):
        """Call MCP tool."""
        if tool == 'email_send':
            return self.email_mcp.send_email(**params)
        elif tool == 'email_test':
            return {'status': 'success', 'message': 'Email MCP server is running'}
        else:
            return {'status': 'error', 'message': f'Unknown tool: {tool}'}
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('--port', type=int, default=8810, help='Server port')
    parser.add_argument('--vault', default='./AI_Employee_Vault', help='Vault path')
    
    args = parser.parse_args()
    
    # Initialize Email MCP
    print("\n" + "=" * 70)
    print("   Email MCP Server")
    print("=" * 70 + "\n")
    
    email_mcp = EmailMCP(args.vault)
    
    if not email_mcp.service:
        print("\nERROR: Gmail service not initialized!")
        print("\nRun authentication first:")
        print("  python authenticate_gmail.py\n")
        return
    
    # Start server
    MCPRequestHandler.email_mcp = email_mcp
    server = HTTPServer(('localhost', args.port), MCPRequestHandler)
    
    print(f"Email MCP Server running on http://localhost:{args.port}")
    print("\nAvailable tools:")
    print("  - email_send: Send email")
    print("  - email_test: Test connection")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
