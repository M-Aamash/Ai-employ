#!/usr/bin/env python3
"""
Silver Tier Verification Script

Verifies that all Silver Tier deliverables are complete for the AI Employee Hackathon.
Uses Qwen Code as the brain instead of Claude Code.

Silver Tier Requirements:
1. All Bronze requirements (complete)
2. Two or more Watcher scripts (Gmail + LinkedIn)
3. Automatically Post on LinkedIn about business
4. Qwen Code reasoning loop that creates Plan.md files
5. One working MCP server for external action
6. Human-in-the-loop approval workflow
7. Basic scheduling via cron or Task Scheduler
8. All AI functionality implemented as Agent Skills

Usage:
    python verify_silver_tier.py
"""

import sys
from pathlib import Path
from typing import List, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def check_file(path: Path, description: str) -> Tuple[bool, str]:
    """Check if a file exists and return status."""
    if path.exists():
        if path.is_file():
            return True, f"OK: {description}"
        elif path.is_dir():
            return True, f"OK: {description} (directory)"
    return False, f"MISSING: {description}"


def check_file_content(path: Path, required_sections: List[str], description: str) -> Tuple[bool, str]:
    """Check if a file exists and contains required sections."""
    if not path.exists():
        return False, f"MISSING: {description}"

    content = path.read_text(encoding='utf-8')
    missing = []

    for section in required_sections:
        if section.lower() not in content.lower():
            missing.append(section)

    if missing:
        return False, f"INCOMPLETE: {description} - Missing: {', '.join(missing)}"

    return True, f"OK: {description}"


def verify_silver_tier(base_path: Path) -> bool:
    """
    Verify all Silver Tier requirements.

    Returns True if all requirements are met.
    """
    print("\n" + "=" * 70)
    print("   Silver Tier Verification - AI Employee Hackathon")
    print("   Brain: Qwen Code (instead of Claude Code)")
    print("=" * 70 + "\n")

    checks = []
    all_passed = True

    # =====================================================================
    # Requirement 1: Bronze Tier (Prerequisites)
    # =====================================================================
    print("1. Bronze Tier Prerequisites")
    print("-" * 70)

    vault_path = base_path / 'AI_Employee_Vault'
    passed, msg = check_file(vault_path, "AI_Employee_Vault directory")
    print(f"  {msg}")
    checks.append(passed)
    all_passed &= passed

    # Required markdown files
    required_files = [
        ('Dashboard.md', ['Quick Status', 'Inbox', 'Needs Action']),
        ('Company_Handbook.md', ['Rules', 'Email', 'Financial', 'Payment']),
        ('Business_Goals.md', ['Objectives', 'Metrics', 'Revenue']),
    ]

    for filename, sections in required_files:
        filepath = vault_path / filename
        passed, msg = check_file_content(filepath, sections, filename)
        print(f"  {msg}")
        checks.append(passed)
        all_passed &= passed

    # Required folders
    required_folders = [
        'Inbox', 'Needs_Action', 'Done', 'Plans', 'Pending_Approval',
        'Approved', 'Rejected', 'Logs', 'Accounting', 'Briefings', 'In_Progress'
    ]

    print("\n  Required Folders:")
    for folder in required_folders:
        folder_path = vault_path / folder
        passed, msg = check_file(folder_path, folder)
        print(f"    {msg}")
        checks.append(passed)
        all_passed &= passed

    # =====================================================================
    # Requirement 2: Two or More Watcher Scripts
    # =====================================================================
    print("\n2. Watcher Scripts (Gmail + LinkedIn)")
    print("-" * 70)

    skills_path = base_path / '.qwen' / 'skills'

    # Gmail Watcher
    gmail_watcher = skills_path / 'gmail-watcher'
    passed, msg = check_file(gmail_watcher, "Gmail Watcher skill")
    print(f"  {msg}")
    checks.append(passed)
    all_passed &= passed

    if gmail_watcher.exists():
        gmail_script = gmail_watcher / 'scripts' / 'gmail_watcher.py'
        passed, msg = check_file_content(gmail_script, ['GmailWatcher', 'check_for_updates', 'create_action_file'], "gmail_watcher.py")
        print(f"  {msg}")
        checks.append(passed)
        all_passed &= passed

    # LinkedIn Watcher
    linkedin_watcher = skills_path / 'linkedin-watcher'
    passed, msg = check_file(linkedin_watcher, "LinkedIn Watcher skill")
    print(f"  {msg}")
    checks.append(passed)
    all_passed &= passed

    if linkedin_watcher.exists():
        linkedin_script = linkedin_watcher / 'scripts' / 'linkedin_watcher.py'
        passed, msg = check_file_content(linkedin_script, ['LinkedInWatcher', 'post_content', 'check_for_updates'], "linkedin_watcher.py")
        print(f"  {msg}")
        checks.append(passed)
        all_passed &= passed

    # =====================================================================
    # Requirement 3: LinkedIn Auto-Posting
    # =====================================================================
    print("\n3. LinkedIn Auto-Posting for Business")
    print("-" * 70)

    content_dir = linkedin_watcher / 'content' if linkedin_watcher.exists() else Path()
    if content_dir.exists():
        posts = list(content_dir.glob('*.txt'))
        passed, msg = (True, f"OK: {len(posts)} business post templates") if posts else (False, "MISSING: Business post templates")
        print(f"  {msg}")
        checks.append(passed)
        all_passed &= passed

    # =====================================================================
    # Requirement 4: Plan Generator (Qwen Code Reasoning Loop)
    # =====================================================================
    print("\n4. Plan Generator (Qwen Code Reasoning)")
    print("-" * 70)

    plan_generator = skills_path / 'plan-generator'
    passed, msg = check_file(plan_generator, "Plan Generator skill")
    print(f"  {msg}")
    checks.append(passed)
    all_passed &= passed

    if plan_generator.exists():
        plan_script = plan_generator / 'scripts' / 'plan_generator.py'
        passed, msg = check_file_content(plan_script, ['PlanGenerator', 'generate_plan', 'process_all'], "plan_generator.py")
        print(f"  {msg}")
        checks.append(passed)
        all_passed &= passed

    # =====================================================================
    # Requirement 5: MCP Server for External Action
    # =====================================================================
    print("\n5. MCP Server (Email)")
    print("-" * 70)

    email_mcp = skills_path / 'email-mcp'
    passed, msg = check_file(email_mcp, "Email MCP skill")
    print(f"  {msg}")
    checks.append(passed)
    all_passed &= passed

    # =====================================================================
    # Requirement 6: Human-in-the-Loop Approval Workflow
    # =====================================================================
    print("\n6. HITL Approval Workflow")
    print("-" * 70)

    hitl = skills_path / 'hitl-workflow'
    passed, msg = check_file(hitl, "HITL Workflow skill")
    print(f"  {msg}")
    checks.append(passed)
    all_passed &= passed

    if hitl.exists():
        hitl_script = hitl / 'scripts' / 'hitl_manager.py'
        passed, msg = check_file_content(hitl_script, ['HITLManager', 'create_approval_request', 'process_approved'], "hitl_manager.py")
        print(f"  {msg}")
        checks.append(passed)
        all_passed &= passed

    # =====================================================================
    # Requirement 7: Basic Scheduling
    # =====================================================================
    print("\n7. Scheduler (Cron/Task Scheduler)")
    print("-" * 70)

    scheduler = skills_path / 'scheduler'
    passed, msg = check_file(scheduler, "Scheduler skill")
    print(f"  {msg}")
    checks.append(passed)
    all_passed &= passed

    if scheduler.exists():
        scheduler_script = scheduler / 'scripts' / 'scheduler.py'
        passed, msg = check_file_content(scheduler_script, ['AIScheduler', 'daily_briefing', 'weekly_audit'], "scheduler.py")
        print(f"  {msg}")
        checks.append(passed)
        all_passed &= passed

    # =====================================================================
    # Requirement 8: Orchestrator
    # =====================================================================
    print("\n8. Orchestrator (Coordination)")
    print("-" * 70)

    orchestrator = skills_path / 'orchestrator'
    passed, msg = check_file(orchestrator, "Orchestrator skill")
    print(f"  {msg}")
    checks.append(passed)
    all_passed &= passed

    if orchestrator.exists():
        orch_script = orchestrator / 'scripts' / 'orchestrator.py'
        passed, msg = check_file_content(orch_script, ['Orchestrator', 'process_queue', 'process_approvals'], "orchestrator.py")
        print(f"  {msg}")
        checks.append(passed)
        all_passed &= passed

    # =====================================================================
    # Additional: Credentials Check
    # =====================================================================
    print("\n9. Credentials Configuration")
    print("-" * 70)

    # Check for credentials.json in project root
    creds = base_path / 'credentials.json'
    passed, msg = check_file(creds, "credentials.json (Gmail API)")
    print(f"  {msg}")
    checks.append(passed)
    if not passed:
        print(f"    ⚠ Place your Gmail API credentials.json in project root")
    all_passed &= passed

    # =====================================================================
    # Summary
    # =====================================================================
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    total = len(checks)
    passed = sum(checks)
    failed = total - passed

    print(f"  Total Checks: {total}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.RESET}")
    if failed > 0:
        print(f"  {Colors.RED}Failed: {failed}{Colors.RESET}")

    print("=" * 70 + "\n")

    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}SUCCESS: Silver Tier Complete!{Colors.RESET}\n")
        print("All Silver Tier deliverables are present:")
        print("  - Gmail Watcher - Monitor emails")
        print("  - LinkedIn Watcher - Auto-post business content")
        print("  - Plan Generator - Qwen Code reasoning loop")
        print("  - Email MCP - Send emails")
        print("  - HITL Workflow - Approval management")
        print("  - Scheduler - Task automation")
        print("  - Orchestrator - Central coordination")
        print("\nNext Steps:")
        print("  1. Place credentials.json in project root (if not done)")
        print("  2. Authorize Gmail API:")
        print("     python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --authorize")
        print("  3. Login to LinkedIn (first time):")
        print("     python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault --visible")
        print("  4. Start the system:")
        print("     python .qwen/skills/orchestrator/scripts/orchestrator.py --vault ./AI_Employee_Vault --daemon")
        print("  5. Use Qwen Code:")
        print("     qwen --cd ./AI_Employee_Vault")
        print()
    else:
        print(f"{Colors.RED}{Colors.BOLD}INCOMPLETE: Silver Tier Incomplete{Colors.RESET}")
        print("\nPlease address the failed checks above.\n")

    return all_passed


def main():
    """Main entry point."""
    # Determine base path (project root)
    base_path = Path(__file__).parent.resolve()

    # Run verification
    success = verify_silver_tier(base_path)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
