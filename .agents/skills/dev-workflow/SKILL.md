---
name: dev-workflow
description: >-
  End-to-end development lifecycle skill: build a High-Level Design, scope
  it into tasks, implement task by task, verify tests/types/lint, commit,
  open a PR, and self-review. Use when starting a new feature, bug fix, or
  any non-trivial change that needs a design step before coding.
compatibility: Requires git, a project test suite, type checker, and linter
  (as configured in the target repo).
metadata:
  author: mario
  version: "1.0"
  category: development
---

# Dev Workflow

## Confirmation

Before doing anything else, summarize what you understand the task to be and ask the user to confirm they want to proceed with the full dev-workflow (HLD → implement → PR). Do not start Phase 1 until the user says yes.

Follow these phases in order. Do not skip phases or proceed past a gate without meeting its condition.

## Phase 1 — Baseline

Run the project's test suite before touching any code.

- If tests fail, stop immediately and report — do not proceed.

## Phase 2 — Design

1. Checkout a new branch off the default branch (`main` or `master` — check the repo):
   ```
   git checkout -b $(whoami)/<short-description>
   ```
2. Copy `docs/HLD_TEMPLATE.md` → `docs/<doc-name>.md` and fill it in (bullet points, concise). Derive `<doc-name>` from the branch name by replacing `/` with `-` (e.g. branch `alice/add-retry-logic` → doc `docs/alice-add-retry-logic.md`).
3. Present the HLD to the user. Iterate until they explicitly approve. Do not start Phase 3 until approved.

## Phase 3 — Implement

Work through the task list in `docs/<doc-name>.md` one task at a time:

1. Implement the task.
2. Verify in order — fix failures before moving on:
   1. Tests
   2. Type checker
   3. Linter / formatter
3. Commit the code change.
4. Update `docs/<doc-name>.md`: mark the task done; note any deviations from the design and why. Commit separately.
5. If this revealed a gap in `AGENTS.md`, fix it and commit separately.
6. Move to the next task.

**Gate rules:**
- Only fix test/type/lint failures your change introduced.
- Max 3 attempts per failing check — if still failing, stop and ask for guidance.
- Never move to the next task while errors are unresolved.

When all tasks are done:
- Keep `docs/<doc-name>.md` — it is a permanent design record.
- Update the **Project structure** section in `AGENTS.md` for any new/removed files. Commit separately.

**Hard constraints:**
- Do NOT refactor existing code as part of the change.
- Do NOT bundle unrelated changes into a single commit.
- Do NOT modify tooling or config without explicit user approval — describe the change and wait for a yes.
- Do NOT add/update/remove dependencies without explicit user approval.

## Phase 4 — Pull Request

After all commits:

1. Push: `git push -u origin HEAD`
2. Resolve GitHub user: `gh api user --jq '.login'`
3. Check for existing PR: `gh pr view --json number 2>/dev/null`
   - No PR → create and assign: `gh pr create --title "..." --body "..." --assignee <login>`
   - PR exists → update body via API (avoids `gh pr edit` silent failures on some repos): `gh api repos/<owner>/<repo>/pulls/<number> --method PATCH --field body="..."` then `gh pr edit --add-assignee <login>`

**Keeping the PR description up to date:** Any time a new commit is pushed to a branch that already has an open PR, update the PR description to reflect the new changes. Do not wait until all work is done — update it after each push.

## Phase 5 — Self-Review

After the PR is open, post a review comment on it that covers:

- What trade-offs were made and why
- Any known limitations or follow-up work
- What was learned that wasn't in the original HLD

## Phase 6 — Retrospective

After the PR is merged (or when asked), update `AGENTS.md` and `docs/HLD_TEMPLATE.md` with any workflow improvements discovered during this cycle. Commit to the default branch directly (or open a separate micro-PR if the repo requires it).
