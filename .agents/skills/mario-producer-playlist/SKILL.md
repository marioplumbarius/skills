---
name: mario-producer-playlist
description: >-
  Build a YouTube Music playlist made entirely of songs released by one or
  more named producers (e.g. Pharrell, Timbaland, Swizz Beatz). Use this
  when the user asks to make a playlist "produced by X", wants a crate-dig
  of a producer's catalog, or wants to combine several producers into one
  YouTube Music playlist — even if they only name the producer(s) and say
  "make me a playlist" without spelling out the pipeline. Resolves each
  name to a specific YouTube channel (disambiguating common names or
  imposters by subscriber count), then confirms the exact track list with
  the user before writing anything to their YouTube account, since
  playlist creation is a real, hard-to-reverse write.
compatibility: >-
  Requires a Google Cloud OAuth client authorized for the YouTube Data API
  v3 (scope: youtube). See references/credentials-setup.md. Uses
  scripts/build_playlist.py. No external credit database is used — YouTube
  itself is the only source of truth.
metadata:
  author: mario
  version: "2.0"
  category: music
---

# Producer Playlist Builder

Turn a list of producers into a real YouTube Music playlist of songs they released. YouTube has no "producer" field, so "produced by X" is treated as **"released under X's own YouTube artist identity"** — this is a deliberate scope narrowing, not an oversight (an earlier version of this skill cross-checked production *credits* via Genius; that dependency was dropped in favor of a YouTube-only pipeline, so a producer's own catalog — not beats they made for other artists — is what gets pulled). Say this plainly if the user seems to expect true production-credit verification.

The real work is **disambiguation**: a producer's name is ambiguous (VEVO channels, fan pages, imposters, unrelated people with the same name), and picking the wrong channel silently produces a whole playlist of the wrong thing.

---

## Step 1: Gather inputs

- **Producers** — one or more names. Required.
- **Tracks per producer** — default **10**.
- **Sort** — `recent` (default, newest release first) or `popular` (highest view count first). This is a real input, not a preset — ask if it's unclear which the user wants.

Don't guess if any of these are genuinely unclear.

---

## Step 2: Check credentials

Verify `YOUTUBE_CLIENT_SECRETS` (a Google Cloud OAuth client JSON path) is set before doing anything else. If missing, walk the user through `references/credentials-setup.md` rather than guessing a path.

---

## Step 3: One-time browser authorization

```bash
python scripts/build_playlist.py auth
```

This pops a real browser tab for the user to approve access — it is **not** a manual copy-paste flow, and shouldn't be turned into one. (An earlier iteration of this script tried a manual code-paste workaround when the automatic flow seemed to be failing; the actual root cause was binding the local callback server to the ambiguous hostname `localhost`, which resolves to IPv6 `::1` before IPv4 `127.0.0.1` on many machines. Binding explicitly to `127.0.0.1` fixed it. If the browser flow ever seems broken again, look there before reaching for a workaround.)

This only has to happen once per machine — the resulting refresh token is cached (default `~/.cache/mario-producer-playlist/youtube_token.json`) and reused silently by every later command, including automatic token refresh on expiry. Skip this step if a valid cached token already exists.

If nothing comes back within `--consent-timeout` (default 120s), the script says so explicitly and stops — don't spin up a workaround, just tell the user the consent link may have been missed and offer to rerun.

---

## Step 4: Resolve each producer to a YouTube channel

The `plan` command (Step 5) does this internally for every producer at once, but the disambiguation logic is worth understanding, since it's the crux of the whole skill:

1. Search YouTube for channels matching the name.
2. **Keep only channels YouTube itself tags with a Music-related topic category** (`topicDetails.topicCategories`) — this drops unrelated same-name channels (sports, gaming, whatever) before comparing anything else.
3. **Among the survivors, the one with the most subscribers wins.** That's the whole rule — no description text, no fuzzy scoring. YouTube's public API has no "official artist channel" flag exposed to third-party consumers (verified this directly against live API responses — don't assume such a field exists), so subscriber count is the deliberately simple stand-in the user chose after that was surfaced.
4. **Look for that artist's paired auto-generated `"<Name> - Topic"` channel** — YouTube builds this automatically from official release metadata, containing only music (no interviews, vlogs, behind-the-scenes). Prefer pulling tracks from it. Two things to watch for here, both found via live testing:
   - The Topic channel's title sometimes uses a shortened stage name (`"Pharrell - Topic"` for `"Pharrell Williams"`) — don't match on exact name equality, match on the `"- Topic"` suffix + Music tagging.
   - Impostor/copycat channels can squat on a `"<Name> - Topic"`-shaped title with near-zero subscribers and no real Music tag — when more than one candidate matches the suffix, rank by subscriber count among the ones actually tagged Music, don't just take the first hit.
   - If no Topic channel is found at all, fall back to the main channel's own uploads.

---

## Step 5: Build the plan (no writes yet)

```bash
python scripts/build_playlist.py plan \
  --producer "<name>" [--producer "<name>" ...] \
  --count 10 --sort recent|popular \
  --out plan.json
```

For each producer this returns: resolved channel (name + clickable URL + subscriber count), track source channel (name + clickable URL), how many tracks were actually found, the most recent release date **and** how many days ago that was, and the full track list (each with its own clickable `music.youtube.com` URL, title, publish date, view count).

The days-ago figure matters: it tells you whether "top N" is actually meaningful for a given producer or whether the pipeline is scraping the bottom of a mostly-dormant catalog (a producer whose newest pick is 3+ years old is a very different result than one with fresh material). Surface it plainly — don't bury it in a details.

Present this to the user as a readable table (producer, resolved channel with link, subs, track source with link, tracks found, most recent release + days ago), not a raw JSON dump.

---

## Step 6: Confirm before writing anything

**Always show the resolved plan and get explicit approval before creating the playlist.** This is a real write to the user's YouTube account and not something to reverse casually. If the user doesn't approve — wants a different sort, different producers, different count — go back to Step 5 with the adjustment and show the new plan. Don't hand-edit the plan file yourself and don't proceed on a partial or ambiguous "sounds fine."

---

## Step 7: Create the playlist

```bash
python scripts/build_playlist.py execute --plan-file plan.json --privacy private
```

Report the result as:

```
https://music.youtube.com/playlist?list=<PLAYLIST_ID>
```

That's the format that opens directly in the user's YouTube Music client — always swap the host from the plain `youtube.com` API response, never hand back that form.

---

## Gotchas

- **Every network call has a hard timeout (default 5s, `--timeout` to adjust).** On a timeout, the script stops and prints a clear message instead of retrying or degrading silently — treat that as a real stop, tell the user what happened, and ask how to proceed rather than looping or raising the timeout unilaterally.
- **"Produced by X" here really means "released by X's own YouTube identity,"** not a verified production credit. Say this out loud if the user's phrasing suggests they expect the latter.
- **No "official artist channel" API flag exists.** Subscriber count among Music-tagged channels is the deliberately simple disambiguation rule — don't reintroduce description-text heuristics or other fuzzy scoring without the user asking for it again; that tradeoff was made explicitly.
- **`localhost` vs `127.0.0.1` in the auth flow is not cosmetic.** If browser consent ever seems to hang or fail near-instantly, check that the callback server and redirect URI are both using `127.0.0.1` explicitly — this was a real, previously-diagnosed failure mode, not a hypothetical one.
- **A producer's catalog can be stale.** Always surface `most_recent_release_days_ago` so the user can judge whether the results are meaningful before approving.
- **This is a real account write.** Don't run `execute` speculatively — only after the user has seen and approved the Step 5 plan.
