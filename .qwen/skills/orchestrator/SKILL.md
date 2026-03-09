---
name: orchestrator
description: |
  Master orchestrator for AI Employee. Coordinates watchers, plan generation,
  HITL workflow, and action execution. The central nervous system that ties
  all skills together into a cohesive autonomous agent.
---

# Orchestrator

Central coordination system for AI Employee operations.

## Architecture

The Orchestrator is the **master process** that:

1. **Monitors** all watcher outputs
2. **Triggers** Claude Code for reasoning
3. **Manages** HITL approval workflow
4. **Executes** approved actions via MCP servers
5. **Updates** Dashboard.md with status
6. **Logs** all activities for audit

## Components

```
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Watcher   │  │   Plan      │  │    HITL     │          │
│  │   Monitor   │  │  Generator  │  │   Manager   │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                  │
│         └────────────────┼────────────────┘                  │
│                          │                                   │
│                  ┌───────▼────────┐                          │
│                  │  Action        │                          │
│                  │  Executor      │                          │
│                  └───────┬────────┘                          │
│                          │                                   │
│                  ┌───────▼────────┐                          │
│                  │   Dashboard    │                          │
│                  │   Updater      │                          │
│                  └────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Start Orchestrator

```bash
# Start main orchestrator
python scripts/orchestrator.py --vault ./AI_Employee_Vault

# Start with specific action
python scripts/orchestrator.py --vault ./vault --action process-queue

# Start in daemon mode
python scripts/orchestrator.py --vault ./vault --daemon
```

### Command Line Options

```
--vault PATH       Path to Obsidian vault (required)
--action ACTION    Specific action to perform
--daemon           Run as background daemon
--interval SECS    Daemon check interval (default: 60)
--verbose          Enable debug logging
--dry-run          Simulate without executing actions
```

## Actions

### process-queue

Process all files in Needs_Action folder:

```bash
python scripts/orchestrator.py --vault ./vault --action process-queue
```

Workflow:
1. Read all files in `/Vault/Needs_Action/`
2. Generate plans using Plan Generator
3. Move files to `/Vault/In_Progress/`
4. Create approval requests for sensitive actions
5. Update Dashboard.md

### generate-plans

Generate plans without processing:

```bash
python scripts/orchestrator.py --vault ./vault --action generate-plans
```

### process-approvals

Process approved actions:

```bash
python scripts/orchestrator.py --vault ./vault --action process-approvals
```

Workflow:
1. Read all files in `/Vault/Approved/`
2. Execute actions via MCP servers
3. Log results
4. Move files to `/Vault/Done/`

### daily-briefing

Generate daily CEO briefing:

```bash
python scripts/orchestrator.py --vault ./vault --action daily-briefing
```

Output: `/Vault/Briefings/YYYY-MM-DD_Daily_Briefing.md`

### weekly-audit

Generate weekly business audit:

```bash
python scripts/orchestrator.py --vault ./vault --action weekly-audit
```

Output: `/Vault/Briefings/YYYY-MM-DD_Weekly_Audit.md`

### check-watchers

Health check on all watchers:

```bash
python scripts/orchestrator.py --vault ./vault --action check-watchers
```

## Daemon Mode

Run orchestrator as background service:

```bash
# Start daemon
python scripts/orchestrator.py --vault ./vault --daemon --interval 60

# Logs written to:
# /Vault/Logs/orchestrator.log
```

### Systemd Service (Linux)

```ini
# /etc/systemd/system/ai-employee-orchestrator.service
[Unit]
Description=AI Employee Orchestrator
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/Ai-employ
ExecStart=/usr/bin/python3 scripts/orchestrator.py --vault /path/to/vault --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Windows Service

Use NSSM or Task Scheduler:

```powershell
# Task Scheduler (runs on login)
schtasks /Create /TN "AI Employee\Orchestrator" /TR "python C:\path\to\orchestrator.py --vault C:\path\to\vault --daemon" /SC ONLOGON /RL HIGHEST
```

## Integration Points

### Watcher Integration

```python
# Orchestrator monitors watcher outputs
class Orchestrator:
    def check_watchers(self):
        """Check all watcher outputs."""
        watchers = {
            'gmail': self.vault_path / 'Needs_Action',
            'whatsapp': self.vault_path / 'Needs_Action',
            'filesystem': self.vault_path / 'Needs_Action'
        }
        
        for watcher, path in watchers.items():
            files = list(path.glob('*.md'))
            if files:
                self.logger.info(f"{watcher}: {len(files)} new items")
```

### Plan Generator Integration

```python
def generate_plans(self):
    """Generate plans for all action items."""
    from plan_generator import PlanGenerator
    
    generator = PlanGenerator(str(self.vault_path))
    plans = generator.process_all()
    
    self.logger.info(f"Generated {len(plans)} plans")
    return plans
```

### HITL Integration

```python
def process_approvals(self):
    """Process approved actions."""
    from hitl_manager import HITLManager
    
    manager = HITLManager(str(self.vault_path))
    executed = manager.process_approved()
    
    for item in executed:
        self.execute_action(item)
```

### MCP Server Integration

```python
def execute_action(self, action):
    """Execute approved action via MCP."""
    action_type = action['action']
    
    if action_type == 'send_email':
        result = self.call_email_mcp(action)
    elif action_type == 'social_post':
        result = self.call_linkedin_mcp(action)
    elif action_type == 'payment':
        result = self.call_payment_mcp(action)
    
    self.log_action(action, result)
```

## Dashboard Updates

Orchestrator maintains Dashboard.md:

```python
def update_dashboard(self):
    """Update Dashboard.md with current status."""
    dashboard_path = self.vault_path / 'Dashboard.md'
    
    # Count items in each folder
    needs_action = len(list((self.vault_path / 'Needs_Action').glob('*.md')))
    in_progress = len(list((self.vault_path / 'In_Progress').glob('*.md')))
    pending_approval = len(list((self.vault_path / 'Pending_Approval').glob('*.md')))
    done_today = self.count_done_today()
    
    # Generate dashboard content
    content = f'''---
last_updated: {datetime.now().isoformat()}
---

# AI Employee Dashboard

## Quick Status

| Metric | Count |
|--------|-------|
| Needs Action | {needs_action} |
| In Progress | {in_progress} |
| Pending Approval | {pending_approval} |
| Done Today | {done_today} |

## Recent Activity

{self.get_recent_activity()}

## Alerts

{self.get_alerts()}
'''
    
    dashboard_path.write_text(content)
```

## Logging

All orchestrator actions are logged:

```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action": "process_queue",
  "actor": "orchestrator",
  "details": {
    "files_processed": 5,
    "plans_generated": 5,
    "approvals_created": 2
  },
  "result": "success"
}
```

## Error Handling

```python
def safe_execute(self, func, *args, **kwargs):
    """Execute function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        self.logger.error(f"Error in {func.__name__}: {e}")
        self.log_error(func.__name__, str(e))
        return None
```

## Verification

Run: `python scripts/verify.py`

Expected: `✓ Orchestrator ready`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Watchers not triggered | Check watcher processes running |
| Plans not generated | Verify Company_Handbook.md exists |
| Approvals not processed | Check HITL manager integration |
| Dashboard not updating | Check file permissions |
| MCP calls failing | Verify MCP servers running |

## Best Practices

1. **Run as daemon** - Keep orchestrator running 24/7
2. **Log everything** - Full audit trail required
3. **Graceful degradation** - Continue if one component fails
4. **Health checks** - Monitor watcher health
5. **Rate limiting** - Don't overwhelm MCP servers
