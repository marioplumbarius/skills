# Contributing Skills

This is a personal skills repository. You're welcome to fork, study, and adapt these skills for your own use. The main branch is protected and only Mario can merge.

## Quick Start: Create a New Skill

### 1. Generate the skill file

```bash
make generate name=my-skill
```

This creates `.agents/skills/my-skill/SKILL.md` with a spec-compliant template.

### 2. Edit the skill

Open `.agents/skills/my-skill/SKILL.md` and:
1. Replace `<name>`, `<description>`, and `<Title>` with your skill details
2. Write clear, imperative instructions
3. Include a "Gotchas" section for edge cases
4. Use phases/checklists if the workflow is multi-step

**Refer to [CLAUDE.md](CLAUDE.md)** for detailed authorship guidance, best practices, and patterns.

### 3. Validate

```bash
make validate file=.agents/skills/my-skill/SKILL.md
```

This checks:
- YAML frontmatter is valid
- Description is ≤ 1024 characters
- File is ≤ 500 lines
- Estimated tokens < 5000

If validation fails, see the troubleshooting section in [CLAUDE.md](CLAUDE.md).

### 4. Test your skill

If you have Claude Code or the Claude app installed:

**Claude Code (CLI):**
```bash
/plugin install --local .
/my-skill
```

**Claude app (web/desktop):**
1. Go to Settings → Capabilities → Skills → Upload skill
2. Zip the skill directory: `( cd .agents/skills && zip -r ../../my-skill.zip my-skill )`
3. Upload the zip file

### 5. Commit and push

```bash
git checkout -b skill/my-skill
git add .agents/skills/my-skill/
git commit -m "Add skill: my-skill"
git push -u origin skill/my-skill
```

Then open a pull request. Include:
- What problem the skill solves
- 2-3 example use cases
- Any special setup required

---

## Project Structure

```
.
├── CLAUDE.md                # ← Read this for authorship guidance
├── AGENTS.md                # Historical workflow notes (reference only)
├── README.md                # Installation and plugin info
├── SKILL.template.md        # Template for new skills
├── Makefile                 # `make generate`, `make validate`, `make help`
├── .agents/skills/          # All skills live here
│   ├── code-review/         # Example: structured code review with severity tiers
│   ├── dev-workflow/        # Example: end-to-end feature development
│   ├── pump-to-obsidian/    # Example: autonomous GitHub operations with approval gates
│   └── resume-review/       # Example: multi-framework scoring system
├── .claude-plugin/
│   ├── plugin.json          # Claude Code plugin metadata
│   └── marketplace.json     # Marketplace manifest
└── skills/                  # Symlink to .agents/skills (for plugin discovery)
```

---

## Study the Examples

Each skill demonstrates different patterns:

- **`code-review`** — Severity-tiered feedback, multi-lens review
- **`dev-workflow`** — Multi-phase with hard constraints and design documents
- **`pump-to-obsidian`** — Autonomous PR operations with explicit approval gates
- **`resume-review`** — Scoring frameworks and structured decision logic

Read their SKILL.md files for inspiration.

---

## Need Help?

1. **How to structure a skill?** → See [CLAUDE.md](CLAUDE.md)
2. **Why is validation failing?** → Run `make validate file=<path>` and check [CLAUDE.md#troubleshooting](CLAUDE.md#troubleshooting)
3. **How do I reference other files?** → Use relative paths: `[reference](references/REFERENCE.md)` or list scripts in instructions
4. **Can I add scripts, templates, or assets?** → Yes! Use `references/`, `scripts/`, `assets/` directories. See [CLAUDE.md#file-structure-best-practices](CLAUDE.md#file-structure-best-practices)

---

## License

All skills in this repository are licensed under MIT unless otherwise noted in the skill's frontmatter.
