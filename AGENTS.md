# AGENTS

For Mario's comprehensive skill creation guide, use the `/mario-skill-creator` skill in Claude Code or Claude app.

This skill walks you through:
1. **Step 1**: Start with /skill-creator (foundation)
2. **Step 2**: Apply external specs (standards)
3. **Step 3**: Apply Mario's philosophy (customization)
4. **Step 4**: Craft the skill content

Or read the full guide in [`.agents/skills/mario-skill-creator/SKILL.md`](.agents/skills/mario-skill-creator/SKILL.md).

## The Skills in This Repository

| Skill | Pattern | Key Lesson |
|-------|---------|-----------|
| **/mario-code-review** | Multi-lens review with severity tiers | Lenses (correctness → simplicity → testability → readability) applied in priority order to avoid scope creep |
| **/mario-dev-workflow** | Six-phase feature dev with hard constraints | Run baseline tests first; design gate blocks implementation; self-review posts trade-offs |
| **/mario-pump-to-obsidian** | Autonomous GitHub ops with approval gates | Approval in phase 2 authorizes both content *and* auto-merge; don't skip gates |
| **/mario-resume-review** | [Amazon LP](https://www.amazon.jobs/en/principles) + [Canva Values](https://www.canva.com/careers/) scoring | Clear decision rules upfront (0–3 per principle); don't improvise at the end |

See the skill files in `.agents/skills/mario-*/SKILL.md` for full details and implementation patterns.
