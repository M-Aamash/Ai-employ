#!/usr/bin/env python3
"""
Verify Orchestrator is ready.
"""

import sys
from pathlib import Path

def check_vault_structure():
    """Check if vault structure exists."""
    vault = Path('AI_Employee_Vault')
    required_dirs = ['Needs_Action', 'In_Progress', 'Pending_Approval', 
                     'Approved', 'Rejected', 'Done', 'Plans', 'Logs', 'Briefings']
    
    missing = []
    for dir_name in required_dirs:
        if not (vault / dir_name).exists():
            missing.append(dir_name)
    
    if missing:
        return False, f"Missing directories: {', '.join(missing)}"
    return True, "Vault structure complete"

def check_context_files():
    """Check if context files exist."""
    vault = Path('AI_Employee_Vault')
    required_files = ['Dashboard.md', 'Company_Handbook.md', 'Business_Goals.md']
    
    missing = []
    for file_name in required_files:
        if not (vault / file_name).exists():
            missing.append(file_name)
    
    if missing:
        return False, f"Missing files: {', '.join(missing)}"
    return True, "Context files present"

def check_orchestrator_script():
    """Check if orchestrator script exists."""
    script = Path('scripts/orchestrator.py')
    if script.exists():
        return True, "Orchestrator script found"
    return False, "Orchestrator script not found"

def check_skills_available():
    """Check if required skills are available."""
    skills_path = Path('.qwen/skills')
    required_skills = ['plan-generator', 'hitl-workflow', 'gmail-watcher', 
                       'whatsapp-watcher', 'email-mcp']
    
    missing = []
    for skill in required_skills:
        if not (skills_path / skill).exists():
            missing.append(skill)
    
    if missing:
        return False, f"Missing skills: {', '.join(missing)}"
    return True, "All required skills available"

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("   Orchestrator Verification")
    print("=" * 60 + "\n")
    
    checks = []
    all_passed = True
    
    # Check 1: Vault structure
    passed, msg = check_vault_structure()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Check 2: Context files
    passed, msg = check_context_files()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Check 3: Orchestrator script
    passed, msg = check_orchestrator_script()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Check 4: Skills available
    passed, msg = check_skills_available()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    print("\n" + "=" * 60 + "\n")
    
    if all_passed:
        print("SUCCESS: Orchestrator is ready!")
        print("\nUsage:")
        print("  # Process queue")
        print("  python scripts/orchestrator.py --vault ./AI_Employee_Vault --action process-queue")
        print("\n  # Process approvals")
        print("  python scripts/orchestrator.py --vault ./AI_Employee_Vault --action process-approvals")
        print("\n  # Generate daily briefing")
        print("  python scripts/orchestrator.py --vault ./AI_Employee_Vault --action daily-briefing")
        print("\n  # Run as daemon")
        print("  python scripts/orchestrator.py --vault ./AI_Employee_Vault --daemon --interval 60")
        print("\nSilver Tier Skills Summary:")
        print("  ✓ LinkedIn MCP - Post business content")
        print("  ✓ WhatsApp Watcher - Monitor messages")
        print("  ✓ Gmail Watcher - Monitor emails")
        print("  ✓ Plan Generator - Create action plans")
        print("  ✓ HITL Workflow - Approval management")
        print("  ✓ Email MCP - Send emails")
        print("  ✓ Scheduler - Task scheduling")
        print("  ✓ Orchestrator - Central coordination")
    else:
        print("INCOMPLETE: Please address the failed checks above.")
    
    print("\n" + "=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
