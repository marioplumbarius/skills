# skills

A library of agent skills distilled from Mario's mental models, values, and approach to thinking and problem-solving.

Skills live under `.agents/skills/<name>/SKILL.md`. A `skills` symlink and the `.claude-plugin/` manifests expose them to Claude Code's plugin loader.

## Install in Claude Code (CLI + web)

This repo is a Claude Code plugin marketplace. Install it from any Claude Code session:

```bash
/plugin marketplace add marioplumbarius/skills
/plugin install mario-skills@marioplumbarius
```

The skills then appear namespaced: `/mario-skills:mario-code-review`, `/mario-skills:mario-dev-workflow`, etc. Works in Claude Code on the web too — cloud sessions fetch from GitHub. No version is pinned, so every commit auto-refreshes for installed users.

## Install in Claude app (claude.ai / Desktop)

Package a skill and upload it under **Settings → Capabilities → Skills → Upload skill**:

```bash
( cd .agents/skills && zip -r ../../<name>.zip <name> )
```

Note: skills that rely on `gh`, git, or the GitHub MCP won't run fully in the app, but will load.

## Creating Skills

Use the `/skill-creator` skill in Claude Code to create new skills. It follows the [AgentSkills specification](https://agentskills.io/specification).

For Mario's skill creation philosophy, see [AGENTS.md](AGENTS.md).

## Examples in This Repo

- **`mario-code-review`** — Severity-tiered PR review with multi-lens analysis
- **`mario-dev-workflow`** — Six-phase feature development with design gates
- **`mario-pump-to-obsidian`** — Autonomous GitHub operations with approval gates
- **`mario-resume-review`** — Multi-framework hiring scorecard

Study these for patterns.

## References

- [AGENTS.md](AGENTS.md) — Mario's skill philosophy, principles, and three-pass workflow
- [RATIONALE.md](RATIONALE.md) — Why these principles work (grounded in experience)
- [DECISIONS.md](DECISIONS.md) — Why the repo is structured this way
- [AgentSkills Specification](https://agentskills.io/specification) — The standard
- [Authorship Guide](https://agentskills.io/guide) — How to build skills
