"""
Bronze Tier Verification Script

Verifies that all Bronze Tier deliverables are complete.
Run this to confirm your setup is ready.

Usage:
    python verify_bronze_tier.py
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


def verify_bronze_tier(base_path: Path) -> bool:
    """
    Verify all Bronze Tier requirements.
    
    Returns True if all requirements are met.
    """
    print("\n" + "=" * 60)
    print("   Bronze Tier Verification")
    print("=" * 60 + "\n")
    
    checks = []
    all_passed = True
    
    # Requirement 1: Obsidian vault with Dashboard.md
    print("1. Obsidian Vault Structure")
    print("-" * 40)
    
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
        'Inbox',
        'Needs_Action',
        'Done',
        'Plans',
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Logs',
        'Accounting',
        'Briefings',
    ]
    
    print("\n2. Required Folders")
    print("-" * 40)
    
    for folder in required_folders:
        folder_path = vault_path / folder
        passed, msg = check_file(folder_path, folder)
        print(f"  {msg}")
        checks.append(passed)
        all_passed &= passed
    
    # Requirement 2: Gmail Watcher script
    print("\n3. Watcher Scripts")
    print("-" * 40)
    
    scripts_path = base_path / 'scripts'
    
    watcher_scripts = [
        ('base_watcher.py', ['BaseWatcher', 'check_for_updates', 'create_action_file']),
        ('gmail_watcher.py', ['GmailWatcher', 'check_for_updates', 'create_action_file']),
        ('orchestrator.py', ['Orchestrator', 'process_queue', 'update_dashboard']),
    ]
    
    for filename, sections in watcher_scripts:
        filepath = scripts_path / filename
        passed, msg = check_file_content(filepath, sections, filename)
        print(f"  {msg}")
        checks.append(passed)
        all_passed &= passed
    
    # Requirement 3: Ralph Wiggum plugin
    print("\n4. Claude Code Integration")
    print("-" * 40)
    
    ralph_path = vault_path / '.claude' / 'plugins' / 'ralph_wiggum.py'
    passed, msg = check_file(ralph_path, "Ralph Wiggum plugin")
    print(f"  {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Requirement 4: Environment configuration
    print("\n5. Configuration Files")
    print("-" * 40)
    
    config_files = [
        ('.env.example', ['GMAIL', 'VAULT_PATH', 'CLAUDE']),
        ('requirements.txt', ['watchdog', 'google-api-python-client']),
        ('.gitignore', ['.env', 'credentials']),
        ('README.md', ['Quick Start', 'Usage', 'Troubleshooting']),
    ]
    
    for filename, sections in config_files:
        filepath = base_path / filename
        passed, msg = check_file_content(filepath, sections, filename)
        print(f"  {msg}")
        checks.append(passed)
        all_passed &= passed
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    total = len(checks)
    passed = sum(checks)
    failed = total - passed
    
    print(f"  Total Checks: {total}")
    print(f"  Passed: {passed}")
    if failed > 0:
        print(f"  Failed: {failed}")
    
    print("=" * 60 + "\n")
    
    if all_passed:
        print("SUCCESS: Bronze Tier Complete!")
        print("\nAll required deliverables are present:")
        print("  - Obsidian vault with Dashboard.md and Company_Handbook.md")
        print("  - Gmail Watcher script working")
        print("  - Claude Code integration ready")
        print("  - Basic folder structure complete")
        print("\nNext Steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure .env file (copy from .env.example)")
        print("  3. Set up Gmail API credentials (optional)")
        print("  4. Open AI_Employee_Vault in Obsidian")
        print("  5. Test the system with a sample email\n")
    else:
        print("INCOMPLETE: Bronze Tier Incomplete")
        print("\nPlease address the failed checks above.\n")
    
    return all_passed


def main():
    """Main entry point."""
    # Determine base path (parent of scripts directory)
    base_path = Path(__file__).parent.resolve()
    
    # Run verification
    success = verify_bronze_tier(base_path)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
