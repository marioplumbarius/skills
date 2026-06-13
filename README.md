# skills

A library of agent skills built on Mario's philosophy: grounded in expertise, prescriptive when it matters, and designed for clarity and coherence.

For Mario's approach to skill creation, see [AGENTS.md](AGENTS.md).

## Install in Claude Code (CLI + web)

**Step 1:** Add the marketplace:

```bash
/plugin marketplace add marioplumbarius/skills
```

**Step 2:** Install the plugin:

```bash
/plugin install mario-skills@marioplumbarius
```

Skills will appear as `/mario-skills:skill-name`. The plugin auto-updates with every commit.

## Install in Claude app (claude.ai / Desktop)

**Step 1:** Package a skill:

```bash
( cd .agents/skills && zip -r ../../<skill-name>.zip <skill-name> )
```

**Step 2:** Upload under **Settings → Capabilities → Skills → Upload skill**

Note: Some skills require external tools (git, GitHub CLI, GitHub MCP) and may have limited functionality in the app.

## Create new skills

Use `skill-creator` to build skills following Mario's philosophy: grounded expertise, prescriptive instructions, validation gates, and clear patterns.

The skill creator guides you through four steps aligned with the AgentSkills specification and tested best practices.

After installation, invoke it as `/mario-skills:skill-creator`.

## Contribute

See [AGENTS.md](AGENTS.md) for the available actions and how the system works.
