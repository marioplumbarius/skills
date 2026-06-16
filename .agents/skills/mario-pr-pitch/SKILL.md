---
name: mario-pr-pitch
description: >-
  Write a pull request title and description that communicate *why* the change
  exists, not what files changed or how the code works. Use whenever the user
  asks to write, draft, or improve a PR title, description, or body — even if
  they say "write the PR", "draft PR copy", "help me write the PR description",
  or just "PR title please". Also use when the user is about to open a PR and
  hasn't written the copy yet. Read the git diff automatically if no context is
  provided.
compatibility: Requires git. Uses `git diff` and `git log` to gather context when not provided.
metadata:
  author: mario
  version: "1.0"
  category: git-workflow
---

# PR Writer

Write the title and description for a pull request. Short, to the point, grounded in *why* — not what files changed or how the implementation works.

---

## The rule

**Title** — one short sentence answering: *Why does this PR exist?* Imperative voice. No implementation details.

**Description** — a short paragraph (or a few bullets if the why has multiple dimensions) answering: *What problem does this solve, and why now?* The reviewer can read the diff. Don't re-explain it.

---

## Step 1: Gather context

If the user hasn't provided a summary, run:

```bash
git diff main...HEAD --stat
git log main...HEAD --oneline
```

Read the diff output. Your goal is to understand *intent*, not catalog changes. Ask yourself:
- What was broken or missing before this?
- What user pain or business need drives this?
- Why was this the right moment to make this change?

If intent is genuinely ambiguous from the diff alone, ask the user one focused question: "What problem were you solving?"

---

## Step 2: Write the title

The title is the *why* in one imperative sentence. It describes the motivation or outcome, not the mechanism.

**Good titles** (outcome or motivation):
- `Allow users to delete their account`
- `Fix silent logout when auth token expires`
- `Speed up cold start by deferring config load`
- `Stop double-charging when payment retries`

**Bad titles** (mechanism or what):
- `Add delete account endpoint`
- `Refactor token refresh logic`
- `Lazy-load config on startup`
- `Fix payment retry bug`

The test: if someone reads only the title, do they understand the *value* of the change? If they need to look at the diff to understand why it matters, rewrite it.

Keep it under 72 characters. No period at the end.

---

## Step 3: Write the description

Use the SAR model — **Situation, Action, Result** — with markdown headers. The T (Task) is the PR itself; skip it.

```markdown
## Situation
<What was broken, missing, or painful before this change? One or two sentences grounded in user or business impact — not code state.>

## Action
<What did this PR do to address it? One sentence. Describe the approach at the intent level, not the implementation level. The reviewer has the diff.>

## Result
<What is now true that wasn't before? Focus on observable outcome — user experience, reliability, performance, developer velocity.>
```

Keep each section to 1–2 sentences. If a section has nothing real to say, fold it into an adjacent one rather than writing filler.

**Good example:**
```markdown
## Situation
Users hitting our 2MB profile picture limit were getting a generic failure with no explanation — the limit was never documented, so they had no idea what went wrong or how to fix it.

## Action
Added a clear error message that names the limit and links to our image compression docs.

## Result
Users can now resolve the issue themselves without filing a support ticket.
```

**Bad example** (narrates implementation instead of impact):
```markdown
## Situation
The upload handler in `storage/profile.ts` returned a 413 without a body.

## Action
Added a new `FileSizeError` class and updated the catch block to return a JSON response with `message` and `docsUrl` fields.

## Result
The response body now contains `{ error: "File too large", docsUrl: "..." }`.
```

---

## Output format

Present the result cleanly, ready to paste:

```
**Title:**
<title here>

**Description:**

## Situation
<one or two sentences>

## Action
<one sentence>

## Result
<one or two sentences>
```

If the user wants to iterate, rewrite the specific section they flag — don't regenerate everything unless they ask.

---

## Gotchas

- **Merge commits and rebases obscure intent** — if `git log` is noisy, focus on `git diff --stat` and ask the user if the commit messages don't tell a clear story.
- **Refactors are hard** — if the change is "pure cleanup with no behavior change," the why is "make future changes easier" or "reduce incident surface" — say that explicitly, don't pretend it's invisible.
- **Large PRs** — if the diff is enormous, scope the description to the single most important *why*. One clear sentence beats a sprawling list.
- **Don't over-ask** — the diff usually contains enough signal. Only ask the user when the why is genuinely unknowable from the code.
