# Email MCP - Complete Guide

## **Overview**

Email MCP allows your AI Employee to **send emails** via Gmail API with human approval (HITL).

---

## **Architecture**

```
Gmail Watcher → Needs_Action → Plan Generator → Pending_Approval → [YOU APPROVE] → Approved → Email MCP → Sent!
```

---

## **Setup**

### **1. Gmail Authentication (Already Done ✓)**

Your Gmail token is at:
```
AI_Employee_Vault/.gmail/.gmail_token.pkl
```

### **2. Start Email MCP Server**

```bash
python .qwen/skills/email-mcp/scripts/email_mcp_server.py --port 8810
```

**Keep this running in background** - it's the bridge between AI Employee and Gmail.

---

## **Complete Email Flow**

### **Step 1: Gmail Watcher Detects Email**

```bash
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --interval 120
```

**Creates:** `Needs_Action/EMAIL_john_doe_*.md`

---

### **Step 2: Plan Generator Creates Plan**

```bash
python .qwen/skills/plan-generator/scripts/plan_generator.py --vault ./AI_Employee_Vault --all
```

**Creates:** `Plans/PLAN_email_response_*.md`

Plan includes:
- ✓ Objective
- ✓ Steps with checkboxes
- ✓ Approval requirement flag

---

### **Step 3: Create Approval Request**

For emails requiring approval (sending, payments):

```bash
python .qwen/skills/hitl-workflow/scripts/hitl_manager.py --vault ./AI_Employee_Vault --action process
```

**Creates:** `Pending_Approval/APPROVAL_EMAIL_john_doe_*.md`

**Approval file contains:**
```markdown
---
type: approval_request
action: send_email
to: john@example.com
subject: Invoice #1234
created: 2026-03-06T12:00:00
status: pending
---

# Approval Request: Send Email

## Action Details
- **To:** john@example.com
- **Subject:** Invoice #1234
- **Body:** [Email content]

## To Approve
Move this file to: /Vault/Approved/

## To Reject
Move this file to: /Vault/Rejected/
```

---

### **Step 4: Human Approval (YOU)**

**Review the approval file:**
```bash
type AI_Employee_Vault\Pending_Approval\APPROVAL_EMAIL_*.md
```

**To Approve:**
```bash
move AI_Employee_Vault\Pending_Approval\APPROVAL_EMAIL_*.md AI_Employee_Vault\Approved\
```

**To Reject:**
```bash
move AI_Employee_Vault\Pending_Approval\APPROVAL_EMAIL_*.md AI_Employee_Vault\Rejected\
```

---

### **Step 5: Send Approved Emails**

```bash
python .qwen/skills/email-mcp/scripts/send_approved_emails.py
```

**What it does:**
1. ✓ Reads all files in `Approved/` folder
2. ✓ Extracts email details (to, subject, body)
3. ✓ Sends via Gmail API
4. ✓ Moves to `Done/` folder
5. ✓ Logs to `Logs/` folder

---

## **Quick Commands**

### **Start All Services:**

```bash
# Terminal 1: Gmail Watcher
start python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --interval 120

# Terminal 2: Email MCP Server
start python .qwen/skills/email-mcp/scripts/email_mcp_server.py --port 8810

# Terminal 3: Process Approvals (run every few minutes)
python .qwen/skills/hitl-workflow/scripts/hitl_manager.py --vault ./AI_Employee_Vault --action process
```

---

### **Check Status:**

```bash
# List pending approvals
python .qwen/skills/hitl-workflow/scripts/hitl_manager.py --vault ./AI_Employee_Vault --action list

# Check Approved folder
dir AI_Employee_Vault\Approved

# Check logs
type AI_Employee_Vault\Logs\*.json
```

---

## **Example: Complete Flow**

### **1. Email Arrives:**
```
From: client@example.com
Subject: Need invoice
```

### **2. Gmail Watcher Creates:**
```
Needs_Action/EMAIL_client_20260306120000.md
```

### **3. Plan Generator Creates:**
```
Plans/PLAN_email_response_20260306120100.md
```

Plan says:
- ✓ Action: Send invoice
- ✓ Requires approval: YES

### **4. HITL Creates:**
```
Pending_Approval/APPROVAL_EMAIL_20260306120200.md
```

### **5. You Approve:**
```bash
move AI_Employee_Vault\Pending_Approval\APPROVAL_EMAIL_*.md AI_Employee_Vault\Approved\
```

### **6. Send Email:**
```bash
python .qwen/skills/email-mcp/scripts/send_approved_emails.py
```

**Output:**
```
======================================================================
   Processing Approved Emails
======================================================================

Found 1 approved email(s)

Processing: APPROVAL_EMAIL_20260306120200.md
  ✓ Sent to: client@example.com
  ✓ Message ID: 18f3c2a1b5d6e7f8

======================================================================
   Sent: 1 | Failed: 0
======================================================================
```

### **7. Result:**
- ✓ Email sent to client
- ✓ File moved to `Done/`
- ✓ Logged in `Logs/`

---

## **Email MCP Server API**

### **Start Server:**
```bash
python .qwen/skills/email-mcp/scripts/email_mcp_server.py --port 8810
```

### **Send Email (HTTP API):**

```bash
curl -X POST http://localhost:8810 \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "email_send",
    "params": {
      "to": "client@example.com",
      "subject": "Invoice #1234",
      "body": "Please find attached your invoice."
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "message_id": "18f3c2a1b5d6e7f8",
  "thread_id": "18f3c2a1b5d6e7f9"
}
```

---

## **Security Features**

| Feature | Description |
|---------|-------------|
| **HITL Approval** | All emails require human approval before sending |
| **Token Storage** | Gmail token encrypted in `.gmail` folder |
| **Audit Logging** | All actions logged to `Logs/` folder |
| **Expiration** | Approval requests expire after 24 hours |
| **Rejection Trail** | Rejected emails moved to `Rejected/` with reason |

---

## **Troubleshooting**

### **Gmail Service Not Initialized:**
```
ERROR: Gmail service not initialized
```

**Solution:**
```bash
python authenticate_gmail.py
```

### **No Approved Emails:**
```
No approved emails to send.
```

**Solution:**
1. Check `Pending_Approval/` folder
2. Move files to `Approved/` folder
3. Run send script again

### **Email Send Failed:**
```
Error sending email: ...
```

**Check:**
1. Gmail token is valid
2. Internet connection
3. Gmail API quota not exceeded

---

## **Files Structure**

```
.qwen/skills/email-mcp/
├── SKILL.md
├── scripts/
│   ├── email_mcp_server.py      # MCP server
│   ├── send_approved_emails.py  # Send approved emails
│   └── verify.py                # Verification script
└── references/
    └── email-tools.md           # API reference
```

---

## **Next Steps**

1. **Start Email MCP Server:**
   ```bash
   python .qwen/skills/email-mcp/scripts/email_mcp_server.py --port 8810
   ```

2. **Process Pending Approvals:**
   ```bash
   python .qwen/skills/hitl-workflow/scripts/hitl_manager.py --vault ./AI_Employee_Vault --action list
   ```

3. **Send Approved Emails:**
   ```bash
   python .qwen/skills/email-mcp/scripts/send_approved_emails.py
   ```

---

**Your AI Employee can now send emails with human approval!** 🚀
