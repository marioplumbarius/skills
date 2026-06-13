# Mario’s Skills Repository — Workflow & Best Practices

This document captures Mario’s personal approach to building agent skills. It reflects lessons from creating `code-review`, `dev-workflow`, `pump-to-obsidian`, and `resume-review`.

**For the technical specification and authorship guide, see [CLAUDE.md](CLAUDE.md).**

## The Core Workflow

When building a new skill, follow this process:

1. **Use Amazon’s Working Backwards** — Ask clarifying questions. Understand the real problem, not what the user *thinks* the problem is.
2. **Craft a tight description** — Imperative, specific, under 1024 characters. This determines whether the agent even *considers* the skill.
3. **Map use cases** — Identify 3–5 scenarios where the skill applies. Identify keywords users would say.
4. **Write step-by-step instructions** — Favoring *procedures* (how to do X) over *declarations* (what X produces).
5. **Build in validation gates** — Especially for autonomous operations (PRs, file writes, network calls). Always ask before executing.
6. **Add a Gotchas section** — Document fragile operations, edge cases, and things that surprised you.
7. **Validate and iterate** — `make validate file=<path>`. Run through the skill with a test user. Revise.
8. **Commit and PR** — Branch, commit, push, open PR with clear use cases.

## Common Rules

- **Always ask before proceeding** — Especially for any operation that touches files, networks, or external systems.
- **Make small, clear commits** — One skill per commit, one change per commit if iterating.
- **Test with a real user** — Ask the user: “Does this skill do what you expected?” before calling it done.
- **If multiple ways exist, pick one** — Mention alternatives briefly. Default to the one that’s safest or most consistent with the codebase.

## Best Practices Distilled

### Ground your skill in real expertise

Effective skills come from *actual* domain knowledge. If writing a code-review skill, you need strong opinions about what constitutes good code. If building a resume-review skill, you’ve screened hundreds of resumes.

**Don’t write skills for hypotheticals.** Write them for patterns you’ve seen repeatedly.

### Be prescriptive when fragility matters

```markdown
❌ Bad:   “You can use git or gh to fetch the branch.”
✅ Good:  “Always use `gh pr diff` because it avoids local clone overhead.
          Fallback to `git diff` only if gh is not available.”
```

When operations are fragile, consistency matters, or a specific sequence is essential — be explicit about *why*.

### Add what the agent lacks, omit what it knows

The agent already knows:
- How to use Bash, Python, git
- General software engineering concepts
- How to write clear code

Teach it *your* mental model:
- Your code-review rubric (simplicity + testability + correctness)
- Your decision-making framework (Amazon LPs, SMART scoring)
- Your process (phases, gates, checklists)

### Design coherent units

A skill should solve a *class* of problems, not a one-off task. “Code review” is coherent. “Review my PR from yesterday” is not. “End-to-end feature development” is coherent. “Fix this specific bug” is not.

**Test:** Can you describe the skill in one sentence? If not, it may be too broad or incoherent.

### Aim for moderate detail

Too little: “Write good code” is not actionable.
Too much: 40 sections with every edge case is overwhelming.

Target: 5–8 distinct sections, each with a clear purpose. One section per major phase or decision point.

### Validation loops are your friend

For autonomous operations (PR merges, file writes, commits), use validation gates:

```markdown
Present the plan to the user:
- [What you decided]
- [What will change]
Then ask: “Proceed?”

Only execute after explicit approval.
```

This prevents accidental merges, secret leaks, or bad commits.

### Structure for progressive disclosure

Keep `SKILL.md` under 500 lines. Move heavy reference material to `references/REFERENCE.md`. Agents load metadata → instructions → references (on demand).

If your skill is approaching 400 lines:
1. Remove redundant examples
2. Move detailed reference to `references/`
3. Move templates to `assets/`
4. Link to them instead

### Gotchas section is mandatory

Every skill should have a “Gotchas” section documenting:
- Operations that broke things before
- Assumptions that must hold
- Common mistakes
- Surprising behaviors

**Example from `code-review`:**
- Don’t flag style issues a linter already enforces
- Tests that only mock aren’t real coverage
- If PR description is vague, flag it

**Example from `pump-to-obsidian`:**
- Never commit secrets (API keys, tokens, passwords)
- Always target the Obsidian vault, never the code repo
- Record what actually happened, not what “should have” happened

## Project Structure

```
.agents/skills/
├── code-review/SKILL.md
│   └── Multi-lens review: correctness, simplicity, testability, readability
├── dev-workflow/SKILL.md
│   └── Six-phase feature dev: baseline → design → implement → test → PR → review
├── pump-to-obsidian/SKILL.md
│   └── Autonomous: plan → PR → merge with explicit approval gates
└── resume-review/SKILL.md
    └── Scoring framework: SMART audit + LP signal detection + verdict
```

Each skill demonstrates a different pattern. Study them for inspiration.

## Available Commands

```bash
make generate name=my-skill      # Create new skill from template
make validate file=<path>         # Check lines, tokens, description length
make help                         # Show all commands
```

For quick contribution steps, see [CONTRIBUTING.md](CONTRIBUTING.md).

## References

- **AgentSkills Specification** — https://agentskills.io/specification
- **Authorship Guide** — [CLAUDE.md](CLAUDE.md) (what Claude reads)
- **Contributing** — [CONTRIBUTING.md](CONTRIBUTING.md)
- **Examples** — Study the 4 skills in `.agents/skills/`