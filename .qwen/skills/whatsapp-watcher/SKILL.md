---
name: whatsapp-watcher
description: |
  WhatsApp monitoring using Playwright. Watch for new messages, detect urgent keywords,
  and create action files in the Obsidian vault. Use for real-time communication monitoring
  and lead capture automation.
---

# WhatsApp Watcher

Monitor WhatsApp Web for new messages and create actionable items in your Obsidian vault.

## Architecture

The WhatsApp Watcher is a **Python Sentinel Script** that runs continuously in the background:

1. **Monitors** WhatsApp Web via Playwright automation
2. **Detects** messages containing urgent keywords
3. **Creates** .md action files in `/Vault/Needs_Action/`
4. **Triggers** Claude Code to process the messages

## Installation

### Prerequisites

```bash
# Install Playwright
pip install playwright

# Install browser
playwright install chromium
```

### Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Start Watcher

```bash
# Start the WhatsApp watcher
python scripts/whatsapp_watcher.py --vault /path/to/vault --interval 30
```

### Command Line Options

```
--vault PATH       Path to Obsidian vault (required)
--interval SECS    Check interval in seconds (default: 30)
--session PATH     Path to browser session storage (default: ~/.whatsapp_session)
--keywords LIST    Comma-separated keywords to watch (default: urgent,asap,invoice,payment,help)
--dry-run          Log actions without creating files
--verbose          Enable debug logging
```

### Example

```bash
python scripts/whatsapp_watcher.py \
  --vault "./AI_Employee_Vault" \
  --interval 30 \
  --keywords "urgent,asap,invoice,payment,help,pricing,buy,purchase" \
  --verbose
```

## Keyword Detection

The watcher monitors for these default keywords:

- `urgent` - Time-sensitive messages
- `asap` - Immediate attention needed
- `invoice` - Billing requests
- `payment` - Payment-related messages
- `help` - Support requests

Customize via `--keywords` flag or environment variable `WHATSAPP_KEYWORDS`.

## Action File Format

When a matching message is detected, the watcher creates:

```markdown
---
type: whatsapp
from: +1234567890
chat: John Doe
received: 2026-01-07T10:30:00Z
priority: high
status: pending
keywords: [urgent, invoice]
---

## Message Content

Hey, can you send me the invoice for January? This is urgent!

## Suggested Actions

- [ ] Reply to sender
- [ ] Generate invoice
- [ ] Send via email
- [ ] Mark as done

## Metadata

- Platform: WhatsApp Web
- Chat ID: 1234567890@c.us
- Message ID: ABC123XYZ
```

## Session Management

### First Run

On first run, you'll need to manually scan the QR code:

1. Script launches browser in visible mode
2. WhatsApp Web shows QR code
3. Scan with your phone
4. Session is saved to `~/.whatsapp_session`

### Subsequent Runs

Session persists - no QR code needed unless:
- You logout from WhatsApp Web
- Session file is deleted
- WhatsApp forces re-authentication

### Session Storage

```bash
# Default session location
~/.whatsapp_session/

# Custom location
python scripts/whatsapp_watcher.py --session /secure/path/session
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **Never commit session files** - Add to `.gitignore`
2. **Use dedicated device** - Consider using a separate phone number for business
3. **Respect ToS** - WhatsApp may restrict automated access
4. **Rate limiting** - Don't check more frequently than 30 seconds
5. **Human approval** - Always require HITL for sending messages

## Integration with Orchestrator

The watcher works with the main orchestrator:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  WhatsApp Web   │────▶│  WhatsApp Watcher │────▶│  Needs_Action/  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                              ┌──────────────────┐
                                              │   Claude Code    │
                                              │   (Processing)   │
                                              └──────────────────┘
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code shows every time | Session not saving - check write permissions |
| No messages detected | Increase interval, check keyword matching |
| Browser crashes | Update Playwright: `pip install -U playwright` |
| Rate limited | Increase check interval to 60+ seconds |
| WhatsApp Web changes | Update selectors in whatsapp_watcher.py |

## Verification

Run: `python scripts/verify.py`

Expected: `✓ WhatsApp Watcher ready`

## Files Structure

```
whatsapp-watcher/
├── SKILL.md              # This file
├── scripts/
│   ├── whatsapp_watcher.py    # Main watcher script
│   ├── base_watcher.py        # Base class for all watchers
│   ├── verify.py              # Verification script
│   └── mcp-client.py          # MCP tool caller
└── references/
    └── whatsapp-selectors.md  # WhatsApp Web CSS selectors
```

## Example Workflow

1. **Client sends message**: "Need pricing info ASAP"
2. **Watcher detects**: Keywords "ASAP" and "pricing"
3. **Creates file**: `/Vault/Needs_Action/WHATSAPP_john_doe_2026-01-07.md`
4. **Orchestrator triggers**: Claude Code processes the file
5. **Claude creates plan**: `/Vault/Plans/PLAN_pricing_response.md`
6. **Human approves**: Review suggested response
7. **Action executed**: Send pricing via WhatsApp/Email
8. **Logged**: Action recorded in `/Vault/Logs/`
