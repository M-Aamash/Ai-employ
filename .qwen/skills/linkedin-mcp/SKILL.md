---
name: linkedin-mcp
description: |
  LinkedIn automation using Playwright MCP. Post business updates, share content,
  engage with posts, and monitor LinkedIn activity. Use for business promotion,
  lead generation, and professional networking automation.
---

# LinkedIn MCP Integration

Automate LinkedIn activities via Playwright MCP server for business promotion and lead generation.

## Server Lifecycle

### Start Server
```bash
# Using helper script (recommended)
bash scripts/start-server.sh

# Or manually
npx @playwright/mcp@latest --port 8809 --shared-browser-context &
```

### Stop Server
```bash
# Using helper script (closes browser first)
bash scripts/stop-server.sh

# Or manually
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_close -p '{}'
pkill -f "@playwright/mcp"
```

### When to Stop
- **End of task**: Stop when LinkedIn work is complete
- **Long sessions**: Keep running if doing multiple LinkedIn tasks
- **Errors**: Stop and restart if browser becomes unresponsive

**Important:** The `--shared-browser-context` flag is required to maintain LinkedIn session state across multiple calls.

## Quick Reference

### Navigation

```bash
# Go to LinkedIn
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_navigate \
  -p '{"url": "https://www.linkedin.com"}'

# Go to LinkedIn feed
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_navigate \
  -p '{"url": "https://www.linkedin.com/feed"}'

# Go to LinkedIn post creation
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_navigate \
  -p '{"url": "https://www.linkedin.com/feed/update/urn:li:share:create"}'
```

### Get Page State

```bash
# Accessibility snapshot (returns element refs for clicking/typing)
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_snapshot -p '{}'

# Screenshot
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_take_screenshot \
  -p '{"type": "png", "fullPage": true}'
```

### Post Content

```bash
# Create a text post
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_run_code \
  -p '{"code": "async (page) => { await page.goto(\"https://www.linkedin.com/feed\"); await page.click(\"button[aria-label=\\\"Start a post\\\"]\"); await page.waitForSelector(\"div[role=\\\"textbox\\\"]\"); await page.fill(\"div[role=\\\"textbox\\\"]\", \"Your post content here\"); await page.click(\"button:has-text(\\\"Post\\\")\"); return \"Post created successfully\"; }"}'

# Create a post with media
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_run_code \
  -p '{"code": "async (page) => { await page.goto(\"https://www.linkedin.com/feed\"); await page.click(\"button[aria-label=\\\"Start a post\\\"]\"); await page.waitForSelector(\"div[role=\\\"textbox\\\"]\"); await page.fill(\"div[role=\\\"textbox\\\"]\", \"Your post content here\"); const [fileChooser] = await Promise.all([page.waitForEvent(\"filechooser\"), page.click(\"button[aria-label=\\\"Add media\\\"]\")]); await fileChooser.setFiles([\"/path/to/image.jpg\"]); await page.click(\"button:has-text(\\\"Post\\\")\"); return \"Post with media created successfully\"; }"}'
```

### Engage with Posts

```bash
# Like a post (by post URL or selector)
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_run_code \
  -p '{"code": "async (page) => { await page.goto(\"https://www.linkedin.com/feed\"); await page.waitForSelector(\"button[aria-label*=\\\"Like\\\"]\"); await page.click(\"button[aria-label*=\\\"Like\\\"]\"); return \"Post liked successfully\"; }"}'

# Comment on a post
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_run_code \
  -p '{"code": "async (page) => { await page.goto(\"https://www.linkedin.com/feed\"); await page.waitForSelector(\"div[aria-label=\\\"Comment\\\"]\"); await page.click(\"div[aria-label=\\\"Comment\\\"]\"); await page.waitForSelector(\"div[role=\\\"textbox\\\"][aria-label=\\\"Write a comment...\\\"]\"); await page.fill(\"div[role=\\\"textbox\\\"][aria-label=\\\"Write a comment...\\\"]\", \"Great post!\"); await page.keyboard.press(\"Enter\"); return \"Comment posted successfully\"; }"}'
```

### Monitor Activity

```bash
# Get notifications count
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_run_code \
  -p '{"code": "async (page) => { await page.goto(\"https://www.linkedin.com\"); await page.waitForSelector(\"button[aria-label=\\\"Notifications\\\"]\"); const badge = await page.$(\"button[aria-label=\\\"Notifications\\\"] .notification-badge\"); return badge ? await badge.textContent() : \"0\"; }"}'

# Extract recent posts from feed
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_run_code \
  -p '{"code": "async (page) => { await page.goto(\"https://www.linkedin.com/feed\"); await page.waitForSelector(\"div[id=\\\"feed-shared-update-v2\\\"]\"); const posts = await page.$$(\"div[id=\\\"feed-shared-update-v2\\\"]\"); return await Promise.all(posts.slice(0, 5).map(async post => ({ author: await post.$eval(\".update-actor\", el => el.textContent).catch(() => \"\"), content: await post.$eval(\".feed-shared-update-v2__description\", el => el.textContent).catch(() => \"\") }))); }"}'
```

### Wait for Conditions

```bash
# Wait for post to be published
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_wait_for \
  -p '{"text": "Your post was published"}'

# Wait for time (ms)
python3 scripts/mcp-client.py call -u http://localhost:8809 -t browser_wait_for \
  -p '{"time": 3000}'
```

## Workflow: Post Business Update

1. Navigate to LinkedIn feed
2. Click "Start a post"
3. Wait for editor to load
4. Fill post content
5. Add media (optional)
6. Click "Post"
7. Wait for confirmation
8. Screenshot result
9. Log to Dashboard.md

## Workflow: Generate Leads from Comments

1. Navigate to industry-related posts
2. Extract commenters
3. Log potential leads to Needs_Action folder
4. Create follow-up tasks

## Verification

Run: `python3 scripts/verify.py`

Expected: `✓ LinkedIn MCP server running`

## If Verification Fails

1. Run diagnostic: `pgrep -f "@playwright/mcp"`
2. Check: Server process running on port 8809
3. Try: `bash scripts/start-server.sh`
4. **Stop and report** if still failing - do not proceed with downstream steps

## Tool Reference

See [references/linkedin-tools.md](references/linkedin-tools.md) for complete tool documentation.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login required | Manually login once, session persists with shared-browser-context |
| Post button not found | Run browser_snapshot to get current element refs |
| Media upload fails | Ensure file path is absolute and accessible |
| Rate limiting | Wait 5-10 seconds between actions |
| Session expired | Re-login manually, then continue automation |

## Security Notes

- **Never automate connection requests** without human approval
- **Always use HITL** for sensitive actions (messaging, connection requests)
- **Respect LinkedIn ToS** - avoid excessive automation that could trigger account restrictions
- **Log all actions** to /Vault/Logs/ for audit trail
