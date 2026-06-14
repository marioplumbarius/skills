---
name: <name>
description: >-
  Use when the user asks to... (imperative phrasing, ≤200 chars, no generic 
  boilerplate — be specific about triggers and user intent)
disable-model-invocation: true
---

# <Title>

## Confirmation

Before proceeding, confirm the task and summarize what you understand the user 
wants. Ask the user to approve before continuing.

## Phase 1 — <Phase name>

Document the first phase of your workflow. Be prescriptive: tell Claude exactly 
how to approach this step, not what the ideal output looks like.

- Use checklists for procedures
- Use tables for comparing options or dimensions
- Use examples when helpful

### Rules & constraints
- **Do NOT** — hard boundaries that prevent mistakes
- **Always** — invariants to maintain
- **Max N attempts** — retry limits

## Phase 2 — <Phase name> (GATE: approval)

If this phase requires approval or validation, mark it clearly. Use this pattern:

**GATE:** [Condition for proceeding]. Do not continue until [specific approval/test/validation].

## Gotchas

- **Specific issue 1** — what goes wrong, how to avoid it. Grounded in real experience.
- **Specific issue 2** — edge case or surprise that trips people up.

---

## How to use this template

1. Replace `<name>` with the skill name (64 chars max, e.g. "Code Review", "Pump to Obsidian")
2. Replace `<description>` with an imperative trigger (200 chars max)
   - ✅ "Use when given a PR link or asked to review code changes"
   - ❌ "Provides code review feedback"
3. Delete "disable-model-invocation: true" if the skill should auto-trigger
4. Rename phases to match your workflow (e.g., "Prepare", "Draft", "Execute", "Report")
5. Add sections that fit your skill (gotchas, examples, rules, templates)
6. Keep it under 500 lines and ~5,000 tokens
7. Run: `make validate file=.agents/skills/<name>/SKILL.md`

See [CLAUDE.md](CLAUDE.md) for patterns, principles, and examples from this repo.