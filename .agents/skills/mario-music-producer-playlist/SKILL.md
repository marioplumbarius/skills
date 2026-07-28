---
name: mario-music-producer-playlist
description: >-
  Build a YouTube Music playlist made entirely of songs credited to one or
  more named producers (e.g. Pharrell, Timbaland, Swizz Beatz) — including
  tracks they produced for other artists, not just their own releases. Use
  this when the user asks to make a playlist "produced by X", wants a
  crate-dig of a producer's beats/catalog, or wants to combine several
  producers into one YouTube Music playlist — even if they only name the
  producer(s) and say "make me a playlist" without spelling out the
  pipeline. Resolves each name to a confirmed Genius artist credit, matches
  each credited song to YouTube, and confirms the exact track list with
  the user before writing anything to their YouTube account, since
  playlist creation is a real, hard-to-reverse write.
compatibility: >-
  Requires a Genius API client access token (producer-credit source of
  truth) and a Google Cloud OAuth client authorized for the YouTube Data
  API v3 (scope: youtube, used for matching + playlist creation). See
  references/credentials-setup.md. Uses scripts/build_playlist.py.
metadata:
  author: mario
  version: "3.0"
  category: music
---

# Producer Playlist Builder

Turn a list of producers into a real YouTube Music playlist of songs they produced — including tracks credited to them on someone else's release, which is the whole point of "produced by X" and something YouTube alone cannot answer (it has no producer-credit concept; it can only ever show a producer's own uploads). **Genius is the sole source of track discovery here.** YouTube is used only to find the matching video for each Genius-confirmed credit, rank/present results, and create the actual playlist.

This design was reached the hard way: an earlier iteration tried resolving producers to their own YouTube channel and pulling from that catalog, which is cheap but structurally blind to cross-artist production credits — verified directly with a real example (a Swizz Beatz/Timbaland-produced track released under The Game's channel never surfaced). Don't reintroduce that shortcut without the user explicitly asking for it again.

---

## Step 1: Gather inputs

- **Producers** — one or more names. Required.
- **Tracks per producer** — default **3**. Kept deliberately small: each confirmed credit costs a YouTube `search.list` call, and the free daily quota is only 100 of those (see Gotchas) — a low default keeps a `plan` run affordable, especially across multiple producers.
- **Sort** — `recent` (default, newest release first) or `popular` (highest YouTube view count first). Real input, not a preset.

Don't guess if any of these are genuinely unclear.

---

## Step 2: Check credentials

Verify both `GENIUS_ACCESS_TOKEN` and `YOUTUBE_CLIENT_SECRETS` are set before doing anything else. If either is missing, walk the user through `references/credentials-setup.md` rather than guessing.

---

## Step 3: One-time YouTube browser authorization

```bash
python scripts/build_playlist.py auth
```

Pops a real browser tab for approval — not a manual copy-paste flow. (Root cause of earlier flakiness: binding the local callback server to the ambiguous hostname `localhost`, which resolves to IPv6 before IPv4 on many machines. `auth` binds explicitly to `127.0.0.1` to avoid this. If it ever seems broken again, check that binding before reaching for a workaround.) Only needed once per machine — the cached refresh token is reused silently afterward, including automatic refresh on expiry.

---

## Step 4: Resolve each producer to a Genius artist

```bash
python scripts/build_playlist.py resolve --producer "<name>"
```

Genius has no direct "look up this artist" endpoint, so this searches broadly and pulls out artist matches. **If more than one plausible candidate comes back, surface them and ask the user which one is correct — never guess.** A wrong artist ID silently produces a playlist of the wrong person's work.

---

## Step 5: Build the plan (no writes yet)

```bash
python scripts/build_playlist.py plan \
  --producer "<name>" [--producer "<name>" ...] \
  --count 3 --sort recent|popular \
  [--youtube-search-fallback] \
  --out plan.json
```

Per producer, this:

1. Resolves the Genius artist (Step 4's logic, run automatically; stops with an `error` + candidate list if ambiguous rather than guessing).
2. Pulls candidate songs from **`/artists/{id}/songs?sort=release_date|popularity`** — the artist's own Genius page, sorted server-side to match the requested sort. This is deliberately *not* generic `/search`: it's scoped to songs Genius already associates with this artist and pre-ordered by the right signal, which is both faster and more accurate than paginating full-text search. (Verified live: for Swizz Beatz, `sort=release_date` put his most recent actual production credit first in the list.)
3. **Confirms each candidate's real producer credit** via the song detail endpoint's `producer_artists` field — the artist-songs listing includes *any* credited role (writer, feature, producer), so this confirmation step is not optional. (Verified live: one of Swizz Beatz's top candidates credited him as a writer only, not a producer, and was correctly filtered out.)
4. Gathers roughly `count * 2` confirmed credits so there's a real pool to rank, then matches each to YouTube. **Genius song details often already include a direct YouTube link** in their `media` field (verified live across 10 songs from 3 producers: 8/10 had one) — when present, this is used to look the video up directly via `videos.list` (1 quota unit) instead of paying for a `search.list` call (100 units) to go find it. **`--youtube-search-fallback` is off by default** — a song with no Genius-provided link is simply skipped (recorded in `tracks_skipped`) rather than spending search quota on it. Only pass this flag when the user explicitly wants the fallback (100 units/song, and the daily budget is only 100 calls total) — don't turn it on "to be thorough" without them asking, since it's exactly the quota-burning behavior that got us into trouble during testing.
5. Ranks the matched set by the requested sort and keeps the top `count`.

**Every step logs its progress to stderr as it happens** (`log()` calls throughout) — a full run can take a while (a Genius round-trip per candidate + a YouTube round-trip per confirmed credit), and silence during that time reads as "stuck" even when it's actively working. Don't strip this logging out; if running the script yourself, don't redirect stderr away from something visible, and if backgrounding it, check the log file rather than assuming it's hung.

**A failed YouTube lookup for one song never aborts the run.** Timeouts, rate limits, and any other per-song failure are caught, recorded with a reason in `tracks_skipped`, and processing continues to the next song. At the end, `cmd_plan` logs a per-producer succeeded/failed summary plus every failure's specific reason — present this to the user so they can decide whether anything is worth a retry, rather than silently losing partial results to one flaky call.

Present the plan as a readable table (producer, Genius artist name + link, tracks found vs. skipped, most recent release + days ago), not a raw JSON dump.

---

## Step 6: Confirm before writing anything

**Always show the resolved plan and get explicit approval before creating the playlist.** This is a real write to the user's YouTube account. If not approved — different sort, different producers, different count — go back to Step 5 with the adjustment. Don't hand-edit the plan file yourself.

**Also ask two more things before proceeding, every time — don't default silently:**

1. **New playlist, or an existing one?** Run `python scripts/build_playlist.py list-playlists` and show the user their existing playlists (title + track count) as options, alongside "create new." This exists specifically so repeated runs don't quietly accumulate a pile of near-duplicate playlists.
2. **If new: what should it be called?** Offer the auto-generated default (`Produced by <producers>`) but let the user override it.
3. **If existing: merge or replace?** `merge` adds this run's tracks on top of what's already there; `replace` clears the existing playlist first. Get an explicit choice — don't assume either one, since replace is destructive to whatever was already in that playlist.

---

## Step 7: Create or update the playlist

```bash
# New playlist
python scripts/build_playlist.py execute --plan-file plan.json --mode create --title "<name>"

# Existing playlist
python scripts/build_playlist.py execute --plan-file plan.json --mode replace --playlist-id <id>
python scripts/build_playlist.py execute --plan-file plan.json --mode merge   --playlist-id <id>
```

`--playlist-id` is required for `replace`/`merge` — get it from `list-playlists`, never guess or construct one. `replace` deletes every existing item in that playlist before adding the plan's tracks; treat that step with the same care as any other destructive write, since it's not reversible from here.

**`execute` deduplicates by YouTube video ID before adding anything.** A track credited to more than one requested producer (e.g. a collab both of them produced) otherwise shows up twice in the plan's combined track list and would get added to the playlist twice — this is deduped down to one add, logged as `skipped_duplicate_in_plan` in the result. In `--mode merge`, it also fetches the target playlist's current contents first and skips any track already sitting there (`skipped_already_in_playlist`) — this matters for repeated merge runs against the same playlist, so re-running doesn't pile up duplicate entries. `--mode replace` doesn't need this second check since the playlist is cleared first.

**New playlists default to `--privacy public`.** Pass `--privacy private` or `--privacy unlisted` explicitly if the user wants otherwise — don't assume public is always fine without at least a quick check when the content might be sensitive to the user, but don't ask about it every single time either now that it's the established default.

Report the result as `https://music.youtube.com/playlist?list=<PLAYLIST_ID>` — always swap the host from the plain `youtube.com` form the API returns, since the ask is specifically to open it in YouTube Music.

---

## Gotchas

- **YouTube Data API's free daily quota is exactly 100 `search.list` calls** (10,000 units/day ÷ 100 units per search — this is the standard default, not a special restriction). The Genius-media-first lookup (see Step 5.4) keeps most songs off this budget entirely, but the fallback search path still uses it — a `429` here is `reason: rateLimitExceeded` with `quota_metric: youtube.googleapis.com/search_list` — check the response body to confirm before assuming it's a transient burst limit; if the daily quota is exhausted, no backoff or retry fixes it, only waiting for the midnight Pacific reset or requesting a quota increase (free to submit, manually reviewed by Google, not instant — don't imply it's a same-day fix). Also remember the reset is midnight **Pacific**, not the local system clock's midnight — check `TZ='America/Los_Angeles' date` before assuming a new day means the quota is back.
- **No automatic retry/backoff on YouTube failures, by deliberate design.** An earlier version added exponential backoff for 429s; the user explicitly asked to remove it in favor of per-song failure tracking + a final report, so a bad run doesn't silently burn time retrying something that won't clear (like a daily quota, which no backoff can fix anyway).
- **Genius's `/artists/{id}/songs` is not producer-specific** — it lists any credited role. The per-song `producer_artists` confirmation step is load-bearing; don't skip it to save a round-trip.
- **Ambiguous producer names** — always surface Genius candidates rather than guessing.
- **This is a real account write.** Don't run `execute` speculatively — only after the user has seen and approved the Step 5 plan.
- **`--mode replace` deletes every existing item in the target playlist before adding anything new.** It cannot be undone from within this skill. Never pick `replace` on the user's behalf — always get an explicit merge-vs-replace answer when targeting an existing playlist (Step 6).
