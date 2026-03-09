# LinkedIn MCP Tools Reference

Complete reference for LinkedIn automation tools via Playwright MCP.

## Core Tools

### browser_navigate
Navigate to a URL.

**Parameters:**
- `url` (string): The URL to navigate to

**Example:**
```bash
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_navigate \
  -p '{"url": "https://www.linkedin.com"}'
```

### browser_snapshot
Get accessibility snapshot of current page (returns element refs).

**Parameters:** None

**Returns:** Element tree with refs for interaction

**Example:**
```bash
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_snapshot -p '{}'
```

### browser_click
Click an element by ref.

**Parameters:**
- `ref` (string): Element reference from snapshot
- `element` (string, optional): Element description for logging

**Example:**
```bash
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_click \
  -p '{"ref": "e42", "element": "Start a post button"}'
```

### browser_type
Type text into an element.

**Parameters:**
- `ref` (string): Element reference from snapshot
- `text` (string): Text to type
- `submit` (boolean, optional): Whether to submit after typing

**Example:**
```bash
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_type \
  -p '{"ref": "e15", "text": "Exciting business update!", "submit": false}'
```

### browser_fill_form
Fill multiple form fields at once.

**Parameters:**
- `fields` (array): List of {ref, value} objects

**Example:**
```bash
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_fill_form \
  -p '{"fields": [{"ref": "e10", "value": "Post title"}, {"ref": "e12", "value": "Post content"}]}'
```

### browser_take_screenshot
Take a screenshot of the current page.

**Parameters:**
- `type` (string, optional): Image type (png, jpeg)
- `fullPage` (boolean, optional): Capture full page or viewport only

**Example:**
```bash
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_take_screenshot \
  -p '{"type": "png", "fullPage": true}'
```

### browser_wait_for
Wait for a condition.

**Parameters:**
- `text` (string, optional): Wait for text to appear
- `time` (number, optional): Wait for specified milliseconds

**Example:**
```bash
# Wait for text
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_wait_for \
  -p '{"text": "Your post was published"}'

# Wait for time
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_wait_for \
  -p '{"time": 3000}'
```

### browser_evaluate
Execute JavaScript on the page.

**Parameters:**
- `function` (string): JavaScript function to execute

**Example:**
```bash
# Get page title
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_evaluate \
  -p '{"function": "return document.title"}'

# Extract post content
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_evaluate \
  -p '{"function": "return Array.from(document.querySelectorAll(\".feed-shared-update-v2__description\")).map(el => el.textContent)"}'
```

### browser_run_code
Run complex multi-step Playwright code.

**Parameters:**
- `code` (string): Async function receiving page object

**Example:**
```bash
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_run_code \
  -p '{"code": "async (page) => { await page.goto(\"https://www.linkedin.com/feed\"); await page.click(\"button[aria-label=\\\"Start a post\\\"]\"); await page.waitForSelector(\"div[role=\\\"textbox\\\"]\"); await page.fill(\"div[role=\\\"textbox\\\"]\", \"Hello LinkedIn!\"); await page.click(\"button:has-text(\\\"Post\\\")\"); return \"Post created\"; }"}'
```

### browser_close
Close the browser (clean shutdown).

**Parameters:** None

**Example:**
```bash
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_close -p '{}'
```

## Common LinkedIn Selectors

### Post Creation
- Start a post button: `button[aria-label="Start a post"]`
- Post textbox: `div[role="textbox"]`
- Post button: `button:has-text("Post")`
- Add media: `button[aria-label="Add media"]`

### Feed Navigation
- Feed home: `https://www.linkedin.com/feed`
- Notifications: `button[aria-label="Notifications"]`
- My posts: `a[href*="/in/your-profile/"]`

### Engagement
- Like button: `button[aria-label*="Like"]`
- Comment button: `button[aria-label*="Comment"]`
- Share button: `button[aria-label*="Share"]`

## Best Practices

1. **Always start with snapshot** - Get current element refs before interacting
2. **Wait for elements** - Use browser_wait_for after navigation
3. **Handle errors gracefully** - Check for element existence before clicking
4. **Respect rate limits** - Wait 5-10 seconds between actions
5. **Log all actions** - Create audit trail in /Vault/Logs/

## Security Considerations

- Never automate connection requests without HITL approval
- Always log actions to Dashboard.md
- Use dry-run mode for testing new workflows
- Respect LinkedIn Terms of Service
