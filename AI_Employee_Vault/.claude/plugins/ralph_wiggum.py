#!/usr/bin/env python3
"""
Ralph Wiggum Stop Hook Plugin for Claude Code

This plugin intercepts Claude's attempt to exit and checks if the task is complete.
If the task file is not in /Done, it blocks the exit and re-injects the prompt.

Installation:
1. Copy this file to: AI_Employee_Vault/.claude/plugins/ralph_wiggum.py
2. Enable in Claude Code settings

Usage:
    /ralph-loop "Your task description here" --max-iterations 10
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RalphWiggum')


class RalphWiggumHook:
    """
    Stop hook that keeps Claude working until tasks are complete.
    
    Implements the "Ralph Wiggum" pattern - a persistent agent that
    continues working until the job is done.
    """
    
    def __init__(self, vault_path: str, max_iterations: int = 10):
        """
        Initialize the Ralph Wiggum hook.
        
        Args:
            vault_path: Path to the Obsidian vault
            max_iterations: Maximum number of iterations before giving up
        """
        self.vault_path = Path(vault_path).resolve()
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.task_description = ""
        self.completion_marker = "TASK_COMPLETE"
        
        # Folders to monitor
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        
        logger.info(f"Ralph Wiggum hook initialized for: {self.vault_path}")
        logger.info(f"Max iterations: {self.max_iterations}")
    
    def check_task_complete(self) -> Tuple[bool, str]:
        """
        Check if the current task is complete.
        
        Returns:
            Tuple of (is_complete, reason)
        """
        self.current_iteration += 1
        logger.info(f"Iteration {self.current_iteration}/{self.max_iterations}")
        
        # Check iteration limit
        if self.current_iteration > self.max_iterations:
            return True, f"Max iterations ({self.max_iterations}) reached"
        
        # Check if Needs_Action and In_Progress are empty
        needs_action_count = len(list(self.needs_action.glob('*.md')))
        in_progress_count = len(list(self.in_progress.glob('*.md')))
        
        if needs_action_count == 0 and in_progress_count == 0:
            return True, "All action files processed (moved to Done)"
        
        # Check for pending approvals (task blocked waiting for human)
        pending_count = len(list(self.pending_approval.glob('*.md')))
        if pending_count > 0:
            return False, f"Waiting for human approval: {pending_count} file(s) in Pending_Approval"
        
        # Task still in progress
        return False, f"Work in progress: {needs_action_count} in Needs_Action, {in_progress_count} in In_Progress"
    
    def should_allow_exit(self) -> Tuple[bool, str]:
        """
        Determine if Claude should be allowed to exit.
        
        Returns:
            Tuple of (allow_exit, message)
        """
        is_complete, reason = self.check_task_complete()
        
        if is_complete:
            logger.info(f"Task complete: {reason}")
            return True, reason
        else:
            logger.info(f"Task incomplete: {reason}")
            return False, reason
    
    def get_continuation_prompt(self, reason: str) -> str:
        """
        Generate a prompt to continue working.
        
        Args:
            reason: Reason why task is incomplete
            
        Returns:
            Prompt string to re-inject
        """
        return f"""
[Ralph Wiggum Hook] Task is not yet complete: {reason}

Please continue working on the task. Remember:
1. Process all files in /Needs_Action and /In_Progress
2. Move completed items to /Done
3. Create approval requests in /Pending_Approval when needed
4. Update the Dashboard.md with current status

Current iteration: {self.current_iteration}/{self.max_iterations}

Continue working until all action files are processed or you reach the iteration limit.
"""
    
    def on_exit_attempt(self, claude_output: str) -> dict:
        """
        Called when Claude attempts to exit.
        
        Args:
            claude_output: Claude's output before exiting
            
        Returns:
            dict with 'allow_exit' boolean and optional 'continue_prompt'
        """
        allow_exit, reason = self.should_allow_exit()
        
        if allow_exit:
            return {
                'allow_exit': True,
                'message': f"Task completed: {reason}"
            }
        else:
            return {
                'allow_exit': False,
                'continue_prompt': self.get_continuation_prompt(reason)
            }


def ralph_loop(task: str, vault_path: str = None, max_iterations: int = 10):
    """
    Start a Ralph Wiggum loop for autonomous task completion.
    
    Args:
        task: Task description
        vault_path: Path to Obsidian vault (default: current directory)
        max_iterations: Maximum iterations
    """
    if vault_path is None:
        vault_path = os.getcwd()
    
    hook = RalphWiggumHook(vault_path=vault_path, max_iterations=max_iterations)
    hook.task_description = task
    
    print(f"\n🔁 Ralph Wiggum Loop Started")
    print(f"Task: {task}")
    print(f"Vault: {vault_path}")
    print(f"Max iterations: {max_iterations}")
    print("-" * 50)
    
    # Create a state file to track the task
    state_file = Path(vault_path) / 'In_Progress' / f'RALPH_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(f"""---
type: ralph_loop
task: {task}
started: {datetime.now().isoformat()}
max_iterations: {max_iterations}
status: in_progress
---

# Ralph Wiggum Autonomous Task

## Task Description
{task}

## Iteration Log
- Iteration 1: Started

## Notes
_Add notes here as the task progresses_
""", encoding='utf-8')
    
    print(f"State file created: {state_file.name}")
    print("\nNow running Claude Code with Ralph Wiggum hook...")
    print("The agent will continue working until the task is complete.\n")
    
    return hook


def main():
    """CLI entry point for Ralph Wiggum hook."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ralph Wiggum Stop Hook for Claude Code')
    parser.add_argument('task', type=str, help='Task description')
    parser.add_argument('--vault', type=str, default=None, help='Path to Obsidian vault')
    parser.add_argument('--max-iterations', type=int, default=10, help='Maximum iterations')
    
    args = parser.parse_args()
    
    hook = ralph_loop(
        task=args.task,
        vault_path=args.vault,
        max_iterations=args.max_iterations
    )
    
    # The hook would integrate with Claude Code's plugin system
    # For now, we just set up the state file and print instructions
    print("To use with Claude Code:")
    print(f"1. Start Claude Code in the vault directory")
    print(f"2. Run your task")
    print(f"3. This hook will monitor for completion")


if __name__ == '__main__':
    main()
