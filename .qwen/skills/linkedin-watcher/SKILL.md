---
name: linkedin-watcher
description: |
  LinkedIn automation using Playwright. Monitor LinkedIn for opportunities,
  automatically post business content to generate sales, and engage with
  potential leads. Integrated with Qwen Code for content generation.
---

# LinkedIn Watcher Skill

Automate LinkedIn activities for business promotion and lead generation using Playwright.

## Quick Start

```bash
# 1. Install Playwright
pip install playwright
playwright install chromium

# 2. Start LinkedIn Watcher (first time - visible mode for login)
python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault --visible

# 3. Login to LinkedIn manually (first time only)

# 4. Start automated posting (headless mode)
python .qwen/skills/linkedin-watcher/scripts/linkedin_watcher.py --vault ./AI_Employee_Vault --action post
```

## Architecture

```
LinkedIn → Playwright → Content Generator → Posts → Lead Detection → Needs_Action/
```

## Features

- **Auto-post business content** - Generate and post sales content
- **Lead detection** - Monitor comments and messages for potential leads
- **Engagement tracking** - Track post performance
- **Session persistence** - Login once, reuse session

## Files

- `scripts/linkedin_watcher.py` - Main watcher script
- `scripts/linkedin_post.py` - Post creation and scheduling
- `scripts/verify.py` - Verification script
- `content/` - Pre-written business content templates

## Usage

See SKILL.md for complete documentation.
