---
name: scheduler
description: |
  Task scheduling using cron (Linux/Mac) or Task Scheduler (Windows). Automate
  daily briefings, periodic watcher checks, and scheduled business audits.
  Use for recurring tasks like Monday Morning CEO Briefing and daily summaries.
---

# Scheduler Integration

Automated task scheduling for recurring AI Employee operations.

## Architecture

The Scheduler provides:
- **Cron jobs** (Linux/Mac) for scheduled task execution
- **Task Scheduler** (Windows) for native Windows scheduling
- **Python APScheduler** for cross-platform scheduling
- **Systemd timers** (Linux) for modern Linux systems

## Scheduling Modes

### Mode 1: Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add scheduled tasks (see examples below)
```

### Mode 2: Windows Task Scheduler

```powershell
# Create scheduled task via PowerShell
schtasks /Create /TN "AI Employee\Daily Briefing" /TR "python scripts\orchestrator.py --action daily-briefing" /SC DAILY /ST 08:00
```

### Mode 3: Python APScheduler (Cross-platform)

```python
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=8, minute=0)
def daily_briefing():
    generate_ceo_briefing()

scheduler.start()
```

## Scheduled Tasks

### Daily Briefing (8:00 AM)

Generates daily summary of tasks, emails, and business metrics.

**Cron:**
```bash
0 8 * * * cd /path/to/Ai-employ && python scripts/orchestrator.py --action daily-briefing >> logs/daily_briefing.log 2>&1
```

**Windows:**
```powershell
schtasks /Create /TN "AI Employee\Daily Briefing" /TR "python C:\path\to\scripts\orchestrator.py --action daily-briefing" /SC DAILY /ST 08:00 /RL HIGHEST
```

### Hourly Watcher Check

Processes Needs_Action folder every hour.

**Cron:**
```bash
0 * * * * cd /path/to/Ai-employ && python scripts/orchestrator.py --action process-queue >> logs/hourly_check.log 2>&1
```

### Weekly Business Audit (Sunday 10:00 PM)

Generates Monday Morning CEO Briefing.

**Cron:**
```bash
0 22 * * 0 cd /path/to/Ai-employ && python scripts/orchestrator.py --action weekly-audit >> logs/weekly_audit.log 2>&1
```

### Monthly Accounting Review (1st of month, 9:00 AM)

Reviews previous month's transactions and generates reports.

**Cron:**
```bash
0 9 1 * * cd /path/to/Ai-employ && python scripts/orchestrator.py --action monthly-review >> logs/monthly_review.log 2>&1
```

## Setup Scripts

### Linux/Mac: Setup Cron

```bash
#!/bin/bash
# setup_cron.sh

VAULT_PATH="/path/to/AI_Employee_Vault"
SCRIPTS_PATH="/path/to/scripts"

# Create log directory
mkdir -p logs

# Install cron if not present
which cron || sudo apt-get install cron

# Create crontab file
cat > /tmp/ai_employee_cron << EOF
# AI Employee Scheduled Tasks

# Daily Briefing at 8:00 AM
0 8 * * * cd $SCRIPTS_PATH && python orchestrator.py --action daily-briefing >> ../logs/daily_briefing.log 2>&1

# Hourly queue processing
0 * * * * cd $SCRIPTS_PATH && python orchestrator.py --action process-queue >> ../logs/hourly_check.log 2>&1

# Weekly audit on Sunday at 10:00 PM
0 22 * * 0 cd $SCRIPTS_PATH && python orchestrator.py --action weekly-audit >> ../logs/weekly_audit.log 2>&1

# Monthly review on 1st at 9:00 AM
0 9 1 * * cd $SCRIPTS_PATH && python orchestrator.py --action monthly-review >> ../logs/monthly_review.log 2>&1
EOF

# Install crontab
crontab /tmp/ai_employee_cron
rm /tmp/ai_employee_cron

echo "Cron jobs installed successfully"
crontab -l
```

### Windows: Setup Task Scheduler

```powershell
# setup_tasks.ps1

$VAULT_PATH = "C:\path\to\AI_Employee_Vault"
$SCRIPTS_PATH = "C:\path\to\scripts"
$PYTHON = "python"

# Create tasks
$tasks = @(
    @{
        Name = "AI Employee\Daily Briefing"
        Command = "$PYTHON $SCRIPTS_PATH\orchestrator.py --action daily-briefing"
        Schedule = "DAILY"
        Time = "08:00"
    },
    @{
        Name = "AI Employee\Hourly Check"
        Command = "$PYTHON $SCRIPTS_PATH\orchestrator.py --action process-queue"
        Schedule = "HOURLY"
    },
    @{
        Name = "AI Employee\Weekly Audit"
        Command = "$PYTHON $SCRIPTS_PATH\orchestrator.py --action weekly-audit"
        Schedule = "WEEKLY"
        Day = "SUNDAY"
        Time = "22:00"
    }
)

foreach ($task in $tasks) {
    $action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $($task.Command)"
    $trigger = New-ScheduledTaskTrigger -$(if ($task.Schedule -eq "HOURLY") { "Once" } else { $task.Schedule }) -At $task.Time
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    Register-ScheduledTask -TaskName $task.Name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
    
    Write-Host "Created task: $($task.Name)"
}
```

## Python APScheduler (Advanced)

For more complex scheduling needs:

```python
# scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=8, minute=0)
def daily_briefing():
    """Generate daily CEO briefing."""
    logger.info("Generating daily briefing...")
    from orchestrator import Orchestrator
    orch = Orchestrator('./AI_Employee_Vault')
    orch.generate_daily_briefing()

@scheduler.scheduled_job('cron', minute=0)
def hourly_check():
    """Process Needs_Action queue."""
    logger.info("Processing queue...")
    from orchestrator import Orchestrator
    orch = Orchestrator('./AI_Employee_Vault')
    orch.process_queue()

@scheduler.scheduled_job('cron', day_of_week='sun', hour=22, minute=0)
def weekly_audit():
    """Generate weekly business audit."""
    logger.info("Running weekly audit...")
    from orchestrator import Orchestrator
    orch = Orchestrator('./AI_Employee_Vault')
    orch.weekly_audit()

if __name__ == '__main__':
    logger.info("Starting scheduler...")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped")
```

### Run APScheduler

```bash
# Install
pip install apscheduler

# Run as daemon
nohup python scheduler.py > logs/scheduler.log 2>&1 &

# Or use systemd/service file for production
```

## Systemd Service (Linux Production)

For production deployment on Linux:

```ini
# /etc/systemd/system/ai-employee-scheduler.service
[Unit]
Description=AI Employee Scheduler
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/Ai-employ
ExecStart=/usr/bin/python3 scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable Service

```bash
# Copy service file
sudo cp ai-employee-scheduler.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable ai-employee-scheduler
sudo systemctl start ai-employee-scheduler

# Check status
sudo systemctl status ai-employee-scheduler

# View logs
journalctl -u ai-employee-scheduler -f
```

## Verification

Run: `python scripts/verify.py`

Expected: `✓ Scheduler ready`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cron job not running | Check cron daemon: `sudo service cron status` |
| Task not executing | Check logs: `tail -f logs/*.log` |
| Permission denied | Ensure script has execute permission |
| Python not found | Use absolute path to python binary |
| Environment variables missing | Source .env in cron script |

## Best Practices

1. **Log everything** - All scheduled tasks should log output
2. **Error handling** - Catch and log exceptions
3. **Notifications** - Alert on failures
4. **Overlap prevention** - Use lock files for long-running tasks
5. **Time zones** - Ensure server time is correct (UTC recommended)
