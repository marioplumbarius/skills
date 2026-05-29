# skills

A library of agent skills distilled from Mario's mental models, values, and approach to thinking and problem-solving.

Skills live under `.agents/skills/<name>/SKILL.md`. A `skills` symlink and the
`.claude-plugin/` manifests expose them to Claude Code's plugin loader without
moving them out of `.agents/skills/`.

## Use the skills in Claude Code (CLI + web)

This repo is a Claude Code plugin marketplace. Install it from any Claude Code
session:

```bash
/plugin marketplace add marioplumbarius/skills
/plugin install mario-skills@marioplumbarius
```

The skills then appear namespaced, e.g. `/mario-skills:pump-to-obsidian`,
`/mario-skills:code-review`. Works in Claude Code on the web too — cloud
sessions fetch the marketplace from GitHub. No version is pinned in
`plugin.json`, so every pushed commit auto-refreshes for installed users.

> The `skills` entry is a git symlink to `.agents/skills`. Symlinked plugin
> skill dirs can be flaky on some hosts (notably Windows). If discovery fails,
> migrate `.agents/skills/*` to a real `skills/` directory.

## Use the skills in the Claude app (claude.ai / Desktop)

The Claude app uses a separate, upload-based system — it can't pull from
GitHub. Package a skill and upload it under **Settings → Capabilities →
Skills → Upload skill**:

```bash
# from repo root, zip one skill so the archive holds <name>/SKILL.md
( cd .agents/skills && zip -r ../../<name>.zip <name> )
```

Note: skills that rely on `gh`, git, or the GitHub MCP (`code-review`,
`dev-workflow`, `pump-to-obsidian`) load in the app but their GitHub/PR steps
won't run there.

## Available Commands
```bash
make help
```