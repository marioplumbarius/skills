# Mario's Skills Philosophy

This is a playbook for creating skills in Mario's style. It captures lessons from building skills for code review, development workflows, autonomous operations, and hiring decisions.

---

## Step 1: Start with /skill-creator (Foundation)

Run the `/skill-creator` skill in Claude Code or Claude app. It handles:
- Skill scaffolding (directory, SKILL.md)
- YAML frontmatter validation
- Basic instruction structure

Don't skip this step. The scaffolding matters.

---

## Step 2: Apply External Specs (Standards)

Once the skill-creator creates the skeleton, enhance it using:
- [AgentSkills Specification](https://agentskills.io/specification) — YAML fields, progressive disclosure patterns
- [Authorship Guide](https://agentskills.io/guide) — Best practices from the community

Study existing skills in `.agents/skills/*/SKILL.md` for patterns.

---

## Step 3: Apply Mario's Philosophy (Customization)

Layer on Mario's approach. These principles shape how to write instructions:

### Principle 1: Ground in expertise, not hypotheticals

Every skill should reflect *actual* patterns you've solved repeatedly. If writing a code-review skill, you have strong opinions about code quality. If building a resume-review skill, you've screened hundreds of resumes.

**Don't write skills for one-off tasks or theoretical problems.**

### Principle 2: Be prescriptive when fragility matters

```markdown
❌ Bad:   "You can use either approach"
✅ Good:  "Always use approach X because [reason].
          Fallback to Y only if [conditions]."
```

When operations are fragile, consistency matters, or a specific sequence is essential—be explicit about *why*.

### Principle 3: Favor defaults, not menus

When multiple tools or approaches work:
- Pick one as the default
- Explain why it's the best choice
- Mention alternatives briefly

This prevents choice paralysis and overwhelm.

### Principle 4: Design coherent units

A skill solves a *class* of problems, not a one-off task:
- ✅ "Code review" (applies to any PR)
- ✅ "End-to-end feature development" (applies to any non-trivial change)
- ❌ "Review my PR from yesterday" (one-off)
- ❌ "Fix this specific bug" (one-off)

**Test**: Can you describe the skill in one sentence? If not, it may be incoherent.

### Principle 5: Validation loops protect against mistakes

For autonomous operations (PR merges, file writes, commits):

```markdown
1. Present the plan to the user:
   - [What you decided]
   - [What will change]
2. Ask: "Proceed?"
3. Only execute after explicit approval
```

This prevents accidental commits, secret leaks, or bad merges.

### Principle 6: Moderate detail is your target

Too little: "Write good code" is not actionable.
Too much: 40 sections with every edge case is overwhelming.

Target: 5–8 distinct sections. One section per major decision point.

---

## Skill Creation: Three-Pass Approach

---

## Step 4: Craft the Skill Content

Once you've applied Steps 1–3, write the skill instruction with these substeps:

1. **Use [Amazon's Working Backwards](https://www.amazon.jobs/en/landing_pages/working-backwards)** — Ask clarifying questions. Understand the real problem. Don't assume.

2. **Craft the description** — Imperative phrasing, specific, under 1024 characters. Frame it as an instruction to the agent: "Use this when…"

3. **Map use cases** — Identify 3–5 real scenarios where the skill applies. Include edge cases and non-obvious contexts.

4. **Write procedures** — Favor *how to do X* over *what X produces*. Be prescriptive at fragile points (file writes, merges, deletions).

5. **Build validation gates** — For autonomous operations, always ask before executing: "Proceed?" is not optional.

6. **Document gotchas** — Edge cases, fragile operations, surprises. If an operation can break silently, call it out.

7. **Validate and iterate** — Run through with a test user. Watch for confusion.

8. **Create a PR** — Clear use cases in description. Link to why this skill matters.

---

## Tension Between Frameworks

The three frameworks (skill-creator → external specs → Mario's philosophy) may conflict. Resolve in priority order:

1. **Mario's philosophy** (top priority)
2. **External specs**
3. **Skill-creator defaults**

This friction is healthy. You're optimizing for how Mario himself would perform the task.

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
