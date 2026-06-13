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

This saves agents from [decision paralysis](https://en.wikipedia.org/wiki/Overchoice) and [decision fatigue](https://en.wikipedia.org/wiki/Decision_fatigue).

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

This prevents accidental commits, secret leaks, or bad merges. Related to [fail-safe](https://en.wikipedia.org/wiki/Fail-safe) and [human-in-the-loop](https://en.wikipedia.org/wiki/Human-in-the-loop) design patterns.

### Moderate detail is your target

Too little: "Write good code" is not actionable.
Too much: 40 sections with every edge case is overwhelming (see [cognitive load theory](https://en.wikipedia.org/wiki/Cognitive_load)).

Target: 5–8 distinct sections. One section per major decision point.

## Skill Creation: Three-Pass Approach

Create skills using this three-pass process (in priority order: Mario's philosophy overrides external specs overrides skill-creator defaults):

### Pass 1: Use /skill-creator (foundation)
Run the `/skill-creator` skill in Claude Code or Claude app. It handles:
- Skill scaffolding (directory, SKILL.md)
- YAML frontmatter validation
- Basic instruction structure

### Pass 2: Apply External Specs (standards)
Once the skill-creator creates the skeleton, enhance it using:
- [AgentSkills Specification](https://agentskills.io/specification) — YAML fields, [progressive disclosure](https://en.wikipedia.org/wiki/Progressive_disclosure)
- [Authorship Guide](https://agentskills.io/guide) — Best practices from the community

### Pass 3: Apply Mario's Philosophy (customization)
Layer on Mario's approach:
1. **Use [Amazon's Working Backwards](https://www.amazon.jobs/en/landing_pages/working-backwards)** — Ask clarifying questions. Understand the real problem.
2. **Craft the description** — Imperative, specific, under 1024 characters.
3. **Map use cases** — Identify 3–5 scenarios where the skill applies.
4. **Write procedures** — Favor *how to do X* over *what X produces*.
5. **Build validation gates** — Ask before executing autonomous operations.
6. **Document gotchas** — Edge cases, fragile operations, surprises.
7. **Validate and iterate** — Run through with a test user.
8. **Create a PR** — Clear use cases in description.

**Tension is healthy:** These three passes may conflict. Resolve conflicts favoring Mario's philosophy (bottom of this list).

## The Skills in This Repository

| Skill | Pattern | Key Lesson |
|-------|---------|-----------|
| **code-review** | Multi-lens review with severity tiers | Lenses (correctness → simplicity → testability → readability) applied in priority order to avoid scope creep |
| **dev-workflow** | Six-phase feature dev with hard constraints | Run baseline tests first; design gate blocks implementation; self-review posts trade-offs |
| **pump-to-obsidian** | Autonomous GitHub ops with approval gates | Approval in phase 2 authorizes both content *and* auto-merge; don't skip gates |
| **resume-review** | [Amazon LP](https://www.amazon.jobs/en/principles) + [Canva Values](https://www.canva.com/careers/) scoring | Clear decision rules upfront (0–3 per principle); don't improvise at the end |

See the skill files in `.agents/skills/*/SKILL.md` for full details and implementation patterns.

## External Resources

For everything else, refer to the authoritative sources:

- **AgentSkills Specification**: https://agentskills.io/specification
- **Authorship Guide**: https://agentskills.io/guide
- **Skill Creator Tool**: Use `/skill-creator` in Claude Code or Claude app

These are the source of truth. They update faster than this repo can.
