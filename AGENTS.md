# Mario's Skills Philosophy

This document captures lessons from building skills for code review, development workflows, autonomous operations, and hiring decisions.

## Core Principles

### Ground in expertise, not hypotheticals

Every skill should reflect *actual* patterns you've solved repeatedly. If writing a code-review skill, you have strong opinions about code quality. If building a resume-review skill, you've screened hundreds of resumes.

**Don't write skills for one-off tasks or theoretical problems.**

### Be prescriptive when fragility matters

```markdown
❌ Bad:   "You can use either approach"
✅ Good:  "Always use approach X because [reason].
          Fallback to Y only if [conditions]."
```

When operations are fragile, consistency matters, or a specific sequence is essential—be explicit about *why*.

### Favor defaults, not menus

When multiple tools or approaches work:
- Pick one as the default
- Explain why it's the best choice
- Mention alternatives briefly

This saves agents from decision paralysis.

### Design coherent units

A skill solves a *class* of problems, not a one-off task:
- ✅ "Code review" (applies to any PR)
- ✅ "End-to-end feature development" (applies to any non-trivial change)
- ❌ "Review my PR from yesterday" (one-off)
- ❌ "Fix this specific bug" (one-off)

**Test**: Can you describe the skill in one sentence? If not, it may be incoherent.

### Validation loops protect against mistakes

For autonomous operations (PR merges, file writes, commits):

```markdown
1. Present the plan to the user:
   - [What you decided]
   - [What will change]
2. Ask: "Proceed?"
3. Only execute after explicit approval
```

This prevents accidental commits, secret leaks, or bad merges.

### Moderate detail is your target

Too little: "Write good code" is not actionable.
Too much: 40 sections with every edge case is overwhelming.

Target: 5–8 distinct sections. One section per major decision point.

## Mario's Workflow

1. **Use Amazon's Working Backwards** — Ask clarifying questions. Understand the real problem.
2. **Craft the description** — Imperative, specific, under 1024 characters. This determines whether the agent even considers the skill.
3. **Map use cases** — Identify 3–5 scenarios where the skill applies.
4. **Write step-by-step instructions** — Favor *procedures* (how to do X) over *declarations* (what X produces).
5. **Build validation gates** — Especially for autonomous operations. Always ask before executing.
6. **Document gotchas** — Edge cases, fragile operations, things that surprised you.
7. **Validate and iterate** — `make validate file=<path>`. Run through with a test user.
8. **Create a PR** — Branch, commit, push. Include clear use cases in the PR description.

## The Skills in This Repository

### code-review
**Pattern**: Multi-lens review with severity tiers.
- Applies three distinct lenses (correctness, simplicity, testability, readability) in priority order
- Groups feedback by file and severity
- Uses a clear recommendation format (APPROVE / REQUEST CHANGES / NEEDS DISCUSSION)

### dev-workflow
**Pattern**: Six-phase feature development with hard constraints.
- Phase 1: Baseline (run tests first)
- Phase 2: Design (write HLD, get approval)
- Phase 3: Implement (task-by-task, with verification gates)
- Phase 4: Pull request (push and create PR)
- Phase 5: Self-review (post trade-off commentary)
- Phase 6: Retrospective (update docs)

### pump-to-obsidian
**Pattern**: Autonomous GitHub operations with approval gates.
- Phase 1: Gather context from session
- Phase 2: Draft note + present plan (GATE: approval)
- Phase 3: Open PR (create branch, commit, open PR)
- Phase 4: Auto-merge + report (only after approval)

Key lesson: Approval in phase 2 authorizes both the content *and* the auto-merge. Don't skip gates.

### resume-review
**Pattern**: Multi-framework scoring system.
- Phase 1: Parse inputs (extract role, must-haves, LP emphasis)
- Phase 2: SMART audit (check each resume bullet)
- Phase 3: LP signal detection (scan for evidence of principles)
- Phase 4: LP scoring (0–3 per principle)
- Phase 5: Section-by-section feedback
- Phase 6: Verdict (advance / reject / judgment call)

Key lesson: Scoring frameworks need clear decision rules upfront. Don't improvise at the end.

## External Resources

For everything else, refer to the authoritative sources:

- **AgentSkills Specification**: https://agentskills.io/specification
- **Authorship Guide**: https://agentskills.io/guide
- **Skill Creator Tool**: Use `/skill-creator` in Claude Code or Claude app

These are the source of truth. They update faster than this repo can.

## Available Commands

```bash
make validate file=.agents/skills/my-skill/SKILL.md  # Check constraints
```

To create a new skill, use the `/skill-creator` skill, which follows the authoritative AgentSkills process.
