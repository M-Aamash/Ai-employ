#!/usr/bin/env python3
"""
Verify Plan Generator is ready.
"""

import sys
from pathlib import Path

def check_vault_structure():
    """Check if vault structure exists."""
    vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    required_dirs = ['Needs_Action', 'Plans', 'In_Progress', 'Pending_Approval', 'Done']
    
    missing = []
    for dir_name in required_dirs:
        if not (vault / dir_name).exists():
            missing.append(dir_name)
    
    if missing:
        return False, f"Missing directories: {', '.join(missing)}"
    return True, "Vault structure complete"

def check_context_files():
    """Check if context files exist."""
    vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    required_files = ['Company_Handbook.md', 'Business_Goals.md']
    
    missing = []
    for file_name in required_files:
        if not (vault / file_name).exists():
            missing.append(file_name)
    
    if missing:
        return False, f"Missing files: {', '.join(missing)}"
    return True, "Context files present"

def check_plan_generator():
    """Check if plan generator script exists."""
    script = Path(__file__).parent / 'plan_generator.py'
    if script.exists():
        return True, "Plan generator script found"
    return False, "Plan generator script not found"

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("   Plan Generator Verification")
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
    
    # Check 3: Plan generator script
    passed, msg = check_plan_generator()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    print("\n" + "=" * 60 + "\n")
    
    if all_passed:
        print("SUCCESS: Plan Generator is ready!")
        print("\nUsage:")
        print("  # Generate plans for all action items")
        print("  python .qwen/skills/plan-generator/scripts/plan_generator.py --vault ./AI_Employee_Vault --all")
        print("\n  # Then use Qwen Code to execute plans")
        print("  qwen --cd ./AI_Employee_Vault")
        print("  # \"Review and execute the plans in the Plans folder\"")
    else:
        print("INCOMPLETE: Please address the failed checks above.")
    
    print("\n" + "=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
