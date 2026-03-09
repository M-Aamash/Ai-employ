"""
Plan Generator - Create structured Plan.md files from action items.

This script analyzes files in Needs_Action folder and generates
structured action plans for Qwen Code to execute.

Usage:
    python plan_generator.py --vault /path/to/vault --all
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class PlanGenerator:
    """Generate structured action plans from action items."""
    
    def __init__(self, vault_path: str):
        """
        Initialize plan generator.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans_path = self.vault_path / 'Plans'
        self.in_progress = self.vault_path / 'In_Progress'
        self.handbook_path = self.vault_path / 'Company_Handbook.md'
        self.goals_path = self.vault_path / 'Business_Goals.md'
        
        # Ensure directories exist
        self.plans_path.mkdir(parents=True, exist_ok=True)
        self.in_progress.mkdir(parents=True, exist_ok=True)
        
        # Load context
        self.handbook = self._load_context(self.handbook_path)
        self.goals = self._load_context(self.goals_path)
    
    def _load_context(self, path: Path) -> str:
        """Load context file if it exists."""
        if path.exists():
            return path.read_text(encoding='utf-8')
        return ""
    
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
                    if value.startswith('[') and value.endswith(']'):
                        value = [v.strip() for v in value[1:-1].split(',')]
                    frontmatter[key] = value
            return frontmatter
        return {}
    
    def _determine_plan_type(self, content: str, frontmatter: Dict) -> str:
        """Determine plan type from content."""
        action_type = frontmatter.get('type', '').lower()
        
        if action_type == 'email':
            return 'email_response'
        elif action_type == 'whatsapp':
            return 'message_response'
        elif action_type == 'linkedin':
            return 'social_engagement'
        elif 'invoice' in content.lower() or 'payment' in content.lower():
            return 'invoice_generation'
        elif 'pricing' in content.lower() or 'quote' in content.lower():
            return 'lead_followup'
        else:
            return 'general_task'
    
    def _determine_priority(self, content: str, frontmatter: Dict) -> str:
        """Determine priority from content."""
        content_lower = content.lower()
        
        # High priority keywords
        high_keywords = ['urgent', 'asap', 'emergency', 'critical', 'immediately']
        if any(kw in content_lower for kw in high_keywords):
            return 'high'
        
        # Medium priority (business-related)
        medium_keywords = ['invoice', 'payment', 'client', 'customer', 'pricing']
        if any(kw in content_lower for kw in medium_keywords):
            return 'medium'
        
        return 'low'
    
    def _estimate_time(self, plan_type: str) -> str:
        """Estimate time required for plan type."""
        estimates = {
            'email_response': '15m',
            'message_response': '10m',
            'invoice_generation': '30m',
            'lead_followup': '45m',
            'social_engagement': '20m',
            'file_processing': '20m',
            'general_task': '30m'
        }
        return estimates.get(plan_type, '30m')
    
    def _generate_steps(self, plan_type: str, content: str, frontmatter: Dict) -> List[Dict]:
        """Generate task steps based on plan type."""
        steps = {
            'email_response': [
                {'task': 'Read and understand the email', 'done': False},
                {'task': 'Determine appropriate response', 'done': False},
                {'task': 'Draft reply (requires approval)', 'done': False},
                {'task': 'Attach files if needed', 'done': False},
                {'task': 'Send via Email MCP', 'done': False, 'approval': True},
                {'task': 'Mark original email as read', 'done': False},
                {'task': 'Move to Done when complete', 'done': False},
            ],
            'message_response': [
                {'task': 'Read and understand the message', 'done': False},
                {'task': 'Determine appropriate response', 'done': False},
                {'task': 'Draft reply (requires approval)', 'done': False},
                {'task': 'Send via messaging platform', 'done': False, 'approval': True},
                {'task': 'Move to Done when complete', 'done': False},
            ],
            'invoice_generation': [
                {'task': 'Identify client and account details', 'done': True},
                {'task': 'Calculate amount from rates', 'done': True},
                {'task': 'Generate invoice PDF', 'done': False},
                {'task': 'Send via email (requires approval)', 'done': False, 'approval': True},
                {'task': 'Log transaction in accounting', 'done': False},
                {'task': 'Mark as complete', 'done': False},
            ],
            'lead_followup': [
                {'task': 'Extract contact information', 'done': True},
                {'task': 'Research company background', 'done': False},
                {'task': 'Prepare pricing information', 'done': False},
                {'task': 'Draft personalized response (approval required)', 'done': False},
                {'task': 'Send response', 'done': False, 'approval': True},
                {'task': 'Schedule follow-up task', 'done': False},
            ],
            'social_engagement': [
                {'task': 'Review LinkedIn engagement', 'done': True},
                {'task': 'Determine response strategy', 'done': False},
                {'task': 'Draft response (requires approval)', 'done': False},
                {'task': 'Post/send response', 'done': False, 'approval': True},
                {'task': 'Log interaction', 'done': False},
            ],
            'general_task': [
                {'task': 'Analyze task requirements', 'done': True},
                {'task': 'Identify required resources', 'done': False},
                {'task': 'Execute task steps', 'done': False},
                {'task': 'Review and verify completion', 'done': False},
                {'task': 'Move to Done', 'done': False},
            ],
        }
        
        return steps.get(plan_type, steps['general_task'])
    
    def _check_approval_required(self, content: str, plan_type: str) -> bool:
        """Check if task requires human approval."""
        # Always require approval for sending actions
        send_keywords = ['send', 'email', 'reply', 'post', 'payment']
        if any(kw in plan_type.lower() for kw in ['email', 'message', 'invoice']):
            return True
        
        # Check content for sensitive actions
        content_lower = content.lower()
        if any(kw in content_lower for kw in send_keywords):
            return True
        
        return False
    
    def generate_plan(self, action_file: Path) -> Path:
        """
        Generate plan from action file.
        
        Args:
            action_file: Path to action file
            
        Returns:
            Path to created plan file
        """
        # Read action file
        content = action_file.read_text(encoding='utf-8')
        frontmatter = self._parse_frontmatter(content)
        
        # Determine plan characteristics
        plan_type = self._determine_plan_type(content, frontmatter)
        priority = self._determine_priority(content, frontmatter)
        estimated_time = self._estimate_time(plan_type)
        steps = self._generate_steps(plan_type, content, frontmatter)
        approval_required = self._check_approval_required(content, plan_type)
        
        # Extract key info
        from_field = frontmatter.get('from', frontmatter.get('contact', 'Unknown'))
        subject = frontmatter.get('subject', action_file.stem)
        received = frontmatter.get('received', datetime.now().isoformat())
        
        # Generate steps markdown
        steps_md = '\n'.join([
            f"- {'[x]' if s.get('done') else '[ ]'} {s['task']}" + 
            (" **(REQUIRES APPROVAL)**" if s.get('approval') else "")
            for s in steps
        ])
        
        # Create plan content
        plan_content = f'''---
created: {datetime.now().isoformat()}
status: {"pending_approval" if approval_required else "in_progress"}
source: {action_file.name}
type: {plan_type}
priority: {priority}
estimated_time: {estimated_time}
---

# Plan: {subject}

## Objective
{self._generate_objective(plan_type, subject, from_field)}

## Context

### Source
- Type: {frontmatter.get('type', 'Unknown')}
- From: {from_field}
- Subject: {subject}
- Received: {received}

### Background
{self._generate_background(content, plan_type)}

## Steps

{steps_md}

## Approval Required

{"This task requires human approval before proceeding with sensitive actions." if approval_required else "No approval required for this task."}

{"See /Pending_Approval/ for approval request file." if approval_required else ""}

## Resources

- Company Handbook: /Vault/Company_Handbook.md
- Business Goals: /Vault/Business_Goals.md
{self._get_additional_resources(plan_type)}

## Notes

<!-- Add any additional context or decisions here -->

---
*Generated by Plan Generator (Qwen Code)*
'''
        
        # Create plan filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        plan_filename = f"PLAN_{plan_type}_{timestamp}.md"
        plan_path = self.plans_path / plan_filename
        
        # Write plan file
        plan_path.write_text(plan_content, encoding='utf-8')
        
        return plan_path
    
    def _generate_objective(self, plan_type: str, subject: str, from_field: str) -> str:
        """Generate objective statement."""
        objectives = {
            'email_response': f"Draft and send appropriate response to email from {from_field}.",
            'message_response': f"Respond to message from {from_field}.",
            'invoice_generation': f"Generate and send invoice for: {subject}.",
            'lead_followup': f"Follow up on pricing inquiry from {from_field}.",
            'social_engagement': f"Respond to LinkedIn engagement.",
            'file_processing': f"Process file and take required actions.",
            'general_task': f"Complete task: {subject}.",
        }
        return objectives.get(plan_type, f"Handle: {subject}")
    
    def _generate_background(self, content: str, plan_type: str) -> str:
        """Generate background context."""
        # Extract first meaningful paragraph
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('---') and not line.startswith('['):
                if len(line) > 50:
                    return line[:200] + ("..." if len(line) > 200 else "")
        return "Processing request from user."
    
    def _get_additional_resources(self, plan_type: str) -> str:
        """Get additional resources based on plan type."""
        resources = {
            'email_response': '- Email Templates: /Vault/Templates/Email/',
            'invoice_generation': '- Rates: /Vault/Accounting/Rates.md\n- Invoice Template: /Vault/Templates/Invoice_Template.md',
            'lead_followup': '- Pricing: /Vault/Accounting/Pricing.md\n- CRM: /Vault/Accounting/Clients.md',
            'social_engagement': '- Social Media Guidelines: /Vault/Company_Handbook.md',
        }
        return resources.get(plan_type, '')
    
    def process_all(self) -> List[Path]:
        """
        Process all action files in Needs_Action.
        
        Returns:
            List of created plan file paths
        """
        plan_paths = []
        
        # Get all markdown files
        action_files = list(self.needs_action.glob('*.md'))
        
        if not action_files:
            print("No action files to process")
            return plan_paths
        
        # Sort by priority (high first)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        
        for action_file in action_files:
            try:
                content = action_file.read_text(encoding='utf-8')
                frontmatter = self._parse_frontmatter(content)
                priority = self._determine_priority(content, frontmatter)
                
                plan_path = self.generate_plan(action_file)
                plan_paths.append((priority_order.get(priority, 2), plan_path))
                
                print(f"Generated plan: {plan_path.name}")
                
            except Exception as e:
                print(f"Error processing {action_file.name}: {e}")
        
        # Sort by priority and return paths
        plan_paths.sort(key=lambda x: x[0])
        return [p[1] for p in plan_paths]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Plan Generator')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--file', help='Specific action file to process')
    parser.add_argument('--all', action='store_true', help='Process all action files')
    
    args = parser.parse_args()
    
    generator = PlanGenerator(args.vault)
    
    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            plan_path = generator.generate_plan(file_path)
            print(f"Plan created: {plan_path}")
        else:
            print(f"File not found: {file_path}")
            return 1
    elif args.all:
        plans = generator.process_all()
        print(f"\nGenerated {len(plans)} plan(s)")
    else:
        # Default: process all
        plans = generator.process_all()
        print(f"\nGenerated {len(plans)} plan(s)")


if __name__ == '__main__':
    main()
