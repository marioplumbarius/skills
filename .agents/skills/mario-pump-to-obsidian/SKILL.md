---
name: mario-pump-to-obsidian
description: "Capture session context as an Obsidian note and push it via PR. Use when the user says 'pump to obsidian' or 'save to my vault'. Shows plan for approval before auto-merge."
disable-model-invocation: true
---

# Pump to Obsidian

Distill the current session into a clean Obsidian note and land it in the
vault via a pull request. Plan first, get approval, open the PR, auto-merge.

**Default target repo:** `marioplumbarius/obsidian`
**Default destination:** `Inbox/` folder, one dated note per run.

Work through the phases in order. Do not skip a phase or pass a gate without
meeting its condition.

```
- [ ] Phase 1: Gather context
- [ ] Phase 2: Draft note + present plan (GATE: approval)
- [ ] Phase 3: Open PR
- [ ] Phase 4: Auto-merge + report
```

## Phase 1 — Gather context

Pull from **this session's** conversation and tool history. Do not invent
content — only capture what actually happened or was discussed. Default scope:

- **Decisions & insights** — key conclusions, takeaways, choices made and the
  reasoning behind them.
- **Code & commands** — relevant snippets, commands run, and file changes worth
  remembering. Keep them runnable; fence with the right language.
- **Open questions / TODOs** — unresolved threads and follow-up actions.

Skip the full verbatim transcript unless the user explicitly asks for it.

If the session is long or covers several topics, ask the user whether to scope
the note to a specific topic before drafting.

## Phase 2 — Draft note + present plan

Build the note in memory, then show the user a **plan** before touching the
repo. The plan must state:

1. **Target**: repo (`marioplumbarius/obsidian`), branch name, and file path.
2. **Filename**: `Inbox/YYYY-MM-DD-<kebab-slug>.md` using today's date and a
   short slug from the topic (e.g. `Inbox/2026-05-29-retry-backoff-design.md`).
   If a file with that exact path already exists, append a short disambiguator
   (`-2`, `-3`) rather than overwriting.
3. **Preview**: the full note content (frontmatter + body) so the user sees
   exactly what lands in the vault.

Use this note template:

```markdown
---
title: <human-readable title>
date: <YYYY-MM-DD>
source: <claude-code | cowork | chat>
tags: [from-claude, <topic-tags>]
---

# <title>

## Summary
<2–4 sentence distillation of what this session was about.>

## Decisions & insights
- <decision/insight + brief why>

## Code & commands
```<lang>
<snippet>
```

## Open questions / TODOs
- [ ] <follow-up>

## References
- <links, file paths, PRs, or [[wikilinks]] to related notes>
```

Drop any section that has no real content — don't ship empty headers. Prefer
Obsidian `[[wikilinks]]` for references to other vault notes when you know them.

**GATE:** Present the plan and wait for explicit approval. If the user requests
changes, revise and re-present. Do not proceed to Phase 3 until they approve.

## Phase 3 — Open PR

Operate on `marioplumbarius/obsidian` using the GitHub MCP tools (`mcp__github__*`).
If those tools are not scoped to the vault repo in this session, tell the user
and stop — do not silently fall back to a different repo.

1. Determine the repo's default branch (`mcp__github__list_branches` or repo
   metadata) — usually `main`.
2. Create a branch off the default branch:
   `mcp__github__create_branch` named `pump/YYYY-MM-DD-<slug>`.
3. Commit the note to that branch with `mcp__github__create_or_update_file`
   (single file) — path and content from the approved plan. Commit message:
   `Add note: <title>`.
4. Open the PR with `mcp__github__create_pull_request`:
   - base = default branch, head = the new branch
   - title: `Pump to Obsidian: <title>`
   - body: short summary of what the note captures + a line noting it was
     generated from a Claude session via the pump-to-obsidian skill.

Report the PR number and URL.

## Phase 4 — Auto-merge + report

Once the PR is open (approval was already granted in Phase 2):

1. Merge it with `mcp__github__merge_pull_request` (squash merge).
2. If the merge is blocked (branch protection, required checks, conflicts),
   do **not** force it — report the blocker and the PR URL so the user can
   resolve or merge manually.
3. On success, report: note path in the vault, PR URL, and merge commit.

## Gotchas

- **Vault, not code repo.** The target is the Obsidian vault
  (`marioplumbarius/obsidian`), never the repo of the current coding session.
  Confirm the GitHub tools point at the vault before writing.
- **No secrets.** Strip API keys, tokens, passwords, and private credentials
  from code/command snippets before they go into the note.
- **Faithful capture.** Record what the session actually produced. If a
  decision was tentative or a test failed, say so — don't polish it into a
  conclusion that wasn't reached.
- **One note per run** by default. If the user wants the content split or
  appended to an existing note, confirm the approach in Phase 2.
- **Approval is for the content.** The Phase 2 gate approves what gets written
  and where; that approval is what authorizes the auto-merge in Phase 4. Any
  change to scope or destination after approval needs re-confirmation.
