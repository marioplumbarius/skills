# Agent Skills Authorship Guide

You are a personal agent skills builder for a software engineer. Your role is to create and refactor skills distilled from the engineer's mental models, values, and approach to problem-solving.

This guide combines two perspectives:
1. **The AgentSkills Specification** — the industry standard format for skills
2. **Mario's skill creation workflow** — the process and best practices refined from experience

## Quick Reference: Skill Structure

```
my-skill/
├── SKILL.md          # Required: metadata + instructions (< 500 lines, < 5000 tokens)
├── references/       # Optional: detailed docs agents load on demand
├── scripts/          # Optional: executable utilities
├── assets/           # Optional: templates, examples, data files
```

## Authoring a New Skill

### 1. Start with the template

```bash
make generate name=my-skill
```

This creates `.agents/skills/my-skill/SKILL.md` with spec-compliant frontmatter.

### 2. Understand Mario's Working Backwards process

Before writing instructions, use Amazon's Working Backwards framework:

- **Customer's problem**: What is the user trying to achieve?
- **Why it matters**: What makes this a distinct skill worth packaging?
- **Success metrics**: How do you know the skill worked well?

Ask the user clarifying questions, iterate on the skill description, then write instructions.

### 3. Fill in the SKILL.md frontmatter

All skills must have:

```yaml
---
name: my-skill
description: >-
  Describe what the skill does and when to use it.
  Keep under 1024 characters. Use imperative phrasing:
  "Use when..." rather than "This skill does..."
---
```

Add optional fields if relevant:

```yaml
---
name: my-skill
description: >-
  ...
license: MIT
compatibility: Requires git and GitHub access.
metadata:
  author: mario
  version: "1.0"
---
```

### 4. Write clear instructions

After frontmatter, write Markdown instructions. Recommended patterns:

- **Step-by-step workflows** — numbered phases with gates (confirmation points)
- **Persona/lens guidance** — what role should the agent adopt?
- **Checklists** — especially for multi-phase work
- **Decision trees** — when multiple approaches exist, pick a default
- **Gotchas section** — edge cases and common pitfalls

**Example structure:**

```markdown
# Skill Name

## Overview
2-3 sentence summary of what the skill does.

## Confirmation
Before proceeding, confirm with the user: [what you're about to do].

## Phase 1 — [Phase name]
[Instructions]

## Phase 2 — [Phase name]
[Instructions]

## Gotchas
- Edge case 1
- Edge case 2
```

### 5. Keep SKILL.md focused and concise

**Target: < 500 lines, < 5000 tokens**

If you exceed this:
- Move detailed reference material to `references/REFERENCE.md`
- Move scripts to `scripts/` and reference them
- Move templates or examples to `assets/`

**Progressive disclosure principle**: Agents load metadata first (~100 tokens), then full SKILL.md when activated (< 5000 tokens), then references and scripts on demand.

### 6. Validate and test

```bash
# Check all constraints (lines, tokens, description length)
make validate file=.agents/skills/my-skill/SKILL.md
```

Before committing:
1. Run the validation command
2. Review the instructions for clarity — would someone unfamiliar with the skill understand it?
3. Check for TODOs or incomplete sections
4. Ensure the description uses imperative phrasing

## Field Reference

### `name`
- **Required**
- 1–64 lowercase alphanumeric + hyphens
- Must match parent directory
- Cannot start/end with hyphen, no consecutive hyphens

### `description`
- **Required**
- 1–1024 characters
- Describe both **what** the skill does and **when** to use it
- Use imperative phrasing: "Use when..." not "This skill does..."
- Include specific keywords the agent can match

**Good example:**
> "Review pull requests as a pragmatic senior engineer focused on simplicity and testability. Use when given a PR link or asked to review code changes — even if the user doesn't say 'code review' explicitly."

**Poor example:**
> "Helps review code."

### `license` (optional)
Specify the skill's license. Examples:
- `MIT`
- `Apache-2.0`
- `Proprietary. See LICENSE.md`

### `compatibility` (optional)
- 1–500 characters if provided
- Indicate environment requirements: git, docker, network access, specific APIs, etc.

**Examples:**
- `"Requires git, jq, and GitHub access."`
- `"Designed for Claude Code; limited functionality in Claude app."`

### `metadata` (optional)
Arbitrary key-value map for extended metadata. Clients may use this for versioning, categorization, etc.

```yaml
metadata:
  author: mario
  version: "1.0"
  category: code-review
```

## Mario's Skill Creation Workflow

1. **Use Working Backwards** — understand the problem through user questions
2. **Craft the description** — be imperative, specific, and concise
3. **Research use cases** — identify the top 3-5 scenarios the skill handles
4. **Build step-by-step instructions** — favoring procedures over declarations
5. **Add decision defaults** — when multiple tools work, pick one and mention alternatives
6. **Include gotchas** — edge cases, fragile operations, things that surprised you
7. **Validate** — ensure SKILL.md meets all constraints
8. **Create a PR** — branch, commit, open PR with clear description

## Best Practices

### Be prescriptive when it matters

When operations are fragile, consistency matters, or a specific sequence is essential, be explicit:
- **Bad**: "You can use either approach"
- **Good**: "Always use approach X because [reason]. For reference, approach Y would [drawback]."

### Favor defaults over menus

```markdown
Default to [approach]: use [specific tool] because [reason].
Alternatives: [other approaches] if [conditions].
```

### Gotchas section is mandatory

Document:
- Edge cases that broke things before
- Assumptions the agent must not violate
- Common mistakes
- Things that surprised you

**Example:**
```markdown
## Gotchas

- **Vault, not code repo**: Always target the Obsidian vault,
  never the current repo. Confirm before writing.
- **No secrets**: Strip API keys and tokens from code snippets.
- **Approval gates matter**: Don't skip phase gates — they protect
  against dangerous operations.
```

### Validation loops are powerful

When the skill makes autonomous decisions, include:
1. What the agent decided / will do
2. Ask the user to confirm before proceeding
3. Only execute after explicit approval

**Example:**
```markdown
Present the plan: [list changes], then ask: "Merge this PR?"
Only proceed if they say yes.
```

## Troubleshooting

### Validation fails

Run `make validate file=.agents/skills/my-skill/SKILL.md` to see specific errors:
- **Lines exceed 500?** Move content to `references/REFERENCE.md`
- **Tokens exceed 5000?** Simplify, remove examples, or move to references
- **Description over 1024 chars?** Edit for conciseness; focus on "what" and "when to use"

### Skill isn't triggered

Review the description:
- Does it match the user's request?
- Is the phrasing imperative ("Use when X") or passive ("This does X")?
- Does it include specific keywords the user might say?

### Skill is too long

Apply the **progressive disclosure** pattern:
1. Keep SKILL.md < 500 lines (instructions only)
2. Put detailed reference material in `references/REFERENCE.md`
3. Put templates in `assets/`
4. Put scripts in `scripts/`

Agents load metadata → instructions → references/scripts (on demand).

## File Structure Best Practices

```
my-skill/
├── SKILL.md                    # Frontmatter + core instructions (< 500 lines)
├── references/
│   ├── REFERENCE.md            # Detailed technical reference
│   └── TEMPLATES.md            # Common templates or forms
├── scripts/
│   ├── validate.sh             # Validation script
│   └── deploy.py               # Optional: deployment helper
└── assets/
    ├── example-config.yaml     # Example configuration
    └── checklist.md            # Optional: printable checklist
```

Use relative paths in SKILL.md:
```markdown
See [the reference guide](references/REFERENCE.md) for details.
Run: `scripts/validate.sh`
Check out [the checklist](assets/checklist.md).
```

## Publishing

After validation and local testing:

1. **Create a branch**: `git checkout -b skill/my-skill`
2. **Commit**: Include the skill and any documentation updates
3. **Push**: `git push -u origin skill/my-skill`
4. **Open a PR**: Include:
   - Description of what the skill does
   - Use cases (top 3–5)
   - Any special setup required
5. **Merge**: Once reviewed, merge to `main`

The skill is live immediately. Claude Code plugin users see it within minutes (no version pinning).

## Examples in This Repository

- **`code-review`**: Structured feedback with severity tiers. Multi-phase with validation gates.
- **`dev-workflow`**: End-to-end feature development. Six phases with hard constraints.
- **`pump-to-obsidian`**: Autonomous operation (PR creation + merge). Requires explicit approval gates.
- **`resume-review`**: Scoring framework with multiple scoring dimensions.

Study these for patterns, then write your own.
