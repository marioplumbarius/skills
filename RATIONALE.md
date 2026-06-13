# Mario's Skill Philosophy — Rationale

This document explains the *why* behind the principles documented in [AGENTS.md](AGENTS.md). It captures the reasoning, sources, and lessons that shaped Mario's approach to skill authorship.

## Core Principles: Where They Come From

### 1. Ground in expertise, not hypotheticals

**Why:** Skills are instructions for agents to follow. An instruction is only as good as the mental model behind it. If you're writing a code-review skill, you need to have *opinions* about code quality—formed by actually reviewing code, not by reading best-practice articles.

**Source:** Years of doing actual code reviews, hiring interviews, and skill creation. When instructions are vague, it's because the author hasn't solved the problem repeatedly enough to develop a clear pattern.

**Edge case:** New domains need research first. But once you've done that research and solved a few problems, ground your instructions in that experience, not in theoretical best practices.

### 2. Be prescriptive when fragility matters

**Why:** When an operation can break (file writes, merges, deletions), agents *should* follow a specific sequence. A well-intentioned "do whatever works" approach usually leads to subtle bugs.

**Example:** In `pump-to-obsidian`, always use GitHub MCP tools in a specific order: check branch exists → create branch → commit → open PR → merge. Skipping the branch check or merging before PR approval are subtle ways it breaks.

**Source:** Learned from debugging automation that had multiple failure modes. The more operations are autonomous, the more prescriptive the instructions need to be.

### 3. Favor defaults, not menus

**Why:** When a skill says "you can use X or Y," agents often freeze or pick arbitrarily. If you, the author, have a strong opinion about which is better, *say so*. This doesn't mean "never mention alternatives"—it means defaulting to the best choice and explaining why.

**Example:** In `code-review`, always use `gh pr diff` (not `git diff`) because it avoids local cloning overhead. But if GitHub CLI isn't available, fall back to git. The default is clear; the exception is documented.

**Source:** Watching agents and humans get paralyzed by choice. Constraints are actually freeing.

### 4. Design coherent units

**Why:** A skill should solve a *class* of problems, not a one-off task. This makes skills reusable and composable.

**Bad skill:** "Review my PR from yesterday" (one-off, not reusable)
**Good skill:** "Code review" (apply to any PR, any time)

**Source:** Early skills were often too narrow (e.g., "fix this bug in this specific file"). They worked once, then were useless. Broader framing makes skills more valuable.

### 5. Validation loops protect against mistakes

**Why:** Autonomous operations (merging PRs, writing files, deleting things) can destroy work in seconds. The cost of asking "are you sure?" is tiny compared to the cost of accidentally merging the wrong branch.

**Example:** In `pump-to-obsidian`, phase 2 requires explicit approval before phase 3 opens a PR. This is where we catch misunderstandings.

**Source:** Experience with "smart" automation that did exactly what I asked, not what I *meant*. The three-part gate (present plan → ask → execute) has never failed me.

### 6. Moderate detail is the target

**Why:** Too little detail → agent gets stuck. Too much detail → overwhelming and hard to follow.

**Target:** 5–8 distinct sections. Usually one per decision point or phase.

**Source:** Reading skill documentation from across projects. The ones that worked had moderate detail; overly detailed ones confused, under-detailed ones failed.

## The Three-Pass Approach

### Why three passes?

Creating a skill involves:
1. **Scaffolding** (skill-creator handles this)
2. **Standards** (AgentSkills specification is the community standard)
3. **Personal philosophy** (Mario's approach, tested through 4 live skills)

These three sources sometimes conflict. Example:
- AgentSkills spec says "description can be up to 1024 characters"
- Mario's rule: "craft it tight, under 200 characters, because if you can't describe the skill briefly, it's not coherent"

Resolving this: Mario's rule wins. It's more restrictive, but produces better skills.

### Why this priority order?

**Mario > AgentSkills > skill-creator** (bottom to top override)

1. **skill-creator** provides the foundation. It handles scaffolding, validation, the basic structure. Don't reinvent this.
2. **AgentSkills** provides standards. Use the spec fields, follow naming conventions, document gotchas. This is the community standard.
3. **Mario's philosophy** is the customization layer. It reflects hard-won lessons from actual skill usage.

When they conflict, the customization layer (Mario) wins because it's grounded in repeated experience.

## The Four Skills as Evidence

Each of the 4 skills demonstrates these principles:

### `code-review`
- **Principle: Be prescriptive when fragility matters**
  - Code review feedback can be harsh or encouraging. The skill uses structured severity tiers (🔴 / 🟡 / 🟢) to make the feedback constructive.
- **Principle: Design coherent units**
  - "Review a PR" is broad enough to apply to any PR, any language. But narrow enough to have a clear workflow.

### `dev-workflow`
- **Principle: Validation loops**
  - Design approval (phase 2 gate) blocks implementation. This catches misunderstandings before wasted work.
- **Principle: Ground in expertise**
  - The workflow reflects Mario's experience shipping features: baseline tests → design → implementation → PR.

### `pump-to-obsidian`
- **Principle: Favor defaults**
  - Default destination: `Inbox/`, target repo: `marioplumbarius/obsidian`. But these are configurable.
- **Principle: Validation loops (critical for autonomous ops)**
  - Three explicit gates before auto-merge. Approval in phase 2 authorizes both content and auto-merge.

### `resume-review`
- **Principle: Moderate detail**
  - 6 phases, clear decision rules, no ambiguity. Not 20 phases, not 2.
- **Principle: Ground in expertise**
  - Scoring frameworks use Amazon Leadership Principles + Canva Values (frameworks Mario has used for hiring).

## Where This Conflicts With "Best Practices"

### Conflict 1: Prescriptive vs. Flexible

**Mainstream advice:** "Give agents choices, let them figure it out."
**Mario's approach:** "Be prescriptive. Choices paralyze agents."

**Why Mario's approach:** Watched too many "flexible" automations produce inconsistent results. Prescriptiveness is a feature, not a bug.

### Conflict 2: DRY (Don't Repeat Yourself)

**Mainstream advice:** "Avoid repeating instructions, reference external docs."
**Mario's approach:** "Keep instructions self-contained. Link to external resources, don't delegate to them."

**Why:** If a skill's instructions depend on reading 5 other docs, agents get confused. The skill should be understandable in isolation.

### Conflict 3: Simplicity

**Mainstream advice:** "Keep everything simple and reusable."
**Mario's approach:** "Make it *complete* before making it simple. Completeness includes validation gates, gotchas, constraints."

**Why:** A simple skill that fails silently is worse than a complex skill that fails loudly.

## What's Intentionally Missing

### No approval from external experts
These principles aren't peer-reviewed or validated by others. They're Mario's personal approach, grounded in experience, not in academic research.

### No formal framework
This isn't a methodology (like Agile or Design Thinking). It's a collection of patterns that worked.

### No universal applicability claim
Mario's principles work well for personal skills (code review, hiring, dev workflows). They might not work for public tools (CLI apps, libraries). Adjust as needed.

## How to Use This

If you're creating skills and disagree with something in [AGENTS.md](AGENTS.md):

1. **Understand the rationale** (read this file)
2. **Respect the principle**, even if you'd do it differently
3. **If you find a gap or flaw**, document it and raise it (with examples)

Good skill creation is iterative. These principles have been tested on 4 production skills. But they're not gospel—they're working hypotheses.
