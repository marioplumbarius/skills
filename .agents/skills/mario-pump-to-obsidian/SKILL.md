---
name: mario-pump-to-obsidian
description: >-
  Capture context from a source — the current Claude session (Claude Code,
  cowork, or chat), or a YouTube video transcribed via yt-dlp — and push it as
  a new note into Mario's Obsidian vault on GitHub (marioplumbeer/obsidian).
  Use when the user says "pump to obsidian", "save this to my vault/obsidian",
  "send this session to my notes", "pump this video to obsidian", or pastes a
  YouTube URL wanting it captured as a note. Always shows a plan for approval
  before opening a PR, then auto-merges once approved.
compatibility: >-
  Requires git, GitHub CLI (gh), and access to the GitHub MCP. Targets the
  marioplumbeer/obsidian repository; not suitable for other vaults. YouTube
  sources additionally require yt-dlp installed and on PATH.
metadata:
  author: mario
  version: "2.0"
  category: knowledge-management
---

# Pump to Obsidian

Distill a source into a clean Obsidian note and land it in the vault via a
pull request. Plan first, get approval, open the PR, auto-merge.

**Default target repo:** `marioplumbeer/obsidian`

Work through the phases in order. Do not skip a phase or pass a gate without
meeting its condition.

```
- [ ] Phase 1: Identify source + gather context
- [ ] Phase 2: Draft note + present plan (GATE: approval)
- [ ] Phase 3: Open PR
- [ ] Phase 4: Auto-merge + report
```

## Phase 1 — Identify source & gather context

Each source type is a self-contained reference file with its own gather
steps, destination rule, note template, and gotchas. Pick the matching row,
read that file in full, and follow it exactly — this file (SKILL.md) does not
duplicate that content.

| Source | When | Reference |
|---|---|---|
| Claude session (default) | No other source is named | [references/session-source.md](references/session-source.md) |
| YouTube video | User gives a YouTube URL, or asks to "pump this video" | [references/youtube-source.md](references/youtube-source.md) |

Adding a new source type later (a blog post, a PDF, a podcast feed) means
adding one row here and one new `references/<source>-source.md` file — never
grow this file inline with another source's steps.

## Phase 2 — Draft note + present plan

Using the destination rule and template from the source's reference file,
build the note in memory, then show the user a **plan** before touching the
repo. The plan must state:

1. **Target**: repo (`marioplumbeer/obsidian`), branch name, and file path.
2. **Filename**: per the source reference file's Destination section.
3. **Preview**: the full note content (frontmatter + body) so the user sees
   exactly what lands in the vault.

Before drafting, skim the vault's `README.md` and existing folder structure
(`people/`, `leadership/`, `startups/`, etc.) so filenames, folders, and tags
match its actual conventions rather than assumptions.

**GATE:** Present the plan and wait for explicit approval. If the user requests
changes, revise and re-present. Do not proceed to Phase 3 until they approve.

## Phase 3 — Open PR

Operate on `marioplumbeer/obsidian` using the GitHub MCP tools (`mcp__github__*`).
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
     generated via the mario-pump-to-obsidian skill.

Report the PR number and URL.

## Phase 4 — Auto-merge + report

Once the PR is open (approval was already granted in Phase 2):

1. Merge it with `mcp__github__merge_pull_request` (squash merge).
2. If the merge is blocked (branch protection, required checks, conflicts),
   do **not** force it — report the blocker and the PR URL so the user can
   resolve or merge manually.
3. On success, report: note path in the vault, PR URL, and merge commit.

## Gotchas

These apply regardless of source. Source-specific gotchas (transcript
handling, citation rules, etc.) live in that source's reference file.

- **Vault, not code repo.** The target is the Obsidian vault
  (`marioplumbeer/obsidian`), never the repo of the current coding session.
  Confirm the GitHub tools point at the vault before writing.
- **No secrets.** Strip API keys, tokens, passwords, and private credentials
  from code/command snippets before they go into the note.
- **Faithful capture.** Record what the source actually produced. If a
  decision was tentative or a claim was uncertain, say so — don't polish it
  into a conclusion that wasn't reached.
- **One note per run** by default. If the user wants the content split or
  appended to an existing note, confirm the approach in Phase 2.
- **Approval is for the content.** The Phase 2 gate approves what gets written
  and where; that approval is what authorizes the auto-merge in Phase 4. Any
  change to scope or destination after approval needs re-confirmation.
