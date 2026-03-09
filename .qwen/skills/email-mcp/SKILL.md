---
name: email-mcp
description: |
  Email sending via MCP server. Send, draft, and manage emails through Gmail API
  or SMTP. Integrates with HITL workflow for approval-based sending. Use for
  invoice delivery, client communication, and automated responses.
---

# Email MCP Integration

Email sending capabilities via Model Context Protocol (MCP) server.

## Architecture

The Email MCP provides:
- **Send emails** via Gmail API or SMTP
- **Draft emails** for review before sending
- **Search emails** for context and threading
- **Manage attachments** for invoices and documents

## Server Setup

### Option 1: Gmail API (Recommended)

```bash
# Install dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Setup credentials (see Gmail Watcher for details)
# Download credentials.json from Google Cloud Console
```

### Option 2: SMTP

```bash
# Install dependencies
pip install aiosmtplib email

# Configure SMTP settings in .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASS=your_password
```

## Usage

### Send Email (Direct)

```python
from email_mcp import EmailMCP

mcp = EmailMCP()
mcp.send_email(
    to='client@example.com',
    subject='Invoice #1234',
    body='Please find attached your invoice.',
    attachments=['/path/to/invoice.pdf']
)
```

### Create Draft (For Approval)

```python
draft_id = mcp.create_draft(
    to='client@example.com',
    subject='Invoice #1234',
    body='Please find attached your invoice.',
    attachments=['/path/to/invoice.pdf']
)
print(f"Draft created: {draft_id}")
```

### Search Emails

```python
results = mcp.search_emails('from:client@example.com is:unread')
for email in results:
    print(f"From: {email['from']}, Subject: {email['subject']}")
```

## MCP Server Mode

Start as MCP server for Claude Code integration:

```bash
# Start Email MCP server
python scripts/email_mcp_server.py --port 8810

# In Claude Code mcp.json:
{
  "servers": [
    {
      "name": "email",
      "command": "python",
      "args": ["scripts/email_mcp_server.py", "--port", "8810"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    }
  ]
}
```

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `email_send` | Send email directly | to, subject, body, attachments |
| `email_draft` | Create draft email | to, subject, body, attachments |
| `email_search` | Search emails | query, max_results |
| `email_read` | Read email by ID | message_id |
| `email_mark_read` | Mark email as read | message_id |

## Integration with HITL

Email MCP integrates with the HITL workflow:

1. **Claude creates plan** → Requires email send
2. **HITL creates approval** → `/Pending_Approval/EMAIL_*.md`
3. **Human approves** → Move to `/Approved/`
4. **Orchestrator calls** → Email MCP sends
5. **Result logged** → `/Vault/Logs/`

## Example: Invoice Email Flow

```python
# 1. Generate invoice PDF
invoice_path = generate_invoice(client_id, amount)

# 2. Create approval request
approval = hitl.create_approval_request(
    action_type='send_email',
    details={
        'to': 'client@example.com',
        'subject': f'Invoice #{invoice_number}',
        'body': email_body,
        'attachments': [invoice_path]
    }
)

# 3. Wait for approval (human moves file)
# File moves from Pending_Approval → Approved

# 4. Send email
result = email_mcp.send_email(
    to='client@example.com',
    subject=f'Invoice #{invoice_number}',
    body=email_body,
    attachments=[invoice_path]
)

# 5. Log and cleanup
log_action('email_sent', result)
move_to_done(approval)
```

## Email Templates

### Invoice Email

```markdown
Subject: Invoice #{invoice_number} - {company_name}

Dear {client_name},

Please find attached your invoice for {period}.

**Invoice Details:**
- Invoice Number: {invoice_number}
- Amount: ${amount}
- Due Date: {due_date}

Payment can be made via:
- Bank Transfer (details on invoice)
- Credit Card (link on invoice)

If you have any questions, please don't hesitate to contact us.

Best regards,
{your_name}
{company_name}
```

### Response Email

```markdown
Subject: Re: {original_subject}

Dear {sender_name},

Thank you for your email.

{response_body}

Best regards,
{your_name}
```

## Security Considerations

⚠️ **Important:**

1. **Always use HITL** for first-time recipients
2. **Verify attachments** before sending
3. **Log all sent emails** for audit trail
4. **Rate limit** sends to avoid spam flags
5. **Never auto-send** to unknown contacts

## Verification

Run: `python scripts/verify.py`

Expected: `✓ Email MCP ready`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-authorize Gmail API |
| Attachment not found | Check file path is absolute |
| Rate limited | Wait 60 seconds between sends |
| SMTP connection failed | Check SMTP settings in .env |
