# Contributing Skills

A quick guide to creating and testing a new skill in this repository.

## Quick Start

### 1. Create a new skill

```bash
make generate name=my-skill
```

This creates `.agents/skills/my-skill/SKILL.md` from the template. Open it and start writing.

### 2. Fill in metadata

```yaml
---
name: My Skill               # 64 chars max
description: >-              # 200 chars max, imperative ("Use when...")
  Use when the user asks for...
disable-model-invocation: true  # (optional) prevent accidental invocation
dependencies: python>=3.8    # (optional) if your skill requires packages
---
```

### 3. Write the skill body

See [CLAUDE.md](CLAUDE.md) for patterns, gotchas, and examples. Use:
- **Phases** for multi-step workflows
- **Lenses** for evaluation-based skills
- **Checklists** for procedures
- **Gotchas** for edge cases

### 4. Validate

```bash
make validate file=.agents/skills/my-skill/SKILL.md
```

Must pass before you commit. Checks: ≤500 lines, ~5,000 tokens, description ≤200 chars.

### 5. Test in Claude Code

#### Option A: Claude Code (CLI)
```bash
# Start a local Claude Code session
claude

# In the session, enable the skill from local disk:
# /plugin local .agents/skills
# /plugin install my-skill

# Test with: /my-skill <prompt>
```

#### Option B: Claude Code (web/Desktop)
1. Go to **Customize > Skills > Upload skill**
2. Create a ZIP:
   ```bash
   ( cd .agents/skills && zip -r ../../my-skill.zip my-skill )
   ```
3. Upload `my-skill.zip` and test

### 6. Commit and push

```bash
git add .agents/skills/my-skill/
git commit -m "Add skill: my-skill"
git push origin HEAD
```

## Folder Structure

Every skill is one directory under `.agents/skills/`:

```
.agents/skills/my-skill/
├── SKILL.md              # Required: the skill definition
├── REFERENCE.md          # (optional) supplemental reference material
├── script.py             # (optional) executable code if needed
└── resources/            # (optional) example files, templates, etc.
```

For most skills, just `SKILL.md` is enough.

## Common Tasks

### See all skills
```bash
ls .agents/skills/
```

### Study an existing skill
```bash
cat .agents/skills/code-review/SKILL.md
```

### Validate all skills
```bash
for skill in .agents/skills/*/; do
  make validate file="$skill/SKILL.md" || exit 1
done
```

## Key Rules

- **Metadata must be correct**: name (≤64 chars), description (≤200 chars, imperative).
- **Skill body**: ≤500 lines, ~5,000 tokens. Move reference material to `REFERENCE.md` if needed.
- **Descriptions are triggers**: Write as "Use when…" not "Does…"
- **Phases are gated**: Explicit conditions before proceeding to the next phase.
- **Gotchas are specific**: Edge cases and surprises relevant to *this* skill, not generic advice.

## Examples to Study

- **Procedural workflow**: `dev-workflow` (design → implement → PR → review)
- **Code review**: `code-review` (senior + staff engineer lenses with severity tiers)
- **Evaluation framework**: `resume-review` (SMART + ALP + Canva Values scoring)
- **Session capture**: `pump-to-obsidian` (multi-phase workflow with auto-merge)

## Publishing

Skills are auto-published via [Claude Code plugin marketplace](README.md#use-the-skills-in-claude-code-cli--web). Every push to `main` auto-refreshes for installed users.

To upload to the Claude app (claude.ai / Desktop):
```bash
( cd .agents/skills && zip -r ../../my-skill.zip my-skill )
```
Then go to **Settings > Capabilities > Skills > Upload skill** and upload the ZIP.

## Questions?

- **How do I write a skill?** → [CLAUDE.md](CLAUDE.md)
- **What are the limits?** → See `make validate` or [CLAUDE.md](CLAUDE.md#writing-principles)
- **Official guideline?** → [Anthropic: How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
