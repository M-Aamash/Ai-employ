---
name: gmail-watcher
description: |
  Gmail monitoring using Gmail API. Watch for new emails, detect important messages,
  and create action files in the Obsidian vault. Use for email triage, lead capture,
  and communication automation. Integrated with Qwen Code for processing.
---

# Gmail Watcher Skill

Monitor Gmail for new and important emails, creating actionable items in your Obsidian vault for Qwen Code to process.

## Quick Start

```bash
# 1. Place your credentials.json in project root
# 2. Authorize Gmail API
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --authorize

# 3. Start watching
python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault ./AI_Employee_Vault --interval 120
```

## Architecture

```
Gmail API → Gmail Watcher → Needs_Action/ → Qwen Code → Plan.md → Action
```

## Files

- `scripts/gmail_watcher.py` - Main watcher script
- `scripts/base_watcher.py` - Base class for all watchers
- `scripts/verify.py` - Verification script
- `references/gmail-queries.md` - Query reference guide

## Usage

See SKILL.md for complete documentation.
