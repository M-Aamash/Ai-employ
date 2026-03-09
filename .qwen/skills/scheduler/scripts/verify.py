#!/usr/bin/env python3
"""
Verify Scheduler is ready.
"""

import sys
from pathlib import Path

def check_apscheduler():
    """Check if APScheduler is installed."""
    try:
        import apscheduler
        return True, f"APScheduler installed (v{apscheduler.__version__})"
    except ImportError:
        return False, "APScheduler not installed"

def check_scheduler_script():
    """Check if scheduler script exists."""
    script = Path('scripts/scheduler.py')
    if script.exists():
        return True, "Scheduler script found"
    return False, "Scheduler script not found"

def check_cron_available():
    """Check if cron is available (Unix-like systems)."""
    import platform
    if platform.system() in ['Linux', 'Darwin']:
        import subprocess
        try:
            result = subprocess.run(['which', 'crontab'], capture_output=True)
            if result.returncode == 0:
                return True, "Cron available"
        except:
            pass
        return False, "Cron not available"
    return False, "Not Unix-like system"

def check_task_scheduler_windows():
    """Check if Task Scheduler is available (Windows)."""
    import platform
    if platform.system() == 'Windows':
        import subprocess
        try:
            result = subprocess.run(['schtasks'], capture_output=True)
            if result.returncode == 0:
                return True, "Task Scheduler available"
        except:
            pass
        return False, "Task Scheduler not available"
    return False, "Not Windows system"

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("   Scheduler Verification")
    print("=" * 60 + "\n")
    
    checks = []
    all_passed = True
    
    # Check 1: APScheduler
    passed, msg = check_apscheduler()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Check 2: Scheduler script
    passed, msg = check_scheduler_script()
    symbol = "✓" if passed else "✗"
    print(f"{symbol} {msg}")
    checks.append(passed)
    all_passed &= passed
    
    # Check 3: Platform-specific scheduler
    import platform
    if platform.system() in ['Linux', 'Darwin']:
        passed, msg = check_cron_available()
        symbol = "✓" if passed else "○"
        print(f"{symbol} {msg} (optional - can use APScheduler)")
    elif platform.system() == 'Windows':
        passed, msg = check_task_scheduler_windows()
        symbol = "✓" if passed else "○"
        print(f"{symbol} {msg} (optional - can use APScheduler)")
    
    print("\n" + "=" * 60 + "\n")
    
    if all_passed:
        print("SUCCESS: Scheduler is ready!")
        print("\nUsage:")
        print("  # Start scheduler (all jobs enabled)")
        print("  python scripts/scheduler.py --vault ./AI_Employee_Vault")
        print("\n  # Disable specific jobs")
        print("  python scripts/scheduler.py --vault ./vault --no-daily --no-weekly")
        print("\nSetup Options:")
        print("  1. APScheduler: Cross-platform Python scheduler (recommended)")
        print("  2. Cron: Linux/Mac system scheduler")
        print("  3. Task Scheduler: Windows system scheduler")
    else:
        print("INCOMPLETE: Please address the failed checks above.")
        print("\nTo install APScheduler:")
        print("  pip install apscheduler")
    
    print("\n" + "=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
