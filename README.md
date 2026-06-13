# skills

A library of agent skills built on Mario's philosophy: grounded in expertise, prescriptive when it matters, and designed for clarity and coherence.

For Mario's approach to skill creation, see [AGENTS.md](AGENTS.md).

## Install

The plugin is available in the Claude Code marketplace.

**Step 1:** Install from marketplace:

```bash
/plugin install mario-skills
```

**Step 2:** Use any skill:

```bash
/mario-skills:skill-name
```

The plugin auto-updates with every release.

## Use in Claude app (claude.ai / Desktop)

Go to **Settings → Capabilities → Skills** to upload individual skills if needed.

Note: Some skills require external tools (git, GitHub CLI, GitHub MCP) and may have limited functionality in the app.

## Create new skills

Use `skill-creator` to build skills following Mario's philosophy: grounded expertise, prescriptive instructions, validation gates, and clear patterns.

The skill creator guides you through four steps aligned with the AgentSkills specification and tested best practices.

After installation, invoke it as `/mario-skills:skill-creator`.

## Contribute

See [AGENTS.md](AGENTS.md) for the available actions and how the system works.
