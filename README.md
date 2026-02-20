# AI Employee - Bronze Tier

> **Your Personal AI Employee - Local-First Autonomous Agent**

A Personal AI Employee (Digital FTE) that proactively manages your communications and tasks using Claude Code as the reasoning engine and Obsidian as the dashboard.

---

## 🏆 Bronze Tier Deliverables

✅ **Completed:**
- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] One working Watcher script (Gmail)
- [x] Claude Code integration for reading/writing to vault
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [x] All AI functionality implemented as Agent Skills

---

## 📁 Project Structure

```
Ai-employ/
├── AI_Employee_Vault/          # Obsidian vault (Brain/Memory)
│   ├── Dashboard.md            # Real-time status dashboard
│   ├── Company_Handbook.md     # Rules of engagement
│   ├── Business_Goals.md       # Objectives and metrics
│   ├── Inbox/                  # Incoming items
│   ├── Needs_Action/           # Items requiring processing
│   ├── In_Progress/            # Currently being processed
│   ├── Done/                   # Completed items
│   ├── Plans/                  # Action plans
│   ├── Pending_Approval/       # Awaiting human decision
│   ├── Approved/               # Approved actions
│   ├── Rejected/               # Rejected actions
│   ├── Logs/                   # Audit logs
│   ├── Accounting/             # Financial records
│   ├── Briefings/              # CEO briefings
│   └── .claude/plugins/        # Claude plugins
│       └── ralph_wiggum.py     # Persistence hook
├── scripts/                    # Python watcher scripts
│   ├── base_watcher.py         # Base watcher class
│   ├── gmail_watcher.py        # Gmail monitor
│   └── orchestrator.py         # Main orchestrator
├── credentials/                # API credentials (gitignored)
├── .env.example               # Environment template
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://python.org) | 3.13+ | Watcher scripts |
| [Node.js](https://nodejs.org) | v24+ LTS | Claude Code |
| [Claude Code](https://claude.com/claude-code) | Latest | AI reasoning engine |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Dashboard/GUI |

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd Ai-employ

# Create Python virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install watchdog

# For Gmail watcher (optional):
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Step 3: Configure Environment

```bash
# Copy environment template
copy .env.example .env

# Edit .env with your settings
notepad .env
```

### Step 4: Set Up Gmail API (Optional)

If using Gmail watcher:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to `credentials/` folder
6. Rename to `gmail_credentials.json`

```bash
# Authenticate Gmail watcher
python scripts/gmail_watcher.py --auth
```

### Step 5: Verify Claude Code

```bash
# Check Claude Code installation
claude --version

# Test Claude Code
claude "Hello, test"
```

### Step 6: Open Obsidian Vault

1. Open Obsidian
2. Click "Open folder as vault"
3. Select `AI_Employee_Vault/` folder
4. Review `Dashboard.md`, `Company_Handbook.md`, `Business_Goals.md`

---

## 📖 Usage

### Start Gmail Watcher

```bash
# Run Gmail watcher (checks every 2 minutes)
python scripts/gmail_watcher.py --vault ./AI_Employee_Vault
```

### Start Orchestrator

```bash
# Run orchestrator (watches Needs_Action folder)
python scripts/orchestrator.py --vault ./AI_Employee_Vault
```

### Manual Claude Code Processing

```bash
# Navigate to vault directory
cd AI_Employee_Vault

# Start Claude Code
claude

# Process Needs_Action folder manually
claude "Process all files in Needs_Action folder and move completed items to Done"
```

### Using Ralph Wiggum Loop

```bash
# Start autonomous task processing
python AI_Employee_Vault/.claude/plugins/ralph_wiggum.py "Process all pending tasks" --vault ./AI_Employee_Vault
```

---

## 🔄 Workflow

### 1. **Perception** (Watcher Scripts)
- Gmail watcher monitors for new unread emails
- Creates action files in `/Needs_Action/` folder
- Each file contains email metadata and content

### 2. **Reasoning** (Claude Code)
- Orchestrator detects new files in `/Needs_Action/`
- Triggers Claude Code to process the file
- Claude reads `Company_Handbook.md` for rules
- Claude creates plan in `/Plans/` folder

### 3. **Action** (Human-in-the-Loop)
- For routine tasks: Claude completes automatically
- For sensitive actions: Claude creates file in `/Pending_Approval/`
- Human reviews and moves to `/Approved/` or `/Rejected/`
- Orchestrator executes approved actions

### 4. **Completion**
- Move processed files to `/Done/`
- Update `Dashboard.md`
- Log actions to `/Logs/`

---

## 📋 Folder Reference

| Folder | Purpose |
|--------|---------|
| `/Inbox` | Raw incoming items |
| `/Needs_Action` | Items requiring AI processing |
| `/In_Progress` | Currently being processed |
| `/Done` | Completed items |
| `/Plans` | Step-by-step action plans |
| `/Pending_Approval` | Awaiting human decision |
| `/Approved` | Approved for execution |
| `/Rejected` | Rejected actions |
| `/Logs` | Audit trail |
| `/Accounting` | Financial records |
| `/Briefings` | CEO briefings |

---

## 🔧 Configuration

### Gmail Watcher Options

```bash
# Custom check interval (300 seconds = 5 minutes)
python scripts/gmail_watcher.py --interval 300

# Custom credentials path
python scripts/gmail_watcher.py --credentials /path/to/credentials.json

# Process once and exit
python scripts/orchestrator.py --once
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VAULT_PATH` | `./AI_Employee_Vault` | Path to Obsidian vault |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `WATCHER_CHECK_INTERVAL` | `120` | Seconds between checks |
| `CLAUDE_MODEL` | `opus` | Claude model to use |
| `DRY_RUN` | `false` | Prevent real actions |

---

## 🛡️ Security

### Credential Management

- ✅ Never commit `.env` file
- ✅ Store credentials in `credentials/` folder (gitignored)
- ✅ Use environment variables
- ✅ Rotate credentials monthly

### Human-in-the-Loop

The system requires human approval for:
- Payments over $100
- New payees
- Bulk emails
- External communications to new contacts

### Audit Logging

All actions are logged to `/Logs/YYYY-MM-DD.md` with:
- Timestamp
- Action type
- Parameters
- Approval status
- Result

---

## 🧪 Testing

### Verify Setup

```bash
# Test Gmail watcher (dry run)
python scripts/gmail_watcher.py --vault ./AI_Employee_Vault --interval 10

# Test orchestrator (single pass)
python scripts/orchestrator.py --vault ./AI_Employee_Vault --once

# Test Claude Code integration
cd AI_Employee_Vault && claude "Update Dashboard.md with test status"
```

### Create Test Email

1. Manually create a test file in `/Needs_Action/`:

```markdown
---
type: email
from: test@example.com
subject: Test Email
received: 2026-02-19T00:00:00Z
priority: normal
status: unread
---

# Test Email

This is a test email for processing.

## Suggested Actions
- [ ] Process this test email
- [ ] Move to Done when complete
```

2. Run orchestrator:
```bash
python scripts/orchestrator.py --vault ./AI_Employee_Vault --once
```

3. Verify file moved to `/Done/`

---

## 🐛 Troubleshooting

### Gmail Watcher Issues

**Problem:** `ModuleNotFoundError: No module named 'google'`

**Solution:**
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**Problem:** `Credentials file not found`

**Solution:**
1. Download credentials from Google Cloud Console
2. Save to `credentials/gmail_credentials.json`
3. Run authentication: `python scripts/gmail_watcher.py --auth`

### Claude Code Issues

**Problem:** `claude: command not found`

**Solution:**
```bash
npm install -g @anthropic/claude-code
```

**Problem:** Claude Code can't write to vault

**Solution:**
- Check file permissions
- Ensure vault folder exists
- Run from vault directory

### Orchestrator Issues

**Problem:** No files being processed

**Solution:**
- Check `Needs_Action/` folder has `.md` files
- Verify vault path is correct
- Check logs for errors

---

## 📚 Next Steps (Silver Tier)

To upgrade to Silver Tier, add:

1. **Additional Watchers**
   - WhatsApp watcher (Playwright-based)
   - File system watcher

2. **MCP Server Integration**
   - Email MCP for sending emails
   - Browser MCP for web automation

3. **Scheduling**
   - Set up cron jobs (Mac/Linux) or Task Scheduler (Windows)
   - Daily briefing generation

4. **Enhanced Claude Reasoning**
   - Plan.md creation for complex tasks
   - Multi-step task orchestration

---

## 📄 License

This project is for educational purposes as part of the Personal AI Employee Hackathon.

---

## 🤝 Contributing

This is a hackathon project. Feel free to:
- Fork and customize for your needs
- Report issues
- Share improvements

---

## 📞 Support

- Hackathon Meetings: Wednesdays 10:00 PM on Zoom
- Documentation: See `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- Community: Join the hackathon Zoom meetings for help

---

*Built with ❤️ for the Personal AI Employee Hackathon 2026*
