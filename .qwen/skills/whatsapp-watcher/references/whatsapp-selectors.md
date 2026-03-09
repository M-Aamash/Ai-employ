# WhatsApp Web Selectors Reference

CSS selectors and locators for WhatsApp Web automation.

**Note:** WhatsApp Web selectors may change over time. Update as needed.

## Core Selectors

### Chat List
```css
/* Main chat list container */
[data-testid="chat-list"]

/* Individual chat items */
[data-testid="chat-list"] > div

/* Unread chat indicator */
[aria-label*="unread"]

/* Chat item with contact name */
span[title*="contact-name"]
```

### Message Content
```css
/* Message preview text */
[aria-label*="unread"] span[dir="auto"]

/* Last message in chat */
[data-testid="chat-list"] span[dir="auto"]:last-child

/* Message timestamp */
[aria-label*="unread"] span[title]
```

### Navigation
```css
/* Menu button */
[data-testid="menu"]

/* Search input */
[data-testid="search"]

/* New chat button */
[data-testid="chat-list"] + div button
```

## Playwright Locator Examples

### Find Unread Chats
```python
# Get all unread chats
unread_chats = page.query_selector_all('[aria-label*="unread"]')

for chat in unread_chats:
    text = chat.inner_text()
    print(f"Unread: {text}")
```

### Extract Message Details
```python
# Get contact name
contact = chat.query_selector('span[title]')
contact_name = contact.get_attribute('title') if contact else 'Unknown'

# Get message preview
message = chat.query_selector('span[dir="auto"]')
message_text = message.inner_text() if message else ''

# Get timestamp
time_elem = chat.query_selector('span[title]')
timestamp = time_elem.get_attribute('title') if time_elem else ''
```

### Click on Chat
```python
# Click specific chat
chat.click()

# Wait for message panel to load
page.wait_for_selector('[data-testid="conversation"]')
```

### Send Message
```python
# Find message input
message_input = page.locator('[data-testid="compose-input"]')

# Type message
message_input.fill('Hello!')

# Send (press Enter)
page.keyboard.press('Enter')
```

## Common Patterns

### Pattern 1: Monitor All Unread
```python
def get_unread_messages(page):
    """Get all unread messages with details."""
    messages = []
    
    unread = page.query_selector_all('[aria-label*="unread"]')
    
    for chat in unread:
        text = chat.inner_text()
        lines = text.split('\n')
        
        messages.append({
            'contact': lines[0] if lines else 'Unknown',
            'preview': '\n'.join(lines[1:]) if len(lines) > 1 else '',
            'element': chat
        })
    
    return messages
```

### Pattern 2: Search by Keyword
```python
def find_keyword_messages(page, keywords):
    """Find chats containing specific keywords."""
    matches = []
    
    unread = page.query_selector_all('[aria-label*="unread"]')
    
    for chat in unread:
        text = chat.inner_text().lower()
        
        for keyword in keywords:
            if keyword.lower() in text:
                matches.append({
                    'chat': chat,
                    'keyword': keyword,
                    'text': text
                })
                break
    
    return matches
```

### Pattern 3: Reply to Chat
```python
def reply_to_chat(page, contact_name, reply_text):
    """Reply to a specific contact."""
    # Find and click chat
    chat = page.locator(f'[title="{contact_name}"]')
    chat.click()
    
    # Wait for input
    page.wait_for_selector('[data-testid="compose-input"]')
    
    # Type and send
    input_field = page.locator('[data-testid="compose-input"]')
    input_field.fill(reply_text)
    page.keyboard.press('Enter')
    
    # Wait for send confirmation
    page.wait_for_selector('[data-testid="msg-status"]')
```

## Troubleshooting

### Selector Not Found
If selectors stop working:
1. Open WhatsApp Web in browser
2. Open DevTools (F12)
3. Inspect the element
4. Find new `data-testid` or aria-label
5. Update selectors

### Session Lost
If session doesn't persist:
1. Check write permissions on session folder
2. Ensure browser closes properly
3. Re-scan QR code

### Rate Limiting
WhatsApp may rate limit:
1. Increase check interval (60+ seconds)
2. Reduce automation frequency
3. Use official WhatsApp Business API for production

## Security Notes

⚠️ **Important:**
- WhatsApp Web automation may violate Terms of Service
- Use at your own risk
- Consider official WhatsApp Business API for production
- Never automate spam or unsolicited messages
- Always get consent for automated messaging

## Alternative: WhatsApp Business API

For production use, consider:
- [WhatsApp Business Platform](https://developers.facebook.com/docs/whatsapp)
- Official API with proper rate limits
- Verified business account
- Better reliability and support
