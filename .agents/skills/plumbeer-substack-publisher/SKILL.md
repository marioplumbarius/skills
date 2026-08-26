---
name: plumbeer-substack-publisher
description: >-
  Create a Substack draft from markdown/prose — draft only, never publishes
  or goes live. Use when the user says "draft this on Substack", "put this
  article in my Substack drafts", "send this as a Substack draft", or hands
  over a piece of writing (or asks you to write one) and wants it staged on
  their Substack publication for them to review and publish themselves.
  Substack has no official publish API, so this uses the unofficial
  cookie-authenticated API via the `python-substack` library, calling only
  its draft-creation endpoint. Requires a one-time local cookie setup (never
  committed to git). This skill has no publish/go-live capability by design —
  it cannot make a post public or email subscribers under any circumstance.
compatibility: >-
  Requires Python 3 and pip (to install `python-substack`). Requires a local,
  non-repo cookies file exported from an authenticated Substack browser
  session — scripts/extract_firefox_cookie.py automates this on macOS with
  Firefox installed (Phase 1 checks both before offering it); other
  platforms/browsers use the manual steps in references/setup.md. Targets
  the user's own Substack publication only.
  Draft-only: never publishes or emails subscribers.
metadata:
  author: plumbeer
  version: "1.0"
  category: publishing
---

# Substack Publisher

Turn a piece of writing into a Substack **draft**. Substack has no official
public API; this relies on the unofficial, reverse-engineered API
(`python-substack`), authenticated with the user's own session cookie. That
cookie is a real credential: it never gets committed, logged, or printed in
full.

**This skill only ever creates drafts.** It never calls a publish/go-live
endpoint, never sends subscriber emails, and never makes anything public. If
the user asks to publish, go live, or send the post, tell them the skill is
draft-only by design and that they need to hit publish themselves in the
Substack editor.

```
- [ ] Phase 1: Confirm credentials & publication config
- [ ] Phase 2: Prepare the article
- [ ] Editing rules: apply before presenting the plan
- [ ] Phase 3: Present plan (GATE: approval)
- [ ] Phase 4: Create draft
```

## Phase 1 — Confirm credentials & publication config

This skill needs two things that must never live in the repo:

1. **Publication URL**, e.g. `https://example.substack.com`.
2. **Session cookie** (`substack.sid`), exported from a browser where the
   user is already logged into Substack.

Check for an existing local config at `~/.config/plumbeer/substack/`:
- `cookies.json` — a JSON object with at least `substack.sid`.
- `config.json` — `{"publication_url": "https://example.substack.com"}`.

If `cookies.json` is missing, check whether
[scripts/extract_firefox_cookie.py](scripts/extract_firefox_cookie.py) is
even applicable **before** offering it — the script assumes its
prerequisites are already met and does not re-check them:

1. **Platform**: run `uname -s` and confirm it prints `Darwin` (macOS).
2. **Firefox installed**: confirm it exists, e.g.
   `test -d "/Applications/Firefox.app" -o -d "$HOME/Applications/Firefox.app"`.

If either check fails, do not offer or run the script — go straight to the
manual path in [references/setup.md](references/setup.md). This skill's job
is to read an existing Firefox profile, not to install Firefox or guess at
another OS's/browser's cookie store, so don't try to work around a failed
check.

If both checks pass, offer to run the script — it copies the local
`cookies.sqlite` (so it works even with Firefox open), pulls the
`substack.sid` value, and writes it straight to
`~/.config/plumbeer/substack/cookies.json` with `chmod 600`, without ever
printing the value. This still reaches into the user's browser profile, so
**ask before running it each time** — don't run it silently just because it
exists and the checks passed. If the user declines, walk them through the
manual path in [references/setup.md](references/setup.md) instead.

Either way, never ask the user to paste the cookie value directly into the
chat: it comes from the script, or the user saves it into
`~/.config/plumbeer/substack/cookies.json` themselves. Treat it as sensitive
regardless of source — never echo it back, never put it in a commit, never
log it.

Verify `~/.config/plumbeer/substack/` is outside this git repo. If the user
insists on keeping config inside the repo working directory for some reason,
confirm a `.gitignore` entry exists for it before writing anything there.

## Phase 2 — Prepare the article

Gather or draft:
- **Title** (required).
- **Subtitle** (optional but recommended — shows in previews/emails).
- **Body**, as markdown. If the user hands you raw notes or asks you to write
  the piece, draft it first and show it to them as part of the Phase 3 plan —
  don't fold drafting approval into the publish approval.
- **Cover image** (optional): a local file path or URL.
- **Tags/section** (optional).

If the user already has a finished piece (file, doc, previous chat output),
use it verbatim — don't rewrite content that wasn't asked to be rewritten.

## Editing rules

Apply these mechanical transformations to the body before presenting it in
Phase 3, and again after any revision the user requests. They are
formatting fixes, not content rewrites — they don't conflict with "use it
verbatim" in Phase 2, which is about not rewriting the substance.

1. **Italicize quoted text.** Wrap text between double quotes in italics,
   quotes included: `"text"` → `*"text"*`. Apply this even when the quote
   sits inside a link label (e.g. `["text"](url)` → `[*"text"*](url)`).

## Phase 3 — Present plan (GATE: approval)

Before calling any Substack API, present the draft as a structured, labeled
block so the user can propose inline revisions against specific parts of it
rather than the whole thing at once. Use this exact shape:

```
**Title:** <title>

**Subtitle:** <subtitle, or "(none)">

**Tags:** <tag1, tag2, ... or "(none)">

**Cover image:** <path/URL, or "(none)">

**Body:**
<full body content, fenced as its own block, verbatim — this is what gets
posted, so no placeholders or "..." truncation>
```

Follow it with:
- **Target publication** (URL) and which cookie file will be used.
- **What happens next**: creating a *draft* only. This skill has no
  publish/go-live capability — say so explicitly, so the user knows they'll
  need to open the draft in Substack and publish it themselves when ready.
- An explicit prompt to either approve or point at what to change (e.g. "say
  which part to revise, or reply 'proceed' to create the draft").

This is not the harness's code-implementation Plan Mode (`EnterPlanMode` /
`ExitPlanMode`) — that tool is scoped to planning code changes and explicitly
says not to use it for content/research tasks, so don't invoke it here. The
structured block above is a plain chat presentation, not a formal plan-mode
session.

Wait for explicit approval. On a revision request, apply it and re-present
the full block again (not just the changed piece) so the user is always
confirming the complete, current draft. Do not proceed to Phase 4 until
approved — draft creation still writes to the user's real Substack account
and is covered by the "publishing/modifying public content" permission rule
even though the draft itself is private.

## Phase 4 — Create draft

Use `python-substack` (`pip install python-substack` if not already
installed — ask before installing new packages if the environment is
unusual; on Homebrew Python this needs a venv, see Gotchas). See
[references/api-usage.md](references/api-usage.md) for the exact call
pattern (`create_draft_from_markdown`, image upload handling, error cases).

Run it, then report back:
- Draft ID and the draft edit URL (`{publication_url}/publish/post/{id}`).
- A reminder that this is the end of what the skill does: the draft sits in
  Substack until the user opens it and publishes it themselves.

If the API call fails (expired cookie, 401/403, schema change in the
unofficial API), stop and report the raw error — don't retry blindly or fall
back to guessing a different endpoint. See Gotchas below.

## Gotchas

- **No official API.** Everything here rides on reverse-engineered endpoints.
  Substack can change them without notice — if a call starts failing with
  unexpected shapes (not just auth errors), say so plainly instead of
  patching around it silently.
- **Cookie = full account access.** Treat `substack.sid` like a password:
  never print it, log it, put it in a commit, or send it anywhere other than
  Substack's own API host.
- **Draft creation still touches the real account.** It's not "free" just
  because it's private — it still needs the Phase 3 gate.
- **No publish path, ever.** Never call `publish_draft`, any "send"/"email"
  endpoint, or otherwise try to make a post public or notify subscribers —
  not even if the user insists or says they'll take responsibility. Tell
  them to publish from the Substack editor themselves.
- **Homebrew Python blocks global pip installs** (PEP 668). If
  `pip install python-substack` fails with an "externally-managed-environment"
  error, create a venv instead (e.g.
  `python3 -m venv ~/.config/plumbeer/substack/venv && ~/.config/plumbeer/substack/venv/bin/pip install python-substack`)
  and use that interpreter for every subsequent Python call in this skill —
  don't reach for `--break-system-packages`.
- **The cookie-extraction script only covers macOS + Firefox, and doesn't
  check that itself.** Phase 1's `uname -s` / Firefox.app checks are what
  gate it — run those first, every time, before offering the script. Don't
  invoke it on an unchecked platform and let it fail, and don't try to
  install Firefox or guess at another OS's/browser's cookie store if the
  checks fail; fall back to the manual DevTools steps in
  [references/setup.md](references/setup.md) instead. Re-running the script
  is safe (it overwrites `cookies.json`) but still ask first each time —
  it's reading live browser data.
- **Expired/invalid cookie** shows up as 401/403. Don't try to "fix" auth by
  guessing header formats — tell the user their cookie likely expired and
  point them back to [references/setup.md](references/setup.md) to refresh it.
- **Cover images**: local file paths need uploading to Substack's asset host
  before they can be referenced in the draft body — handled by
  `create_draft_from_markdown(..., api=api)`; don't hand it a bare local path
  without the `api` argument or the image silently won't attach.
