---
type: approval_request
action: send_email
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
priority: high
request_id: APPROVAL_20260107_103000_EML
---

# Approval Request: Send Email

## Action Details

**To:** john@example.com
**Subject:** January 2026 Invoice - $1,500
**Attachments:** /Vault/Invoices/2026-01_John_Doe.pdf

## Context

Client requested invoice via email. Invoice has been generated and is ready to send.

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
- **Compliance:** Follows Company Handbook guidelines

## To Approve

Move this file to: `/Vault/Approved/`

## To Reject

Move this file to: `/Vault/Rejected/`
Add comment explaining rejection reason.

## Expiration

This request expires: 2026-01-08T10:30:00Z

---
*Created by AI Employee - Approval System*
