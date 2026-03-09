---
name: plan-generator
description: |
  Plan generator for Qwen Code reasoning loop. Automatically analyzes tasks in
  Needs_Action folder and generates structured Plan.md files with objectives,
  steps, and approval requirements. Use with Qwen Code as the brain.
---

# Plan Generator Skill

Automated plan generation using Qwen Code reasoning patterns. Creates structured `Plan.md` files for each task requiring action.

## Quick Start

```bash
# Generate plans for all action items
python .qwen/skills/plan-generator/scripts/plan_generator.py --vault ./AI_Employee_Vault --all

# Process with Qwen Code
qwen --cd ./AI_Employee_Vault
# "Review the plans in the Plans folder and execute them"
```

## Architecture

```
Needs_Action/ → Plan Generator → Plans/ → Qwen Code → Execution
```

## Files

- `scripts/plan_generator.py` - Plan generation script
- `scripts/verify.py` - Verification script
- `templates/plan_template.md` - Plan template

## Usage

See SKILL.md for complete documentation.
