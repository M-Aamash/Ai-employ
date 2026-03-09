"""
HITL Workflow Manager - Human-in-the-Loop Approval System

Manages approval requests for sensitive actions like sending emails.

Usage:
    python hitl_manager.py --vault ./AI_Employee_Vault --action list
    python hitl_manager.py --vault ./AI_Employee_Vault --action process
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class HITLManager:
    """Human-in-the-Loop approval workflow manager."""
    
    def __init__(self, vault_path: str):
        """
        Initialize HITL manager.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        for path in [self.pending_approval, self.approved, self.rejected, self.done, self.logs]:
            path.mkdir(parents=True, exist_ok=True)
    
    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from markdown."""
        import re
        match = re.search(r'^---\s*\n(.*?)\n---\s*$', content, re.DOTALL)
        if match:
            fm_text = match.group(1)
            frontmatter = {}
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    frontmatter[key] = value
            return frontmatter
        return {}
    
    def create_approval_request(self, action_type: str, details: Dict[str, Any], 
                                content: str = "") -> Path:
        """
        Create a new approval request.
        
        Args:
            action_type: Type of action (send_email, payment, etc.)
            details: Action-specific details
            content: Full content for the approval file
            
        Returns:
            Path to created approval file
        """
        timestamp = datetime.now()
        request_id = f"APPROVAL_{timestamp.strftime('%Y%m%d_%H%M%S')}_{action_type.upper()[:3]}"
        
        # Set expiration (24 hours)
        from datetime import timedelta
        expires = timestamp + timedelta(hours=24)
        
        # Create content if not provided
        if not content:
            content = f'''---
type: approval_request
action: {action_type}
created: {timestamp.isoformat()}
expires: {expires.isoformat()}
status: pending
priority: {details.get('priority', 'medium')}
request_id: {request_id}
---

# Approval Request: {action_type.replace('_', ' ').title()}

## Action Details

{chr(10).join([f"- **{k.replace('_', ' ').title()}:** {v}" for k, v in details.items()])}

## To Approve

Move this file to: `/Vault/Approved/`

## To Reject

Move this file to: `/Vault/Rejected/`
Add comment explaining rejection reason.

---
*Created by HITL Workflow Manager*
'''
        
        # Create file
        filename = f"{request_id}.md"
        filepath = self.pending_approval / filename
        filepath.write_text(content, encoding='utf-8')
        
        # Log creation
        self._log_event('approval_created', request_id, action_type)
        
        return filepath
    
    def list_pending(self) -> List[Dict[str, Any]]:
        """List all pending approval requests."""
        pending = []
        
        for approval_file in self.pending_approval.glob('*.md'):
            content = approval_file.read_text(encoding='utf-8')
            metadata = self._parse_frontmatter(content)
            
            pending.append({
                'file': approval_file.name,
                'action': metadata.get('action'),
                'created': metadata.get('created'),
                'expires': metadata.get('expires'),
                'priority': metadata.get('priority', 'medium'),
                'path': str(approval_file)
            })
        
        return sorted(pending, key=lambda x: x.get('priority', 'low'))
    
    def process_approved(self) -> List[Dict[str, Any]]:
        """
        Process all approved requests.
        
        Returns:
            List of executed actions
        """
        executed = []
        
        for approval_file in self.approved.glob('*.md'):
            try:
                content = approval_file.read_text(encoding='utf-8')
                metadata = self._parse_frontmatter(content)
                
                action_type = metadata.get('action', 'unknown')
                request_id = metadata.get('request_id', approval_file.stem)
                
                # Execute based on action type
                if action_type == 'send_email':
                    result = self._execute_email_send(metadata, content)
                else:
                    result = {'status': 'unknown_action', 'action': action_type}
                
                # Log and move to Done
                self._log_event('approval_executed', request_id, action_type, result)
                
                # Move to Done
                done_file = self.done / approval_file.name
                shutil.move(str(approval_file), str(done_file))
                
                executed.append({
                    'request_id': request_id,
                    'action': action_type,
                    'result': result
                })
                
            except Exception as e:
                self._log_event('execution_error', approval_file.stem, str(e))
        
        return executed
    
    def _execute_email_send(self, metadata: Dict, content: str) -> Dict:
        """Execute email send action."""
        # For now, just log that email would be sent
        # In production, this would call the Email MCP server
        
        to = metadata.get('to', 'unknown')
        subject = metadata.get('subject', 'unknown')
        
        return {
            'status': 'simulated',
            'action': 'email_send',
            'to': to,
            'subject': subject,
            'message': 'Email ready to send via Email MCP server'
        }
    
    def _log_event(self, event_type: str, request_id: str, action: str, 
                   result: Dict = None):
        """Log event to JSON log file."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'request_id': request_id,
            'action': action,
            'result': result or {}
        }
        
        log_file = self.logs / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        
        if log_file.exists():
            logs = json.loads(log_file.read_text(encoding='utf-8'))
        else:
            logs = []
        
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def check_expirations(self) -> List[Path]:
        """Check for expired approval requests."""
        expired = []
        now = datetime.now()
        
        for approval_file in self.pending_approval.glob('*.md'):
            content = approval_file.read_text(encoding='utf-8')
            metadata = self._parse_frontmatter(content)
            
            expires_str = metadata.get('expires', '')
            if expires_str:
                try:
                    expires = datetime.fromisoformat(expires_str)
                    if expires < now:
                        # Expired - move to Rejected with note
                        self._reject_expired(approval_file)
                        expired.append(approval_file)
                except:
                    pass
        
        return expired
    
    def _reject_expired(self, filepath: Path):
        """Move expired approval to Rejected with note."""
        content = filepath.read_text(encoding='utf-8')
        content += f"\n\n## Expired\n\nThis request expired at {datetime.now().isoformat()} without approval.\n"
        filepath.write_text(content, encoding='utf-8')
        
        dest = self.rejected / filepath.name
        shutil.move(str(filepath), str(dest))
        
        self._log_event('approval_expired', filepath.stem, 'expired')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='HITL Workflow Manager')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--action', required=True, 
                       choices=['list', 'process', 'check-expiry'],
                       help='Action to perform')
    
    args = parser.parse_args()
    
    manager = HITLManager(args.vault)
    
    if args.action == 'list':
        pending = manager.list_pending()
        print(f"\nPending approvals: {len(pending)}\n")
        for item in pending:
            print(f"  - {item['file']}")
            print(f"    Action: {item['action']}")
            print(f"    Priority: {item['priority']}")
            print(f"    Created: {item['created']}")
            print()
    
    elif args.action == 'process':
        executed = manager.process_approved()
        print(f"\nProcessed {len(executed)} approval(s)\n")
        for item in executed:
            print(f"  - {item['request_id']}: {item['action']}")
            if item['result'].get('status') == 'simulated':
                print(f"    To: {item['result'].get('to')}")
                print(f"    Subject: {item['result'].get('subject')}")
            print()
    
    elif args.action == 'check-expiry':
        expired = manager.check_expirations()
        print(f"\nExpired approvals: {len(expired)}\n")
        for item in expired:
            print(f"  - {item.name}")


if __name__ == '__main__':
    main()
