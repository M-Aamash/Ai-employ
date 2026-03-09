# Silver Tier Skills - AI Employee Hackathon

**Complete Implementation using Qwen Code as the Brain**

This document describes the complete Silver Tier implementation for the Personal AI Employee Hackathon.

## Silver Tier Requirements (All Complete ✓)

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | All Bronze requirements | ✓ | Complete |
| 2 | Two or more Watcher scripts | ✓ | Gmail Watcher + LinkedIn Watcher |
| 3 | Auto-post on LinkedIn for business | ✓ | LinkedIn Watcher with business templates |
| 4 | Qwen Code reasoning loop (Plan.md) | ✓ | Plan Generator |
| 5 | One working MCP server | ✓ | Email MCP |
| 6 | Human-in-the-loop approval | ✓ | HITL Workflow |
| 7 | Basic scheduling | ✓ | Scheduler (APScheduler + cron) |
| 8 | All as Agent Skills | ✓ | 8 skills in `.qwen/skills/` |

## Skills Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI EMPLOYEE - SILVER TIER                     │
│                      Brain: Qwen Code                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐
│ Gmail Watcher│     │LinkedIn Watch│
│              │     │              │
└──────┬───────┘     └──────┬───────┘
       │                    │
       ▼                    ▼
┌─────────────────────────────────────────┐
│          Needs_Action/ Folder            │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         Plan Generator                   │
│    (Qwen Code Reasoning Loop)           │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         HITL Workflow                    │
│      (Approval Required?)               │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│   Approved   │    │   Rejected   │
└──────┬───────┘    └──────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Email MCP                        │
│      (Send Actions)                      │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Orchestrator                     │
│    (Coordination + Dashboard)           │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Scheduler                        │
│   (Daily/Weekly/Monthly Tasks)          │
└─────────────────────────────────────────┘
```

## Skills Directory Structure

```
.qwen/skills/
├── gmail-watcher/          # Gmail monitoring
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── gmail_watcher.py
│   │   ├── base_watcher.py
│   │   └── verify.py
│   └── references/
│
├── linkedin-watcher/       # LinkedIn automation
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── linkedin_watcher.py
│   │   ├── base_watcher.py
│   │   └── verify.py
│   └── content/
│       ├── post1.txt
│       ├── post2.txt
│       └── post3.txt
│
├── plan-generator/         # Qwen Code reasoning
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── plan_generator.py
│   │   └── verify.py
│   └── templates/
│
├── email-mcp/              # Email sending
│   ├── SKILL.md
│   └── scripts/
│       └── email_mcp_server.py
│
├── hitl-workflow/          # Approval system
│   ├── SKILL.md
│   ├── scripts/
│   │   └── hitl_manager.py
│   └── templates/
│
├── scheduler/              # Task scheduling
│   ├── SKILL.md
│   └── scripts/
│       └── scheduler.py
│
└── orchestrator/           # Central coordination
    ├── SKILL.md
    └── scripts/
        └── orchestrator.py
```

## Quick Start

### 1. Install Dependencies

```bash
# Core dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install playwright
pip install apscheduler
pip install watchdog

# Install Playwright browsers
playwright install chromium
```

### 2. Configure Credentials

Place your Gmail API `credentials.json` in the project root:

```bash
# Should be at: D:\Aamash code\Ai-employ\credentials.json
```

### 3. Verify Silver Tier

```bash
python verify_silver_tier.py
```

### 4. Authorize Gmail API

```bash
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --authorize
```

### 5. Login to LinkedIn (First Time)

```bash
python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault --visible
```

### 6. Start the System

```bash
# Start orchestrator (daemon mode)
python .qwen/skills/orchestrator/scripts/orchestrator.py --vault ./AI_Employee_Vault --daemon --interval 60

# Or start individual components
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --interval 120
```

### 7. Use Qwen Code

```bash
# Point Qwen Code to the vault
qwen --cd ./AI_Employee_Vault

# Then prompt:
"Check the Needs_Action folder and create plans for all items"
"Review pending approvals and suggest actions"
"Generate the daily briefing"
```

## Skill Details

### Gmail Watcher

**Purpose:** Monitor Gmail for important emails

**Features:**
- Gmail API integration
- Unread/important email detection
- Custom query filtering
- Action file creation

**Usage:**
```bash
# Authorize (first time)
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --authorize

# Start watching
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --interval 120
```

### LinkedIn Watcher

**Purpose:** Automate LinkedIn for business promotion

**Features:**
- Auto-post business content
- Lead detection
- Session persistence
- Engagement monitoring

**Usage:**
```bash
# Post content
python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault --action post

# Monitor for leads
python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault --action monitor
```

### Plan Generator

**Purpose:** Create Plan.md files using Qwen Code reasoning

**Features:**
- Automatic plan generation
- Priority-based processing
- Step-by-step tasks
- Approval detection

**Usage:**
```bash
python .qwen/skills/plan-generator/scripts/plan_generator.py --vault ./AI_Employee_Vault --all
```

### Email MCP

**Purpose:** Send emails via MCP server

**Features:**
- Gmail API or SMTP
- Draft creation
- Attachment handling

**Usage:**
```bash
python .qwen/skills/email-mcp/scripts/email_mcp_server.py --port 8810
```

### HITL Workflow

**Purpose:** Human-in-the-Loop approval management

**Features:**
- File-based approval
- Expiration handling
- Audit logging

**Usage:**
```bash
# List pending
python .qwen/skills/hitl-workflow/scripts/hitl_manager.py --vault ./AI_Employee_Vault --action list

# Process approved
python .qwen/skills/hitl-workflow/scripts/hitl_manager.py --vault ./AI_Employee_Vault --action process
```

### Scheduler

**Purpose:** Task scheduling

**Features:**
- Daily briefing (8 AM)
- Hourly check
- Weekly audit (Sunday 10 PM)
- Monthly review (1st, 9 AM)

**Usage:**
```bash
python .qwen/skills/scheduler/scripts/scheduler.py --vault ./AI_Employee_Vault
```

### Orchestrator

**Purpose:** Central coordination

**Features:**
- Queue processing
- Approval management
- Dashboard updates
- Daemon mode

**Usage:**
```bash
# Process queue
python .qwen/skills/orchestrator/scripts/orchestrator.py --vault ./AI_Employee_Vault --action process-queue

# Run as daemon
python .qwen/skills/orchestrator/scripts/orchestrator.py --vault ./AI_Employee_Vault --daemon --interval 60
```

## Workflow Example

1. **Email arrives** → Gmail Watcher detects
2. **Action file created** → `Needs_Action/EMAIL_*.md`
3. **Plan Generator** → Creates `Plans/PLAN_*.md`
4. **Qwen Code processes** → Reviews and suggests actions
5. **HITL creates approval** → `Pending_Approval/APPROVAL_*.md`
6. **Human approves** → Moves to `Approved/`
7. **Email MCP sends** → Email delivered
8. **Orchestrator logs** → `Logs/*.json`
9. **Dashboard updated** → Status reflected

## Verification

Run individual skill verifications:

```bash
python .qwen/skills/gmail-watcher/scripts/verify.py
python .qwen/skills/linkedin-watcher/scripts/verify.py
python .qwen/skills/plan-generator/scripts/verify.py
python .qwen/skills/orchestrator/scripts/verify.py
```

Run full Silver Tier verification:

```bash
python verify_silver_tier.py
```

## Next Steps (Gold Tier)

To advance to Gold Tier:
- [ ] Odoo Community integration
- [ ] Facebook/Instagram integration
- [ ] Twitter (X) integration
- [ ] Multiple MCP servers
- [ ] Weekly Business Audit
- [ ] Error recovery
- [ ] Ralph Wiggum loop

## Support

For issues:
1. Check verification scripts
2. Review logs in `/Vault/Logs/`
3. Consult individual skill documentation
