# skills

A library of agent skills built on Mario's philosophy: grounded in expertise, prescriptive when it matters, and designed for clarity and coherence.

For Mario's approach to skill creation, see [AGENTS.md](AGENTS.md).

## Install

The plugin is available in the Claude Code marketplace.

**Step 1:** Install from marketplace:

```bash
/plugin install marioplumbarius/skills
```

**Step 2:** Use any skill:

```bash
/marioplumbarius/skills:skill-name
```

The plugin auto-updates with every release.

## Use in Claude app (claude.ai / Desktop)

Go to **Settings → Capabilities → Skills** to upload individual skills if needed.

Note: Some skills require external tools (git, GitHub CLI, GitHub MCP) and may have limited functionality in the app.

## Create or update skills

Use `.agents/skills/skill-creator` from this repo to build or update skills following Mario's philosophy.
