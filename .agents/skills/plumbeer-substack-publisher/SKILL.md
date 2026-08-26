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
  session. Targets the user's own Substack publication only. Draft-only:
  never publishes or emails subscribers.
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

If either is missing, walk the user through [references/setup.md](references/setup.md)
**before** doing anything else. Do not ask the user to paste the cookie value
directly into the chat — have them save it straight into
`~/.config/plumbeer/substack/cookies.json` themselves (or paste it into a
file you write, then treat that value as sensitive: never echo it back, never
put it in a commit, never log it).

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

## Phase 3 — Present plan (GATE: approval)

Before calling any Substack API, show the user:

1. **Target publication** (URL) and which cookie file will be used.
2. **Title, subtitle, tags, cover image** (if any).
3. **Full body content** (or the drafted piece, if you wrote it) so they see
   exactly what will be posted.
4. **What you'll do now**: create a *draft* only. This skill has no
   publish/go-live capability — make that explicit so the user knows they'll
   need to open the draft in Substack and publish it themselves when ready.

Wait for explicit approval. Revise and re-present on request. Do not proceed
to Phase 4 until approved — draft creation still writes to the user's real
Substack account and is covered by the "publishing/modifying public content"
permission rule even though the draft itself is private.

## Phase 4 — Create draft

Use `python-substack` (`pip install python-substack` if not already
installed — ask before installing new packages if the environment is
unusual). See [references/api-usage.md](references/api-usage.md) for the
exact call pattern (`create_draft_from_markdown`, image upload handling,
error cases).

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
- **Expired/invalid cookie** shows up as 401/403. Don't try to "fix" auth by
  guessing header formats — tell the user their cookie likely expired and
  point them back to [references/setup.md](references/setup.md) to refresh it.
- **Cover images**: local file paths need uploading to Substack's asset host
  before they can be referenced in the draft body — handled by
  `create_draft_from_markdown(..., api=api)`; don't hand it a bare local path
  without the `api` argument or the image silently won't attach.
