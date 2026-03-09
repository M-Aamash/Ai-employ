---
name: hitl-workflow
description: |
  Human-in-the-Loop approval workflow for sensitive actions. Creates approval
  request files, waits for human decision, and triggers action execution only
  after explicit approval. Essential for payments, email sends, and social posts.
---

# Human-in-the-Loop (HITL) Workflow

Safe approval workflow for sensitive actions requiring human review before execution.

## Architecture

The HITL workflow uses a **file-based approval system**:

1. **Claude/Agent** creates approval request in `/Pending_Approval/`
2. **Human** reviews and moves file to `/Approved/` or `/Rejected/`
3. **Orchestrator** detects movement and executes/rejects action
4. **Result** logged to `/Vault/Logs/`

## Approval Categories

| Category | Auto-Approve | Always Require Approval |
|----------|--------------|------------------------|
| Email replies | Known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs, sensitive topics |
| File operations | Create, read | Delete, move outside vault |

## Approval Request Format

```markdown
---
type: approval_request
action: send_email
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
priority: high
request_id: APPROVAL_20260107_103000_001
---

# Approval Request: Send Email

## Action Details

**Action Type:** Send Email
**To:** john@example.com
**Subject:** January 2026 Invoice - $1,500
**Attachment:** /Vault/Invoices/2026-01_John_Doe.pdf

## Context

This email contains the January 2026 invoice for consulting services.
Client requested invoice via email on 2026-01-07.

## Email Body

Dear John,

Please find attached your invoice for January 2026.

Amount Due: $1,500.00
Due Date: 2026-01-21

Best regards,
AI Employee

## Risk Assessment

- **Recipient:** Known client (verified)
- **Content:** Standard invoice (low risk)
- **Attachment:** Verified invoice PDF
- **Compliance:** Follows Company Handbook guidelines

## To Approve

Move this file to: `/Vault/Approved/`

## To Reject

Move this file to: `/Vault/Rejected/`
Add comment explaining rejection reason.

## Expiration

This request expires: 2026-01-08T10:30:00Z
(24 hours from creation)

---
*Created by AI Employee - Approval System*
```

## Workflow Steps

### Step 1: Create Approval Request

When Claude detects a sensitive action:

```markdown
# Claude creates in /Pending_Approval/
APPROVAL_EMAIL_invoice_john_doe.md
```

### Step 2: Human Review

Human reviews the request:
- Check recipient is correct
- Verify content is appropriate
- Confirm attachment exists
- Review risk assessment

### Step 3: Decision

**To Approve:**
```bash
# Move file to Approved folder
mv /Vault/Pending_Approval/APPROVAL_*.md /Vault/Approved/
```

**To Reject:**
```bash
# Add rejection comment and move
echo "## Rejection Reason\nWrong amount - should be $1,200" >> file.md
mv /Vault/Pending_Approval/APPROVAL_*.md /Vault/Rejected/
```

### Step 4: Execution

Orchestrator detects file in `/Approved/`:
- Calls appropriate MCP server
- Executes the action
- Logs result

### Step 5: Completion

- Move related files to `/Done/`
- Update Dashboard.md
- Log to audit trail

## Approval Templates

### Email Send Approval

```markdown
---
type: approval_request
action: send_email
to: recipient@example.com
subject: Email Subject
created: 2026-01-07T10:30:00Z
status: pending
---

# Approval Request: Send Email

## Details
- **To:** {{to}}
- **Subject:** {{subject}}
- **Attachments:** {{attachments}}

## Body
{{email_body}}

## Risk Assessment
- Recipient verified: Yes/No
- Content appropriate: Yes/No
- Compliance check: Passed/Failed

---
Move to /Approved/ to send | Move to /Rejected/ to cancel
```

### Payment Approval

```markdown
---
type: approval_request
action: payment
amount: 500.00
currency: USD
recipient: Client Name
created: 2026-01-07T10:30:00Z
status: pending
---

# Approval Request: Payment

## Details
- **Amount:** $500.00 USD
- **Recipient:** Client Name
- **Bank:** XXXX1234
- **Reference:** Invoice #1234

## Reason
Payment for January 2026 services.

## Risk Assessment
- New payee: No
- Amount threshold: Within limits
- Documentation: Invoice attached

---
Move to /Approved/ to pay | Move to /Rejected/ to cancel
```

### Social Media Post Approval

```markdown
---
type: approval_request
action: social_post
platform: LinkedIn
created: 2026-01-07T10:30:00Z
status: pending
---

# Approval Request: LinkedIn Post

## Content

{{post_content}}

## Media
- Image: /path/to/image.jpg (if any)

## Schedule
- Post at: 2026-01-08T09:00:00Z

## Risk Assessment
- Brand alignment: Verified
- Sensitive content: None
- Compliance: Approved

---
Move to /Approved/ to post | Move to /Rejected/ to cancel
```

## Orchestrator Integration

```python
# Orchestrator watches Approved folder
class ApprovalOrchestrator:
    def __init__(self, vault_path):
        self.approved_path = Path(vault_path) / 'Approved'
        self.rejected_path = Path(vault_path) / 'Rejected'
    
    def process_approvals(self):
        """Process all approved requests."""
        for approval_file in self.approved_path.glob('*.md'):
            self.execute_approval(approval_file)
    
    def execute_approval(self, approval_file):
        """Execute approved action."""
        content = approval_file.read_text()
        metadata = parse_frontmatter(content)
        
        action = metadata.get('action')
        
        if action == 'send_email':
            execute_email_send(metadata)
        elif action == 'payment':
            execute_payment(metadata)
        elif action == 'social_post':
            execute_social_post(metadata)
        
        # Log and move to Done
        log_action(metadata, 'executed')
        move_to_done(approval_file)
```

## Security Rules

### Never Auto-Approve

1. Payments to new recipients
2. Emails to unknown contacts
3. Social media replies to strangers
4. Any action > $100
5. File deletions

### Always Log

1. Who approved (timestamp)
2. What was approved
3. Execution result
4. Any errors

### Expiration Policy

- High priority: 4 hours
- Medium priority: 24 hours
- Low priority: 7 days

Expired requests are moved to `/Rejected/` with note.

## Verification

Run: `python scripts/verify.py`

Expected: `✓ HITL Workflow ready`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approvals not detected | Check orchestrator is running |
| Actions not executing | Verify MCP server connection |
| Files not moving | Check file permissions |
| Expired requests | Review expiration policy |

## Best Practices

1. **Clear context** - Include all relevant information
2. **Risk assessment** - Always evaluate and document risks
3. **Expiration** - Set reasonable timeouts
4. **Audit trail** - Log every approval decision
5. **Human friendly** - Make review easy and clear
