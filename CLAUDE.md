# Authoring Skills in This Repository

A guide to creating, refining, and publishing agent skills for this library. Grounded in [Anthropic's skill creation guideline](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills), adapted for Mario's personal engineering workflows.

## What Makes a Good Skill

A skill is **domain expertise encoded as reusable instructions** for Claude. The best skills in this repo:

1. **Solve a specific, repeatable task** — not a one-off problem or a general capability Claude already has.
   - ✅ "Multi-step code review workflow with tiered feedback and PR integration"
   - ❌ "Help me review code" (too vague; Claude does this natively)

2. **Distill real mental models** — your actual approach to thinking and problem-solving, not a generic process.
   - ✅ `code-review`: Applies pragmatic senior + staff engineer lenses simultaneously
   - ❌ "Code review checklist" (any engineer could write this)

3. **Define when they should be used** — phrase the description as "use when…" not "does…"
   - ✅ "Use when given a PR link or asked to review code changes"
   - ❌ "Provides code review feedback"

4. **Are focused and composable** — one workflow per skill, designed to stack with others.
   - ✅ `dev-workflow` (design → implement → PR) + `code-review` (review the PR)
   - ❌ One mega-skill that does design, implementation, review, and deployment

5. **Stay under limits** — 500 lines, ~5,000 tokens (validated with `make validate`).

## Structure

Every skill lives in `.agents/skills/<name>/SKILL.md` with this structure:

```
---
name: <name>                          # 64 chars max; e.g., "Code Review"
description: >-                       # 200 chars max; imperative, user-focused
  Use when given a PR link or asked
  to review code changes...
disable-model-invocation: true        # (optional) prevents accidental invocation
dependencies: python>=3.8             # (optional) runtime requirements
---

# <Title>

<Body: phases, rules, gotchas, examples>
```

### Metadata fields

#### `name` (required, 64 chars max)
Human-friendly skill name. Examples: "Code Review", "Pump to Obsidian", "Resume Review".

#### `description` (required, 200 chars max)
**Critical field.** Claude uses this to decide whether to invoke the skill. Make it:

- **Imperative**: "Use when…" or "Apply this skill to…" Frame as instructions to Claude.
- **User-focused**: Describe what the *user* wants to achieve, not what the skill does internally.
- **Specific**: List concrete triggers. Examples from this repo:
  
  ```
  ❌ "Provides code review feedback"
  ✅ "Review a PR as a pragmatic senior/staff engineer. Use when given a PR link, 
     branch name, or asked to review code changes."
  
  ❌ "Pushes content to Obsidian"
  ✅ "Capture context from the current session and push it as a note to your 
     Obsidian vault via PR. Use when the user says 'pump to obsidian' or 
     'save this to my notes'."
  ```

- **Concise**: Under 200 chars means being ruthless with words. Cut boilerplate; keep triggers and intent.

#### `disable-model-invocation` (optional)
Set to `true` if the skill should *never* auto-invoke (e.g., skills that mutate repos). The user explicitly invokes it via `/skill-name`.

#### `dependencies` (optional)
Runtime requirements. Examples: `python>=3.8`, `node>=16, git>=2.30`. If a skill shells out to `gh` or git, consider documenting this here.

### Markdown body

The markdown body is the **operational manual** — phases, rules, gate conditions, gotchas, and examples.

**Structure** (use what fits; not all skills need all sections):

1. **Confirmation** — if the skill is destructive or requires approval, confirm intent first.
2. **Phases** — numbered steps or gated workflow (Phase 1 → Phase 2 → …).
3. **Rules & constraints** — hard boundaries (do NOT X, always Y, max Z attempts).
4. **Gotchas** — surprises, edge cases, common mistakes.
5. **Examples** — before/after, templates, command snippets.

**Patterns from this repo:**

- **Phase-driven** (`dev-workflow`, `pump-to-obsidian`): Multi-step workflows with explicit gates (approval, pass tests, etc.). Use checkboxes and "Do not proceed until…" to force sequencing.
  
- **Lens-based** (`code-review`, `resume-review`): Apply multiple evaluative frameworks in parallel or sequence. Tables help organize dimensions.
  
- **Checklists + templates** (`resume-review`): SMART framework, decision rules, output format.

Pick the pattern that matches your workflow. Mix and match if needed.

## Writing Principles

### 1. Add what the agent lacks; omit what it knows
Don't tell Claude how to write Markdown, call APIs, or use git — it already knows. *Do* tell Claude:
- Your specific decision criteria (why you prefer simplicity over abstraction)
- Workflow sequences that prevent mistakes (test before commit; commit before PR)
- Domain knowledge it wouldn't guess (ALP signal + Canva Values for hiring)

### 2. Be prescriptive when fragility or consistency matters
Example from `dev-workflow`: "Hard constraints: Do NOT refactor existing code, bundle unrelated changes, or modify tooling without approval." This prevents common pitfalls.

Example from `code-review`: Specific lens order (correctness → simplicity → testability → readability) ensures consistent prioritization.

### 3. Provide defaults, not menus
When multiple paths exist, pick one and mention alternatives briefly:

```
❌ "You could use gh pr diff or git diff. Which would you prefer?"
✅ "Use gh pr diff (preferred). Alternatively: git diff <base>..<head>"
```

### 4. Favor procedures over declarations
Show Claude *how* to approach a problem, not what to output for a specific instance:

```
❌ "Write a high-level design document describing the architecture."
✅ "Copy docs/HLD_TEMPLATE.md → docs/<doc-name>.md and fill it in (bullet 
    points, concise). Derive <doc-name> by replacing '/' with '-' in the 
    branch name."
```

### 5. Keep it under 500 lines, ~5,000 tokens
Validate with:
```bash
make validate file=.agents/skills/my-skill/SKILL.md
```

If you exceed limits, move reference material to a separate `REFERENCE.md` file and link it from the main skill.

## Common Patterns

### Pattern: Phase-driven workflow
For multi-step processes with gates (approval, test passage, PR merge):

```markdown
---
name: my-workflow
description: >-
  Use when the user asks to start [X workflow]. Always shows a plan for 
  approval before proceeding.
disable-model-invocation: true
---

# My Workflow

Work through phases in order. Do not skip phases or pass a gate without 
meeting its condition.

```
- [ ] Phase 1: Prepare
- [ ] Phase 2: Draft (GATE: approval)
- [ ] Phase 3: Execute
- [ ] Phase 4: Report
```

## Phase 1 — Prepare
...

## Phase 2 — Draft + Plan
Show the user a plan before touching anything. 

**GATE:** Present the plan and wait for explicit approval.

## Phase 3 — Execute
Proceed only after Phase 2 approval.
...

## Phase 4 — Report
...
```

### Pattern: Lens-based evaluation
For reviews or audits across multiple dimensions:

```markdown
## Persona & Lenses

Adopt **two frameworks simultaneously**:
- **Framework A** — ...
- **Framework B** — ...

## Review by priority

| # | Lens | Key questions |
|----|------|---------------|
| 1 | **Lens A** | ? |
| 2 | **Lens B** | ? |

## Format feedback

Group findings by severity:
- 🔴 **Critical** — must fix
- 🟡 **Suggestion** — consider
- 🟢 **Nice to have** — worth noting
```

### Pattern: Gotchas
Always include a "Gotchas" section at the end:

```markdown
## Gotchas

- **Specific surprise 1** — what goes wrong, how to avoid it.
- **Specific surprise 2** — edge case that trips people up.
```

Good gotchas from this repo:
- `pump-to-obsidian`: "No secrets. Strip API keys, tokens, passwords before they go in the note."
- `code-review`: "Don't flag style issues that a linter already enforces; mention the tool instead."
- `resume-review`: "Titles lie, bullets don't. Judge by evidence in bullets, not role title."

## Testing & Validation

### Before committing
1. **Run validation**:
   ```bash
   make validate file=.agents/skills/my-skill/SKILL.md
   ```
   Checks: line count, token count, description length.

2. **Review clarity**:
   - Can you read it in 5 minutes?
   - Are triggers and decision points clear?
   - Are gotchas specific and actionable?

3. **Check consistency**:
   - Does formatting match other skills (phase headers, gotchas, tables)?
   - Is the description imperative and under 200 chars?

### After publishing
In Claude Code or claude.ai:
1. Enable the skill in **Customize > Skills**.
2. Try prompts that *should* trigger it.
3. Try prompts that *shouldn't* and confirm it doesn't fire.
4. Check Claude's thinking to see if it's loading the skill.
5. Iterate on the description if triggering is off.

## Refactoring Checklist

When improving an existing skill:

- [ ] Description is imperative ("Use when…") and ≤200 chars
- [ ] No jargon without context; explain acronyms on first use
- [ ] Phases (if any) are explicitly numbered and gated
- [ ] Rules are prescriptive ("Do NOT…", "Always…") not advisory
- [ ] Gotchas are specific to *this* workflow, not generic advice
- [ ] All referenced tools/files/repos are real and current (git status, file checks)
- [ ] Validation passes: `make validate file=<path>`
- [ ] Formatting is consistent with other skills (headers, tables, lists)

## DRY Principles for Skills

1. **Don't repeat process steps across skills** — factor out to reusable "sub-skills" or shared reference docs.
   - Example: `dev-workflow` and `code-review` are separate but composable; a user runs workflow, then reviews the PR independently.

2. **Don't hardcode user-specific context** — parameterize or ask at runtime.
   - Example: `pump-to-obsidian` defaults to `marioplumbarius/obsidian` but can be overridden.

3. **Don't duplicate decision criteria** — link to shared frameworks.
   - Example: `resume-review` uses Amazon LP + Canva Values scoring; if you build another hiring skill, reference the same framework.

4. **Don't document version-specific tooling in the skill** — link to external docs and mention fallbacks.
   - Example: `code-review` uses `gh cli` (preferred) but mentions `git diff` as an alternative.

## Repository Commands

```bash
# Generate a new skill
make generate name=my-new-skill

# Validate an existing skill
make validate file=.agents/skills/my-skill/SKILL.md

# Run tests
make test

# See all commands
make help
```

## Examples in This Repo

Study these skills as templates:

- **`pump-to-obsidian`** — Phase-driven workflow with gates (approval, auto-merge).
- **`dev-workflow`** — Complex multi-phase process with hard constraints and gotchas.
- **`code-review`** — Lens-based review with structured output format and severity tiers.
- **`resume-review`** — Framework-heavy evaluation (SMART + ALP + Canva Values) with scoring and decision rules.

## Publishing

### As a Claude Code plugin
Skills are auto-discovered and published via `.claude-plugin/plugin.json`. No action needed — every push to main triggers an auto-refresh for installed users.

### To the Claude app (claude.ai / Desktop)
Package and upload via **Settings > Capabilities > Skills > Upload skill**:
```bash
( cd .agents/skills && zip -r ../../my-skill.zip my-skill )
```

Upload the ZIP. Note: Skills using `gh` or GitHub MCP won't function in the app.

## References

- [Anthropic: How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- [This repo's AGENTS.md](AGENTS.md) — workflow guide for the skill-creation process itself
- [SKILL.template.md](SKILL.template.md) — minimal template to get started
