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
        Process a single file using Claude Code.
        
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
            
            # Create prompt for Claude
            prompt = self._create_claude_prompt(content, in_progress_path.name)
            
            # Call Claude Code
            self.logger.info("Invoking Claude Code...")
            claude_response = self._call_claude_code(prompt)
            
            # Process Claude's response
            if claude_response:
                self._process_claude_response(claude_response, in_progress_path)
            else:
                self.logger.warning("No response from Claude Code")
                # Move back to Needs_Action on failure
                shutil.move(str(in_progress_path), str(file_path))
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path.name}: {e}", exc_info=True)
            # Move back to Needs_Action on error
            try:
                shutil.move(str(in_progress_path), str(file_path))
            except:
                pass
    
    def _create_claude_prompt(self, content: str, filename: str) -> str:
        """
        Create a prompt for Claude Code.
        
        Args:
            content: Content of the action file
            filename: Name of the file
            
        Returns:
            Prompt string for Claude
        """
        return f"""You are an AI Employee assistant. Process the following action file.

Action File: {filename}

{content}

---

Based on this action file, please:

1. **Understand**: What is being requested?
2. **Check**: Review the Company_Handbook.md and Business_Goals.md for relevant rules
3. **Plan**: Create a step-by-step plan in the Plans/ folder
4. **Act**: Execute what you can within your autonomy level
5. **Request Approval**: For actions requiring human approval, create a file in Pending_Approval/
6. **Log**: Record all actions in the Logs/ folder
7. **Update Dashboard**: Update Dashboard.md with the current status

Remember:
- Follow the Company Handbook rules for autonomy levels
- Always log your actions
- Request approval for sensitive actions (payments, external communications)
- Move completed items to Done/ when finished

Output your response in a structured format with clear sections."""
    
    def _call_claude_code(self, prompt: str) -> Optional[str]:
        """
        Call Claude Code with the given prompt.
        
        Args:
            prompt: The prompt to send to Claude
            
        Returns:
            Claude's response or None
        """
        try:
            # Build the Claude Code command
            cmd = [
                'claude',
                '--model', f'claude-3-5-{self.claude_model}-20241022',
                '--verbose',
                '--output-format', 'text'
            ]
            
            # Run Claude Code
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.vault_path)
            )
            
            stdout, stderr = process.communicate(prompt, timeout=300)
            
            if process.returncode != 0:
                self.logger.error(f"Claude Code error: {stderr}")
                return None
            
            return stdout
            
        except subprocess.TimeoutExpired:
            self.logger.error("Claude Code timed out after 5 minutes")
            return None
        except FileNotFoundError:
            self.logger.error("Claude Code not found. Please install: npm install -g @anthropic/claude-code")
            return None
        except Exception as e:
            self.logger.error(f"Error calling Claude Code: {e}")
            return None
    
    def _process_claude_response(self, response: str, in_progress_path: Path):
        """
        Process Claude's response and move files appropriately.
        
        Args:
            response: Claude's response text
            in_progress_path: Path to the file in In_Progress
        """
        # Log the response
        log_file = self.logs / f"claude_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        log_file.write_text(f"""---
timestamp: {datetime.now().isoformat()}
source: {in_progress_path.name}
---

# Claude Code Response

{response}
""", encoding='utf-8')
        
        self.logger.info(f"Logged response to {log_file.name}")
        
        # Move original file to Done
        done_path = self.done / in_progress_path.name
        shutil.move(str(in_progress_path), str(done_path))
        
        self.logger.info(f"Moved {in_progress_path.name} to Done/")
    
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
