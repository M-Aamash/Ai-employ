#!/usr/bin/env python3
"""
Verify HITL Workflow is ready.
"""

import sys
from pathlib import Path

def check_vault_structure():
    """Check if vault structure exists."""
    vault = Path('AI_Employee_Vault')
    required_dirs = ['Pending_Approval', 'Approved', 'Rejected', 'Done', 'Logs']
    
    missing = []
    for dir_name in required_dirs:
        if not (vault / dir_name).exists():
            missing.append(dir_name)
    
    if missing:
        return False, f"Missing directories: {', '.join(missing)}"
    return True, "Vault structure complete"

def check_hitl_manager():
    """Check if HITL manager script exists."""
    script = Path('scripts/hitl_manager.py')
    if script.exists():
        return True, "HITL manager script found"
    return False, "HITL manager script not found"

def check_templates():
    """Check if approval templates exist."""
    templates_path = Path('templates')
    if templates_path.exists() and list(templates_path.glob('*.md')):
        return True, "Approval templates found"
    return False, "Approval templates not found"

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("   HITL Workflow Verification")
    print("=" * 60 + "\n")
    
    checks = []
    all_passed = True
    
    # Check 1: Vault structure
    passed, msg = check_vault_structure()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Check 2: HITL manager
    passed, msg = check_hitl_manager()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Check 3: Templates
    passed, msg = check_templates()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    print("\n" + "=" * 60 + "\n")
    
    if all_passed:
        print("SUCCESS: HITL Workflow is ready!")
        print("\nUsage:")
        print("  # List pending approvals")
        print("  python scripts/hitl_manager.py --vault ./AI_Employee_Vault --action list")
        print("\n  # Process approved requests")
        print("  python scripts/hitl_manager.py --vault ./AI_Employee_Vault --action process")
        print("\n  # Check for expired requests")
        print("  python scripts/hitl_manager.py --vault ./AI_Employee_Vault --action check-expiry")
    else:
        print("INCOMPLETE: Please address the failed checks above.")
    
    print("\n" + "=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
