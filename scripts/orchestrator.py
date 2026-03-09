"""
Orchestrator

Main orchestration script for the AI Employee system.
Watches the Needs_Action folder and triggers Claude Code to process items.
Manages the overall workflow and updates the Dashboard.

Usage:
    python orchestrator.py --vault ./AI_Employee_Vault
"""

import os
import sys
import time
import logging
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class OrchestratorHandler(FileSystemEventHandler):
    """
    Handles file system events in the Needs_Action folder.
    Triggers Claude Code processing when new files appear.
    """
    
    def __init__(self, vault_path: Path, orchestrator: 'Orchestrator'):
        super().__init__()
        self.vault_path = vault_path
        self.orchestrator = orchestrator
        self.logger = logging.getLogger('OrchestratorHandler')
        self.processing_lock = False  # Simple lock to prevent concurrent processing
        
    def on_created(self, event):
        """Handle new file creation."""
        if event.is_directory:
            return
            
        if not self.processing_lock:
            self.logger.info(f"New file detected: {event.src_path}")
            self.orchestrator.process_queue()


class Orchestrator:
    """
    Main orchestrator class that manages the AI Employee workflow.
    
    Responsibilities:
    - Watch Needs_Action folder for new items
    - Trigger Claude Code to process items
    - Update Dashboard.md with current status
    - Manage file movements between folders
    """
    
    def __init__(self, vault_path: str, claude_model: str = None):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault
            claude_model: Claude model to use (default: opus)
        """
        self.vault_path = Path(vault_path).resolve()
        self.claude_model = claude_model or 'opus'
        self.logger = logging.getLogger('Orchestrator')
        
        # Define folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Ensure all folders exist
        for folder in [self.needs_action, self.in_progress, self.done, 
                       self.plans, self.pending_approval, self.approved, 
                       self.rejected, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Observer for file watching
        self.observer = None
        self.handler = None
        
        # Processing state
        self.is_processing = False
        self.processed_files = set()
        
    def start_watching(self):
        """Start watching the Needs_Action folder."""
        self.logger.info(f"Starting orchestrator for vault: {self.vault_path}")
        
        self.handler = OrchestratorHandler(self.vault_path, self)
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.needs_action), recursive=False)
        self.observer.start()
        
        self.logger.info("Watching for new files in Needs_Action folder...")
        self.logger.info("Press Ctrl+C to stop")
        
        # Update dashboard
        self.update_dashboard_status()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the orchestrator."""
        self.logger.info("Stopping orchestrator...")
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.logger.info("Orchestrator stopped")
    
    def process_queue(self):
        """Process all files in the Needs_Action folder."""
        if self.is_processing:
            self.logger.debug("Already processing, skipping...")
            return
        
        self.is_processing = True
        
        try:
            # Get all markdown files in Needs_Action
            files_to_process = list(self.needs_action.glob('*.md'))
            
            if not files_to_process:
                self.logger.debug("No files to process")
                return
            
            self.logger.info(f"Found {len(files_to_process)} file(s) to process")
            
            # Process each file
            for file_path in files_to_process:
                if file_path.name in self.processed_files:
                    continue
                    
                self.process_file(file_path)
                self.processed_files.add(file_path.name)
            
            # Update dashboard after processing
            self.update_dashboard_status()
            
        except Exception as e:
            self.logger.error(f"Error processing queue: {e}", exc_info=True)
        finally:
            self.is_processing = False
    
    def process_file(self, file_path: Path):
        """
        Process a single file using Plan Generator.

        Args:
            file_path: Path to the file to process
        """
        self.logger.info(f"Processing file: {file_path.name}")

        try:
            # Move to In_Progress
            in_progress_path = self.in_progress / file_path.name
            shutil.move(str(file_path), str(in_progress_path))

            # Read the file content
            content = in_progress_path.read_text(encoding='utf-8')

            # Use Plan Generator instead of Claude Code
            self.logger.info("Generating plan...")
            plan_path = self._generate_plan(in_progress_path, content)

            # Process plan result
            if plan_path:
                self.logger.info(f"Plan created: {plan_path.name}")
                # Check if approval needed
                if self._needs_approval(content):
                    self._create_approval_request(in_progress_path, content)
            else:
                self.logger.warning("No plan generated")
                # Move back to Needs_Action on failure
                shutil.move(str(in_progress_path), str(file_path))

        except Exception as e:
            self.logger.error(f"Error processing file {file_path.name}: {e}", exc_info=True)
            # Move back to Needs_Action on error
            try:
                shutil.move(str(in_progress_path), str(file_path))
            except:
                pass
    
    def _generate_plan(self, file_path: Path, content: str) -> Path:
        """
        Generate a plan using Plan Generator.

        Args:
            file_path: Path to the action file
            content: Content of the action file

        Returns:
            Path to created plan file or None
        """
        try:
            # Import Plan Generator
            sys.path.insert(0, str(Path(__file__).parent.parent / '.qwen' / 'skills' / 'plan-generator' / 'scripts'))
            from plan_generator import PlanGenerator
            
            generator = PlanGenerator(str(self.vault_path))
            plan_path = generator.generate_plan(file_path)
            
            return plan_path
            
        except Exception as e:
            self.logger.error(f"Error generating plan: {e}")
            return None
    
    def _needs_approval(self, content: str) -> bool:
        """
        Check if action requires approval.

        Args:
            content: Content of the action file

        Returns:
            True if approval needed, False otherwise
        """
        # Check for sensitive actions
        sensitive_keywords = ['send', 'email', 'reply', 'post', 'payment', 'transfer']
        content_lower = content.lower()
        
        return any(keyword in content_lower for keyword in sensitive_keywords)
    
    def _create_approval_request(self, file_path: Path, content: str):
        """
        Create approval request for sensitive actions.

        Args:
            file_path: Path to the action file
            content: Content of the action file
        """
        try:
            # Import HITL Manager
            sys.path.insert(0, str(Path(__file__).parent.parent / '.qwen' / 'skills' / 'hitl-workflow' / 'scripts'))
            from hitl_manager import HITLManager
            
            manager = HITLManager(str(self.vault_path))
            
            # Parse basic info from content
            import re
            match = re.search(r'from:\s*(.+)', content, re.IGNORECASE)
            from_field = match.group(1).strip() if match else 'Unknown'
            
            match = re.search(r'subject:\s*(.+)', content, re.IGNORECASE)
            subject = match.group(1).strip() if match else 'Action Required'
            
            # Determine action type
            action_type = 'send_email' if 'email' in content.lower() else 'general'
            
            details = {
                'to': from_field,
                'subject': subject,
                'priority': 'medium'
            }
            
            approval_path = manager.create_approval_request(action_type, details, content)
            self.logger.info(f"Approval request created: {approval_path.name}")
            
        except Exception as e:
            self.logger.error(f"Error creating approval request: {e}")
    
    def update_dashboard_status(self):
        """Update the Dashboard.md with current status."""
        try:
            # Count files in each folder
            needs_action_count = len(list(self.needs_action.glob('*.md')))
            in_progress_count = len(list(self.in_progress.glob('*.md')))
            done_count = len(list(self.done.glob('*.md')))
            pending_approval_count = len(list(self.pending_approval.glob('*.md')))
            
            # Get recent activity
            recent_files = sorted(self.done.glob('*.md'), key=lambda f: f.stat().st_mtime, reverse=True)[:5]
            recent_activity = []
            for f in recent_files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                recent_activity.append(f"- [{mtime}] {f.name}")
            
            # Update dashboard
            if self.dashboard.exists():
                content = self.dashboard.read_text(encoding='utf-8')
                
                # Update counts
                content = self._update_section(content, 'Pending Actions', str(needs_action_count))
                content = self._update_section(content, 'In Progress', str(in_progress_count))
                content = self._update_section(content, 'Completed Today', str(done_count))
                content = self._update_section(content, 'Pending Approval', str(pending_approval_count))
                
                self.dashboard.write_text(content, encoding='utf-8')
                self.logger.info("Dashboard updated")
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")
    
    def _update_section(self, content: str, section_marker: str, new_value: str) -> str:
        """Update a specific section in the dashboard content."""
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            if section_marker in line and '|' in line:
                # This is a table row, update the value
                parts = line.split('|')
                if len(parts) >= 3:
                    parts[2] = f' {new_value} '
                    line = '|'.join(parts)
            new_lines.append(line)
        
        return '\n'.join(new_lines)


def main():
    """Main entry point for the Orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('--vault', type=str, default='../AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--model', type=str, default='opus',
                       choices=['opus', 'sonnet', 'haiku'],
                       help='Claude model to use')
    parser.add_argument('--once', action='store_true',
                       help='Process once and exit (don\'t watch continuously)')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault).resolve()
    
    if not vault_path.exists():
        print(f"Error: Vault not found at {vault_path}")
        sys.exit(1)
    
    orchestrator = Orchestrator(vault_path=str(vault_path), claude_model=args.model)
    
    if args.once:
        print("Processing queue once...")
        orchestrator.process_queue()
        print("Done!")
    else:
        orchestrator.start_watching()


if __name__ == '__main__':
    main()
