"""
Orchestrator - Master coordination system for AI Employee.

Coordinates watchers, plan generation, HITL workflow, and action execution.

Usage:
    python orchestrator.py --vault /path/to/vault --action process-queue
"""

import argparse
import json
import logging
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class Orchestrator:
    """AI Employee Orchestrator."""
    
    def __init__(self, vault_path: str, config: Dict[str, Any] = None):
        """
        Initialize orchestrator.
        
        Args:
            vault_path: Path to Obsidian vault
            config: Configuration dictionary
        """
        self.vault_path = Path(vault_path).resolve()
        self.config = config or {}
        
        # Vault paths
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.logs = self.vault_path / 'Logs'
        self.briefings = self.vault_path / 'Briefings'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure directories exist
        for path in [self.needs_action, self.in_progress, self.pending_approval,
                     self.approved, self.rejected, self.done, self.plans,
                     self.logs, self.briefings]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        self.logger.info(f"Orchestrator initialized: {self.vault_path}")
    
    def _setup_logging(self):
        """Setup logging."""
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.DEBUG if self.config.get('verbose') else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('Orchestrator')
    
    def process_queue(self) -> Dict[str, int]:
        """
        Process all files in Needs_Action queue.
        
        Returns:
            Statistics dictionary
        """
        self.logger.info("Processing queue...")
        
        stats = {
            'files_processed': 0,
            'plans_generated': 0,
            'approvals_created': 0,
            'errors': 0
        }
        
        # Get all action files
        action_files = list(self.needs_action.glob('*.md'))
        
        if not action_files:
            self.logger.info("No files to process")
            return stats
        
        self.logger.info(f"Found {len(action_files)} file(s) to process")
        
        for action_file in action_files:
            try:
                # Read file
                content = action_file.read_text(encoding='utf-8')
                frontmatter = self._parse_frontmatter(content)
                
                # Move to In_Progress
                dest = self.in_progress / action_file.name
                shutil.move(str(action_file), str(dest))
                
                # Generate plan
                plan_path = self._generate_plan(dest, content, frontmatter)
                if plan_path:
                    stats['plans_generated'] += 1
                
                # Check if approval needed
                if self._needs_approval(content, frontmatter):
                    approval_path = self._create_approval_request(dest, content, frontmatter)
                    if approval_path:
                        stats['approvals_created'] += 1
                
                stats['files_processed'] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing {action_file.name}: {e}")
                stats['errors'] += 1
        
        # Update dashboard
        self.update_dashboard()
        
        self.logger.info(f"Queue processing complete: {stats}")
        return stats
    
    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter."""
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
    
    def _generate_plan(self, action_file: Path, content: str, 
                       frontmatter: Dict) -> Optional[Path]:
        """Generate plan for action file."""
        try:
            # Import plan generator
            import sys
            sys.path.insert(0, str(Path(__file__).parent / 'plan_generator'))
            from plan_generator import PlanGenerator
            
            generator = PlanGenerator(str(self.vault_path))
            plan_path = generator.generate_plan(action_file)
            
            self.logger.info(f"Generated plan: {plan_path.name}")
            return plan_path
            
        except Exception as e:
            self.logger.error(f"Plan generation failed: {e}")
            return None
    
    def _needs_approval(self, content: str, frontmatter: Dict) -> bool:
        """Check if action requires approval."""
        # Check action type
        action_type = frontmatter.get('type', '').lower()
        if action_type in ['email', 'payment', 'social_post']:
            return True
        
        # Check content for sensitive keywords
        sensitive_keywords = ['send', 'pay', 'transfer', 'approve', 'delete']
        content_lower = content.lower()
        if any(kw in content_lower for kw in sensitive_keywords):
            return True
        
        return False
    
    def _create_approval_request(self, action_file: Path, content: str,
                                  frontmatter: Dict) -> Optional[Path]:
        """Create approval request."""
        try:
            # Import HITL manager
            import sys
            sys.path.insert(0, str(Path(__file__).parent / 'hitl_workflow'))
            from hitl_manager import HITLManager
            
            manager = HITLManager(str(self.vault_path))
            
            # Determine action type
            action_type = frontmatter.get('type', 'general')
            if action_type == 'email':
                action_type = 'send_email'
            
            # Extract details
            details = {
                'to': frontmatter.get('to', frontmatter.get('from', 'N/A')),
                'subject': frontmatter.get('subject', action_file.stem),
                'priority': frontmatter.get('priority', 'medium')
            }
            
            approval_path = manager.create_approval_request(action_type, details, content)
            
            self.logger.info(f"Created approval request: {approval_path.name}")
            return approval_path
            
        except Exception as e:
            self.logger.error(f"Approval creation failed: {e}")
            return None
    
    def process_approvals(self) -> Dict[str, int]:
        """Process all approved actions."""
        self.logger.info("Processing approvals...")
        
        stats = {
            'executed': 0,
            'errors': 0
        }
        
        # Import HITL manager
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent / 'hitl_workflow'))
            from hitl_manager import HITLManager
            
            manager = HITLManager(str(self.vault_path))
            executed = manager.process_approved()
            
            stats['executed'] = len(executed)
            
            for item in executed:
                self.logger.info(f"Executed: {item['request_id']} - {item['action']}")
                
        except Exception as e:
            self.logger.error(f"Approval processing failed: {e}")
            stats['errors'] += 1
        
        # Update dashboard
        self.update_dashboard()
        
        return stats
    
    def generate_daily_briefing(self) -> Optional[Path]:
        """Generate daily CEO briefing."""
        self.logger.info("Generating daily briefing...")
        
        try:
            date_str = datetime.now().strftime('%Y-%m-%d')
            briefing_path = self.briefings / f'{date_str}_Daily_Briefing.md'
            
            # Gather metrics
            needs_action_count = len(list(self.needs_action.glob('*.md')))
            in_progress_count = len(list(self.in_progress.glob('*.md')))
            pending_approval_count = len(list(self.pending_approval.glob('*.md')))
            done_count = len(list(self.done.glob('*.md')))
            
            content = f'''---
generated: {datetime.now().isoformat()}
date: {date_str}
type: daily_briefing
---

# Daily Briefing: {date_str}

## Executive Summary

Daily status report for AI Employee operations.

## Queue Status

| Queue | Count |
|-------|-------|
| Needs Action | {needs_action_count} |
| In Progress | {in_progress_count} |
| Pending Approval | {pending_approval_count} |
| Done (Total) | {done_count} |

## Today's Activity

{self._get_activity_summary()}

## Pending Approvals

{self._get_pending_approvals()}

## Alerts

{self._get_alerts()}

## Recommendations

{self._get_recommendations()}

---
*Generated by AI Employee Orchestrator*
'''
            
            briefing_path.write_text(content, encoding='utf-8')
            self.logger.info(f"Daily briefing created: {briefing_path}")
            
            return briefing_path
            
        except Exception as e:
            self.logger.error(f"Daily briefing failed: {e}")
            return None
    
    def _get_activity_summary(self) -> str:
        """Get today's activity summary."""
        # Read today's logs
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y-%m-%d")}.log'
        if log_file.exists():
            content = log_file.read_text()
            lines = content.split('\n')[-10:]  # Last 10 lines
            return '\n'.join([f"- {line}" for line in lines if line])
        return "- No activity recorded"
    
    def _get_pending_approvals(self) -> str:
        """Get pending approvals list."""
        approvals = list(self.pending_approval.glob('*.md'))
        if approvals:
            return '\n'.join([f"- {a.name}" for a in approvals])
        return "- No pending approvals"
    
    def _get_alerts(self) -> str:
        """Get alerts."""
        alerts = []
        
        # Check for old items
        needs_action = list(self.needs_action.glob('*.md'))
        if len(needs_action) > 10:
            alerts.append(f"- ⚠️ High queue volume: {len(needs_action)} items")
        
        # Check for expired approvals
        # (Would check expiration dates here)
        
        if not alerts:
            return "- No alerts"
        
        return '\n'.join(alerts)
    
    def _get_recommendations(self) -> str:
        """Get recommendations."""
        recommendations = []
        
        needs_action = list(self.needs_action.glob('*.md'))
        if len(needs_action) > 5:
            recommendations.append("- Process Needs_Action queue soon")
        
        pending = list(self.pending_approval.glob('*.md'))
        if pending:
            recommendations.append("- Review pending approvals")
        
        if not recommendations:
            return "- All systems operating normally"
        
        return '\n'.join([f"- {r}" for r in recommendations])
    
    def update_dashboard(self):
        """Update Dashboard.md."""
        self.logger.info("Updating dashboard...")
        
        try:
            # Count items
            needs_action_count = len(list(self.needs_action.glob('*.md')))
            in_progress_count = len(list(self.in_progress.glob('*.md')))
            pending_approval_count = len(list(self.pending_approval.glob('*.md')))
            approved_count = len(list(self.approved.glob('*.md')))
            
            content = f'''---
last_updated: {datetime.now().isoformat()}
---

# AI Employee Dashboard

## Quick Status

| Metric | Count |
|--------|-------|
| Needs Action | {needs_action_count} |
| In Progress | {in_progress_count} |
| Pending Approval | {pending_approval_count} |
| Approved (Ready) | {approved_count} |

## Recent Activity

See /Vault/Logs/ for detailed activity logs.

## Quick Links

- [Needs_Action](file:///{self.needs_action})
- [In_Progress](file:///{self.in_progress})
- [Pending_Approval](file:///{self.pending_approval})
- [Done](file:///{self.done})

---
*Auto-updated by Orchestrator*
'''
            
            self.dashboard.write_text(content, encoding='utf-8')
            
        except Exception as e:
            self.logger.error(f"Dashboard update failed: {e}")
    
    def run_daemon(self, interval: int = 60):
        """Run orchestrator as daemon."""
        self.logger.info(f"Starting daemon mode (interval: {interval}s)")
        
        try:
            while True:
                self.process_queue()
                self.process_approvals()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("Daemon stopped by user")
        except Exception as e:
            self.logger.error(f"Daemon error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('--vault', required=True, help='Path to Obsidian vault')
    parser.add_argument('--action', 
                       choices=['process-queue', 'process-approvals', 'daily-briefing',
                               'weekly-audit', 'check-watchers', 'update-dashboard'],
                       default='process-queue',
                       help='Action to perform')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--interval', type=int, default=60, help='Daemon interval')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    # Create orchestrator
    config = {
        'verbose': args.verbose,
        'dry_run': args.dry_run
    }
    orch = Orchestrator(args.vault, config)
    
    # Execute action
    if args.daemon:
        orch.run_daemon(args.interval)
    elif args.action == 'process-queue':
        stats = orch.process_queue()
        print(f"Processed: {stats['files_processed']} files, "
              f"{stats['plans_generated'] } plans, "
              f"{stats['approvals_created']} approvals")
    elif args.action == 'process-approvals':
        stats = orch.process_approvals()
        print(f"Executed: {stats['executed']} approvals")
    elif args.action == 'daily-briefing':
        briefing = orch.generate_daily_briefing()
        if briefing:
            print(f"Daily briefing created: {briefing}")
    elif args.action == 'update-dashboard':
        orch.update_dashboard()
        print("Dashboard updated")


if __name__ == '__main__':
    main()
