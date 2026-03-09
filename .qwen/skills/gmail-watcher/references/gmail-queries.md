# Gmail Search Queries Reference

Complete reference for Gmail search queries to filter and find emails.

## Basic Queries

### Unread Emails
```
is:unread
```

### Important Emails
```
is:important
```

### Starred Emails
```
is:starred
```

### From Specific Sender
```
from:john@example.com
from:@company.com
```

### To Specific Recipient
```
to:me
to:john@example.com
```

### Subject Contains
```
subject:invoice
subject:"urgent request"
```

### Body Contains
```
"payment received"
"project update"
```

## Combined Queries

### Unread + Important
```
is:unread is:important
```

### From Client + Unread
```
from:client@example.com is:unread
```

### Subject Invoice + Unread
```
subject:invoice is:unread
```

### Has Attachment + Unread
```
has:attachment is:unread
```

### Label Specific + Unread
```
label:work is:unread
label:clients is:unread
```

## Advanced Queries

### Date Range
```
after:2026/01/01 before:2026/01/31
newer_than:7d
older_than:30d
```

### Size Based
```
larger:10M
smaller:1M
```

### Multiple Senders
```
(from:john@example.com OR from:jane@example.com)
```

### Exclude Terms
```
-is:spam -subject:newsletter
```

### Category Based
```
category:primary
category:social
category:promotions
category:updates
category:forums
```

## Business Use Cases

### Lead Detection
```
subject:(pricing OR quote OR demo OR trial) is:unread
```

### Invoice Requests
```
(subject:invoice OR subject:payment OR subject:billing) is:unread
```

### Support Requests
```
(subject:help OR subject:support OR subject:issue) is:unread
```

### Partnership Inquiries
```
(subject:partnership OR subject:collaboration OR subject:opportunity) is:unread
```

### Urgent Messages
```
(urgent OR asap OR "time sensitive" OR emergency) is:unread
```

## Watcher Configuration Examples

### Example 1: High Priority Only
```python
query = 'is:unread is:important label:inbox'
interval = 60  # Check every minute
```

### Example 2: Client Emails
```python
query = 'from:@clientdomain.com is:unread'
interval = 120  # Check every 2 minutes
```

### Example 3: Invoice Related
```python
query = '(subject:invoice OR subject:payment) is:unread'
interval = 300  # Check every 5 minutes
```

### Example 4: All Business Emails
```python
query = '(-category:promotions -category:social) is:unread'
interval = 120  # Check every 2 minutes
```

## Gmail Labels

### Default Labels
- `INBOX` - Main inbox
- `SPAM` - Spam folder
- `TRASH` - Trash folder
- `SENT` - Sent emails
- `DRAFT` - Draft emails
- `STARRED` - Starred emails
- `IMPORTANT` - Important emails

### Custom Labels
Create custom labels in Gmail:
- `Clients`
- `Leads`
- `Invoices`
- `Projects`
- `Personal`

Use in queries:
```
label:clients is:unread
label:invoices newer_than:7d
```

## Testing Queries

Test your queries in Gmail search before using in watcher:

1. Open Gmail
2. Paste query in search box
3. Verify results match expectations
4. Adjust as needed

## Rate Limiting

Gmail API has quotas:
- 1,000,000 units/day
- Search: 1 unit per call
- Get message: 1 unit per call

Recommended intervals:
- Minimum: 60 seconds
- Recommended: 120-300 seconds
- Low priority: 600+ seconds

## Troubleshooting

### No Results
- Check query syntax
- Verify label names
- Test in Gmail web interface

### Too Many Results
- Add more specific filters
- Use date ranges
- Combine with is:important

### Query Not Working
- Check for typos
- Ensure proper escaping in code
- Verify Gmail API permissions
