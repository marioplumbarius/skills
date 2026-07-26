---
name: mario-producer-playlist
description: >-
  Build a YouTube Music playlist made entirely of songs produced by one or
  more named producers (e.g. Pharrell, Timbaland, Metro Boomin, Kanye West).
  Use this when the user asks to make a playlist "produced by X", wants a
  crate-dig of a producer's beats/catalog, or wants to combine several
  producers into one YouTube Music playlist — even if they only name the
  producer(s) and say "make me a playlist" without spelling out the pipeline.
  Confirms the exact track list with the user before writing anything to
  their YouTube account, since playlist creation is a real, hard-to-reverse
  write.
compatibility: >-
  Requires a Genius API client access token and a Google Cloud OAuth client
  authorized for the YouTube Data API v3 (scope: youtube). See
  references/credentials-setup.md. Uses scripts/build_playlist.py.
metadata:
  author: mario
  version: "1.0"
  category: music
---

# Producer Playlist Builder

Turn a list of producers into a real YouTube Music playlist of songs they produced. The hard part isn't the API calls — it's that **YouTube has no concept of "producer."** Producer credit has to come from somewhere else (Genius), and then each credited song has to be found and ranked on YouTube. Treat this as a two-source pipeline, not a single search.

---

## Why this is two systems, not one

- **Genius** is the credit source. Its song data includes a `producer_artists` field, which is the actual ground truth for "who produced this." Use it to build the *candidate pool* per producer.
- **YouTube Data API v3** is the destination and the popularity signal. It has no idea who produced anything — its job is to find the matching video for each Genius-credited song, rank candidates by view count, and create the playlist.

Never try to shortcut this by just searching YouTube for the producer's name — that returns videos *about* or *featuring* the producer, not songs they produced, and it's exactly the kind of noisy shortcut this skill exists to avoid.

---

## Step 1: Gather inputs

Ask for (or infer from the request), and don't guess if any of these are genuinely unclear:

- **Producers** — one or more names. Required.
- **Tracks per producer** — default **10**.
- **Time window** — default **last 7 days**, filtered by each song's release date. Alternative: `all-time` (no release-date filter). See the Gotchas section for what this default actually means in practice — it is a release-date filter, not a "views gained this week" metric, because YouTube's public API doesn't expose the latter.
- **Region** — default **global** (no country bias). Alternative: an ISO country code (e.g. `US`, `BR`, `GB`) to bias YouTube search relevance toward that market.

Time window and region are **independent filters** — a user can ask for "all-time, but popular in Brazil" or "last 7 days, globally." Don't collapse them into one combined preset.

---

## Step 2: Check credentials

Before doing anything else, verify both credentials exist:

- `GENIUS_ACCESS_TOKEN` environment variable
- A YouTube OAuth client (client secrets file + a way to complete the consent screen once)

If either is missing, stop and walk the user through `references/credentials-setup.md` rather than assuming they have it configured. Don't attempt API calls with placeholder or guessed credentials.

---

## Step 3: Resolve each producer to a Genius artist

Run:

```bash
python scripts/build_playlist.py resolve --producer "<name>"
```

This searches Genius for the name and returns candidate artist matches. **If more than one plausible candidate comes back (common names, or a producer who's also a performing artist under a similar handle), show the candidates to the user and ask which one is correct.** Never silently pick the first result — a wrong artist ID silently produces a whole playlist of the wrong person's work, which is a much worse failure than pausing to ask.

---

## Step 4: Pull and confirm the candidate pool

Run:

```bash
python scripts/build_playlist.py plan \
  --producer-id <id> --producer-name "<confirmed name>" \
  [--producer-id <id> --producer-name "<confirmed name>" ...] \
  --count 10 \
  --time-window last-7-days|all-time \
  --region global|<ISO-country-code>
```

`--producer-id` and `--producer-name` are paired positionally — pass one of each per producer, in the same order, using the artist confirmed in Step 3.

This does the real work, per producer:

1. Searches Genius broadly for the producer's name, then confirms each candidate song's `producer_artists` field actually includes them — Genius's API has no direct "songs by producer" endpoint, so this search-then-confirm step is unavoidable. Don't accept a Genius search hit without this confirmation step; a raw search result frequently just *mentions* the producer.
2. Applies the time-window filter against each song's Genius release date, if set.
3. Searches the YouTube Data API for each confirmed song (`"<artist> - <title>"`, restricted to music) and takes the best match.
4. Ranks matched videos by `statistics.viewCount`, applying the region bias to the search relevance if a country was given.
5. Keeps the top N per producer.

The script prints a **plan**: every selected track (producer → title → matched YouTube video → view count), plus a separate list of anything it had to skip (no Genius credit confirmation, or no YouTube match found) with the reason. Read this whole plan yourself before showing it to the user — don't just relay the raw script output if it's long; summarize the picks and call out every skip.

---

## Step 5: Confirm before writing anything

**Always show the user the resolved plan and ask them to confirm before creating the playlist.** This is a real write to their YouTube account — creating a playlist and adding videos to it — and it's not something to reverse casually. Show:

- The producer list as resolved (in case any name matched an unexpected artist)
- The final track list per producer, with the filters applied (time window, region)
- Anything skipped and why

Only proceed to Step 6 after explicit confirmation. If the user wants changes (swap a track, drop a producer, widen the time window), rerun Step 4 with the adjustment rather than hand-editing the plan yourself.

---

## Step 6: Create the playlist

Run:

```bash
python scripts/build_playlist.py execute --plan-file <path-to-plan-from-step-4>
```

This creates a real playlist on the authenticated YouTube account and adds every confirmed track to it. Report back the playlist link in the form:

```
https://music.youtube.com/playlist?list=<PLAYLIST_ID>
```

That's the format the user can click to open directly in YouTube Music. Don't hand back the plain `youtube.com/playlist` link — swap the host, since the ask is specifically to open it in their YouTube Music client.

---

## Gotchas

- **"Top" isn't a native YouTube metric over a time window.** The public YouTube Data API only exposes lifetime view counts (`statistics.viewCount`) and a region-locked *current* trending chart — there's no API for "views gained in the last 7 days" on an arbitrary video. The `last-7-days` default is implemented as a **release-date filter**, then ranks the survivors by lifetime views. Say this plainly to the user if they seem to expect a true rolling-popularity metric — don't let them believe it's measuring something the API can't actually measure.
- **Region is a relevance bias, not a hard filter.** YouTube's `regionCode` parameter nudges search relevance toward that locale; it doesn't restrict results to videos popular *only* in that country. Set expectations accordingly.
- **Genius credit ≠ guaranteed YouTube match.** Some Genius-credited songs won't have a clean YouTube Music match (unreleased, region-locked, or removed). Skip and report these — never quietly drop a producer down to fewer tracks without saying so.
- **Ambiguous producer names are common** (there are multiple "Boi-1da"-adjacent handles, producers who share names with performing artists, etc.) — always surface candidates rather than guessing, per Step 3.
- **This is a real account write.** Once Step 6 runs, the playlist exists on the user's account. Don't run Step 6 speculatively "to see what happens" — only after the user has seen and confirmed the Step 4/5 plan.
