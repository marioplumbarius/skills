#!/usr/bin/env python3
"""
Build a YouTube Music playlist from songs credited to one or more producers.

Track discovery is 100% driven by Genius (the only source with a real
"who produced this" credit — YouTube has no such concept and can only ever
show a producer's own uploads, missing every track they produced that got
released under someone else's name). YouTube is used only to find the
matching video for each Genius-credited song and to rank/present results.

Every network call has a hard timeout (default 5s). A timeout aborts the
run with a clear message instead of retrying or silently degrading — the
caller (the agent driving this script) is expected to stop and ask the
user what to do next, per mario-music-producer-playlist/SKILL.md.

Subcommands:
  auth  resolve  plan  execute
"""

import argparse
import json
import os
import sys
import urllib.parse
from datetime import datetime, timezone

import requests

YT_API_BASE = "https://www.googleapis.com/youtube/v3"
TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/youtube"
DEFAULT_TOKEN_CACHE = os.path.expanduser("~/.cache/mario-music-producer-playlist/youtube_token.json")

GENIUS_API_BASE = "https://api.genius.com"
GENIUS_SEARCH_MAX_PAGES = 5


def die(msg):
    sys.exit(msg)


def log(msg):
    """Progress line to stderr, flushed immediately. `plan` can run for a
    while (Genius search-and-confirm + a YouTube lookup per candidate
    song) — silence during that time reads as "stuck" even when it's
    actively working, so every meaningful step reports here."""
    print(msg, file=sys.stderr, flush=True)


# --- YouTube auth / token plumbing ----------------------------------------

def load_client_secrets():
    path = os.environ.get("YOUTUBE_CLIENT_SECRETS")
    if not path or not os.path.isfile(path):
        die("YOUTUBE_CLIENT_SECRETS is not set or file not found. See references/credentials-setup.md.")
    with open(path) as f:
        data = json.load(f)
    return data.get("installed") or data.get("web") or die("Unrecognized client secrets format.")


def load_cached_token(cache_path):
    if not os.path.exists(cache_path):
        return None
    with open(cache_path) as f:
        return json.load(f)


def save_token(cache_path, token_info):
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(token_info, f)


def refresh_access_token(token_info, timeout):
    client = load_client_secrets()
    try:
        resp = requests.post(
            TOKEN_URI,
            data={
                "client_id": client["client_id"],
                "client_secret": client["client_secret"],
                "refresh_token": token_info["refresh_token"],
                "grant_type": "refresh_token",
            },
            timeout=timeout,
        )
    except requests.exceptions.Timeout:
        die(f"Timed out refreshing the YouTube access token after {timeout}s. Stopping — rerun when ready.")
    resp.raise_for_status()
    new_token = resp.json()
    token_info["access_token"] = new_token["access_token"]
    return token_info


def get_access_token(args):
    token_info = load_cached_token(args.token_cache)
    if not token_info:
        die("No cached YouTube token found. Run `auth` first.")
    # We don't track expiry timestamps locally; a 401 on first real call
    # triggers a refresh-and-retry-once instead of guessing expiry.
    return token_info


def yt_get(path, access_token, params, timeout, retry_token_info=None, args=None):
    resp = requests.get(
        f"{YT_API_BASE}/{path}",
        params=params,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=timeout,
    )
    if resp.status_code == 401 and retry_token_info is not None:
        refreshed = refresh_access_token(retry_token_info, timeout)
        save_token(args.token_cache, refreshed)
        access_token = refreshed["access_token"]
        resp = requests.get(
            f"{YT_API_BASE}/{path}",
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=timeout,
        )
    resp.raise_for_status()
    return resp.json()


# --- auth ------------------------------------------------------------------
#
# Uses google-auth-oauthlib's InstalledAppFlow to pop a real browser tab and
# catch the redirect on a local loopback server — NOT a manual copy/paste
# flow. Root cause of earlier flakiness in sandboxed environments: binding
# to the hostname "localhost" is ambiguous (it commonly resolves to IPv6
# ::1 before IPv4 127.0.0.1, and the server ends up bound to the address
# the browser doesn't try first). Binding explicitly to 127.0.0.1 for both
# the server and the redirect_uri host fixes it. Auth only has to happen
# once — after this, the cached refresh_token is used silently on every
# future run.

def cmd_auth(args):
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google_auth_oauthlib.flow import WSGITimeoutError

    flow = InstalledAppFlow.from_client_secrets_file(
        os.environ.get("YOUTUBE_CLIENT_SECRETS") or die(
            "YOUTUBE_CLIENT_SECRETS is not set. See references/credentials-setup.md."
        ),
        [SCOPE],
    )
    try:
        creds = flow.run_local_server(
            host="127.0.0.1",
            bind_addr="127.0.0.1",
            port=0,
            open_browser=True,
            timeout_seconds=args.consent_timeout,
        )
    except WSGITimeoutError:
        die(
            f"Hey — there was a timeout. No approval came back within {args.consent_timeout}s. "
            "Maybe you missed the link that was printed above, or closed the tab before approving. "
            "Rerun `auth` to get a fresh link and try again."
        )

    client = load_client_secrets()
    token_info = {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
    }
    save_token(args.token_cache, token_info)
    print(f"Token cached at {args.token_cache}")


# --- Genius: producer identity + credit lookup -----------------------------

def genius_token():
    token = os.environ.get("GENIUS_ACCESS_TOKEN")
    if not token:
        die("GENIUS_ACCESS_TOKEN is not set. See references/credentials-setup.md.")
    return token


def genius_get(path, params, timeout):
    try:
        resp = requests.get(
            f"{GENIUS_API_BASE}{path}",
            params=params,
            headers={"Authorization": f"Bearer {genius_token()}"},
            timeout=timeout,
        )
    except requests.exceptions.Timeout:
        die(
            f"Genius API call to {path} timed out after {timeout}s. "
            "Stopping — tell me how you'd like to proceed."
        )
    resp.raise_for_status()
    return resp.json()["response"]


def _normalize_name(s):
    """Strip everything but letters/digits before comparing artist names.
    Genius sometimes punctuates a stage name differently than how a user
    types it (e.g. the producer "No I.D." vs. a user typing "No ID") —
    without normalizing, a literal substring match misses this entirely
    and reports zero candidates for a very real, well-known artist."""
    return "".join(ch for ch in s.lower() if ch.isalnum())


def resolve_producer_candidates(name, timeout, limit=5):
    """Search Genius for the name and return plausible artist candidates.
    Genius has no direct "look up this artist" endpoint by name, so this
    goes through song search and pulls out artists whose (normalized) name
    contains the query — deliberately permissive, since ambiguity here
    should be surfaced to the user rather than silently resolved."""
    data = genius_get("/search", {"q": name}, timeout)
    normalized_query = _normalize_name(name)
    seen = {}
    for hit in data.get("hits", []):
        result = hit["result"]
        for artist in [result["primary_artist"]] + result.get("featured_artists", []):
            if artist["id"] not in seen and normalized_query in _normalize_name(artist["name"]):
                seen[artist["id"]] = {"id": artist["id"], "name": artist["name"], "url": artist["url"]}
        if len(seen) >= limit:
            break
    return list(seen.values())[:limit]


def song_credits_producer(song_id, producer_artist_id, timeout):
    """Confirm via the song detail endpoint that this song actually credits
    the producer — a Genius search hit only means the name appears
    somewhere on the page, not that they're a confirmed producer_artists
    credit."""
    song = genius_get(f"/songs/{song_id}", {"text_format": "plain"}, timeout)["song"]
    producer_ids = {p["id"] for p in song.get("producer_artists", [])}
    return producer_artist_id in producer_ids, song


def extract_youtube_video_id(media):
    """Genius song detail responses often already include a direct YouTube
    link in `media` (verified live across 10 songs from 3 producers: 8/10
    had one). Using this skips the expensive YouTube search.list call
    (100 quota units) entirely for those songs — only videos.list (1 unit)
    is needed afterward to pull stats. Falls back to a real search only
    when Genius has no such link."""
    for m in media or []:
        if m.get("provider") != "youtube" or not m.get("url"):
            continue
        parsed = urllib.parse.urlparse(m["url"])
        qs = urllib.parse.parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]
        if parsed.netloc.endswith("youtu.be"):
            return parsed.path.lstrip("/")
    return None


GENIUS_SORT_BY_OUR_SORT = {"recent": "release_date", "popular": "popularity"}


def find_credited_songs(producer_name, producer_artist_id, want, timeout, sort="recent", max_pages=GENIUS_SEARCH_MAX_PAGES):
    """Pull candidate songs from the artist's own Genius page
    (`/artists/{id}/songs`), sorted server-side by release_date or
    popularity to match the requested sort — this is a far better
    candidate source than generic full-text `/search`, since it's already
    scoped to songs Genius associates with this specific artist and
    already ordered by the signal we care about (verified live: for
    Swizz Beatz, sort=release_date puts his most recent production credit
    dead first).

    It still isn't producer-specific, though — the artist-songs listing
    includes ANY credited role (writer, feature, producer), so each
    candidate is confirmed via the song detail endpoint exactly as before
    (verified live: one of the top-5 results for Swizz Beatz credited him
    as a writer only, not a producer, and was correctly filtered out)."""
    genius_sort = GENIUS_SORT_BY_OUR_SORT.get(sort, "release_date")
    confirmed = []
    seen_song_ids = set()
    page = 1
    while len(confirmed) < want and page <= max_pages:
        log(f"  [{producer_name}] Genius: fetching artist songs page {page}/{max_pages} (sort={genius_sort})...")
        data = genius_get(
            f"/artists/{producer_artist_id}/songs",
            {"sort": genius_sort, "per_page": 20, "page": page},
            timeout,
        )
        songs = data.get("songs", [])
        if not songs:
            log(f"  [{producer_name}] Genius: page {page} returned no songs, stopping search.")
            break
        log(f"  [{producer_name}] Genius: page {page} has {len(songs)} songs, confirming producer credit on each...")
        for result in songs:
            song_id = result["id"]
            if song_id in seen_song_ids:
                continue
            seen_song_ids.add(song_id)
            is_match, song = song_credits_producer(song_id, producer_artist_id, timeout)
            if not is_match:
                continue
            confirmed.append(
                {
                    "genius_song_id": song_id,
                    "title": song["title"],
                    "primary_artist": song["primary_artist"]["name"],
                    "genius_url": song["url"],
                    "genius_video_id": extract_youtube_video_id(song.get("media")),
                }
            )
            log(f"  [{producer_name}] Confirmed credit {len(confirmed)}/{want}: "
                f"\"{song['title']}\" by {song['primary_artist']['name']}")
            if len(confirmed) >= want:
                break
        page += 1
    log(f"  [{producer_name}] Genius search done: {len(confirmed)} confirmed credits across {page - 1} page(s).")
    return confirmed, page - 1


def cmd_resolve(args):
    candidates = resolve_producer_candidates(args.producer, args.timeout)
    if not candidates:
        die(f"No Genius artist candidates found for '{args.producer}'.")
    print(json.dumps({"producer": args.producer, "candidates": candidates}, indent=2))


# --- YouTube matching -------------------------------------------------------

def video_url(video_id):
    return f"https://music.youtube.com/watch?v={video_id}"


def days_ago(iso_timestamp):
    if not iso_timestamp:
        return None
    published = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - published).days


def youtube_video_by_id(access_token, video_id, args, token_info):
    """Look up a specific video ID directly (videos.list, 1 quota unit) —
    used when Genius already told us which YouTube video this song is,
    instead of paying for a search.list call (100 units) to go find it."""
    try:
        stats = yt_get(
            "videos",
            access_token,
            {"part": "statistics,snippet", "id": video_id},
            args.timeout,
            retry_token_info=token_info,
            args=args,
        )
    except requests.exceptions.Timeout:
        return None, f"YouTube video lookup timed out after {args.timeout}s"
    except requests.exceptions.RequestException as e:
        return None, f"YouTube video lookup failed: {e}"

    items = stats.get("items", [])
    if not items:
        return None, "Genius-linked video not found on YouTube (removed or region-locked?)"
    v = items[0]
    return {
        "video_id": v["id"],
        "title": v["snippet"]["title"],
        "channel_title": v["snippet"]["channelTitle"],
        "published_at": v["snippet"]["publishedAt"],
        "view_count": int(v["statistics"].get("viewCount", 0)),
        "url": video_url(v["id"]),
    }, None


def best_youtube_match(access_token, artist, title, args, token_info):
    """Returns (match, failure_reason) — exactly one is None. A failure here
    (timeout, rate limit, any other API error) is per-song and non-fatal:
    the caller records it and moves on to the next song rather than
    aborting the whole plan. This is a deliberate choice — a single flaky
    lookup shouldn't cost the user everything already found for every
    other producer/song in the run. The full list of what failed vs.
    succeeded is reported in the plan so the user can decide whether any
    of it is worth retrying."""
    query = f"{artist} - {title}"
    try:
        search = yt_get(
            "search",
            access_token,
            {
                "part": "snippet",
                "q": query,
                "type": "video",
                "videoCategoryId": "10",
                "maxResults": 5,
            },
            args.timeout,
            retry_token_info=token_info,
            args=args,
        )
    except requests.exceptions.Timeout:
        return None, f"YouTube search timed out after {args.timeout}s"
    except requests.exceptions.RequestException as e:
        return None, f"YouTube search failed: {e}"

    items = search.get("items", [])
    video_ids = [i["id"]["videoId"] for i in items if "videoId" in i.get("id", {})]
    if not video_ids:
        return None, "no YouTube search results"

    try:
        stats = yt_get(
            "videos",
            access_token,
            {"part": "statistics,snippet", "id": ",".join(video_ids)},
            args.timeout,
            retry_token_info=token_info,
            args=args,
        )
    except requests.exceptions.Timeout:
        return None, f"YouTube stats lookup timed out after {args.timeout}s"
    except requests.exceptions.RequestException as e:
        return None, f"YouTube stats lookup failed: {e}"

    candidates = stats.get("items", [])
    if not candidates:
        return None, "no video stats returned"
    # Among the top search hits, the one with the most views is taken as the
    # correct/official upload for this song — search relevance alone is too
    # noisy (lyric videos, fan reuploads, etc. can outrank the real one).
    top = max(candidates, key=lambda v: int(v["statistics"].get("viewCount", 0)))
    return {
        "video_id": top["id"],
        "title": top["snippet"]["title"],
        "channel_title": top["snippet"]["channelTitle"],
        "published_at": top["snippet"]["publishedAt"],
        "view_count": int(top["statistics"].get("viewCount", 0)),
        "url": video_url(top["id"]),
    }, None


# --- plan --------------------------------------------------------------

def build_producer_plan(name, count, sort, args, token_info, access_token):
    log(f"[{name}] Resolving Genius artist...")
    candidates = resolve_producer_candidates(name, args.timeout)
    if not candidates:
        log(f"[{name}] No Genius artist candidates found.")
        return {"producer": name, "error": "No Genius artist candidates found."}
    if len(candidates) > 1:
        log(f"[{name}] Ambiguous — {len(candidates)} Genius artist candidates found, stopping for disambiguation.")
        return {
            "producer": name,
            "error": "Ambiguous — multiple Genius artist candidates found. Disambiguate and rerun.",
            "candidates": candidates,
        }

    artist = candidates[0]
    log(f"[{name}] Resolved to Genius artist \"{artist['name']}\" (id={artist['id']}).")
    # Gather more confirmed credits than requested so recency/popularity
    # sorting has something real to choose among, not just "first N found".
    want = count * 2
    log(f"[{name}] Searching Genius for credited songs (target: {want} confirmed credits)...")
    credited_songs, pages_searched = find_credited_songs(
        name, artist["id"], want=want, timeout=args.timeout, sort=sort
    )

    log(f"[{name}] Matching {len(credited_songs)} confirmed credits against YouTube...")
    matched, skipped = [], []
    for i, song in enumerate(credited_songs, start=1):
        genius_video_id = song.get("genius_video_id")
        if genius_video_id:
            log(f"  [{name}] ({i}/{len(credited_songs)}) Using Genius-linked video {genius_video_id} for "
                f"\"{song['title']}\" (cheap lookup, no search needed)...")
            match, failure_reason = youtube_video_by_id(access_token, genius_video_id, args, token_info)
            if not match and args.youtube_search_fallback:
                log(f"  [{name}] ({i}/{len(credited_songs)}) Genius-linked video lookup failed "
                    f"({failure_reason}) — falling back to YouTube search...")
                match, failure_reason = best_youtube_match(
                    access_token, song["primary_artist"], song["title"], args, token_info
                )
        elif args.youtube_search_fallback:
            log(f"  [{name}] ({i}/{len(credited_songs)}) No Genius-linked video — searching YouTube for "
                f"\"{song['title']}\" by {song['primary_artist']}...")
            match, failure_reason = best_youtube_match(
                access_token, song["primary_artist"], song["title"], args, token_info
            )
        else:
            match, failure_reason = None, (
                "no Genius-linked YouTube video, and --youtube-search-fallback is off (default)"
            )

        if match:
            log(f"  [{name}] ({i}/{len(credited_songs)}) OK: matched \"{match['title']}\"")
            matched.append({**song, **match})
        else:
            log(f"  [{name}] ({i}/{len(credited_songs)}) FAILED: \"{song['title']}\" — {failure_reason}. Continuing.")
            skipped.append({**song, "skip_reason": failure_reason})

    matched.sort(key=lambda t: t["view_count"] if sort == "popular" else t["published_at"], reverse=True)
    tracks = matched[:count]
    most_recent = max((t["published_at"] for t in tracks), default=None)
    log(
        f"[{name}] Done: {len(matched)}/{len(credited_songs)} YouTube lookups succeeded "
        f"({len(tracks)} kept after applying the count limit), {len(skipped)} failed — see "
        "tracks_skipped in the plan for reasons."
    )

    return {
        "producer": name,
        "genius_artist_name": artist["name"],
        "genius_artist_url": artist["url"],
        "genius_pages_searched": pages_searched,
        "tracks_found": len(tracks),
        "tracks_skipped": skipped,
        "most_recent_release_date": most_recent,
        "most_recent_release_days_ago": days_ago(most_recent),
        "tracks": tracks,
    }


def cmd_plan(args):
    token_info = get_access_token(args)
    access_token = token_info["access_token"]

    plan = {"filters": {"count": args.count, "sort": args.sort}, "producers": []}
    total = len(args.producer)
    for idx, name in enumerate(args.producer, start=1):
        log(f"=== Producer {idx}/{total}: {name} ===")
        plan["producers"].append(
            build_producer_plan(name, args.count, args.sort, args, token_info, access_token)
        )

    log(f"=== All {total} producer(s) done. Summary: ===")
    for p in plan["producers"]:
        if "error" in p:
            log(f"  {p['producer']}: ERROR — {p['error']}")
            continue
        succeeded = len(p.get("tracks", []))
        failed = len(p.get("tracks_skipped", []))
        log(f"  {p['producer']}: {succeeded} succeeded, {failed} failed")
        for f_song in p.get("tracks_skipped", []):
            log(f"    - FAILED \"{f_song['title']}\": {f_song['skip_reason']}")

    out_path = args.out
    with open(out_path, "w") as f:
        json.dump(plan, f, indent=2)
    print(json.dumps(plan, indent=2))
    print(f"\nPlan written to {out_path}", file=sys.stderr)


# --- execute --------------------------------------------------------------

def cmd_list_playlists(args):
    """List the authenticated user's existing playlists, so the caller can
    offer them as a choice instead of always creating a new one — the
    whole point being to avoid accumulating duplicate playlists across
    runs."""
    token_info = get_access_token(args)
    access_token = token_info["access_token"]
    playlists = []
    page_token = None
    while True:
        params = {"part": "snippet,contentDetails", "mine": "true", "maxResults": 50}
        if page_token:
            params["pageToken"] = page_token
        data = yt_get("playlists", access_token, params, args.timeout, retry_token_info=token_info, args=args)
        for item in data.get("items", []):
            playlists.append(
                {
                    "id": item["id"],
                    "title": item["snippet"]["title"],
                    "item_count": item["contentDetails"]["itemCount"],
                }
            )
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    print(json.dumps({"playlists": playlists}, indent=2))


def delete_all_playlist_items(access_token, playlist_id, args, token_info):
    """Used by --mode replace: clears every existing item from the target
    playlist before adding the plan's tracks, so "replace" actually means
    replace rather than append-on-top-of-whatever-was-there."""
    removed, failed = 0, []
    page_token = None
    while True:
        params = {"part": "id", "playlistId": playlist_id, "maxResults": 50}
        if page_token:
            params["pageToken"] = page_token
        data = yt_get("playlistItems", access_token, params, args.timeout, retry_token_info=token_info, args=args)
        items = data.get("items", [])
        for item in items:
            try:
                resp = requests.delete(
                    f"{YT_API_BASE}/playlistItems",
                    params={"id": item["id"]},
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=args.timeout,
                )
                if resp.ok:
                    removed += 1
                else:
                    failed.append({"playlist_item_id": item["id"], "error": resp.text})
            except requests.exceptions.Timeout:
                failed.append({"playlist_item_id": item["id"], "error": f"timed out after {args.timeout}s"})
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return removed, failed


def existing_playlist_video_ids(access_token, playlist_id, args, token_info):
    """Video IDs already sitting in the target playlist. Used by --mode merge
    so a re-run (or a track credited to more than one producer being merged
    in a later run) doesn't add a second copy of something already there."""
    video_ids = set()
    page_token = None
    while True:
        params = {"part": "contentDetails", "playlistId": playlist_id, "maxResults": 50}
        if page_token:
            params["pageToken"] = page_token
        data = yt_get("playlistItems", access_token, params, args.timeout, retry_token_info=token_info, args=args)
        for item in data.get("items", []):
            video_id = item.get("contentDetails", {}).get("videoId")
            if video_id:
                video_ids.add(video_id)
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return video_ids


def dedupe_by_video_id(tracks):
    """Keep the first occurrence of each video_id. A track credited to more
    than one producer in the same run (e.g. a collab both producers worked
    on) otherwise ends up in `all_tracks` twice and would be added to the
    playlist twice."""
    seen = set()
    deduped, dupes = [], []
    for t in tracks:
        if t["video_id"] in seen:
            dupes.append(t)
            continue
        seen.add(t["video_id"])
        deduped.append(t)
    return deduped, dupes


def cmd_execute(args):
    token_info = get_access_token(args)
    access_token = token_info["access_token"]

    with open(args.plan_file) as f:
        plan = json.load(f)

    all_tracks = [t for p in plan["producers"] if "tracks" in p for t in p["tracks"]]
    if not all_tracks:
        die("Plan has no tracks — nothing to create.")

    all_tracks, cross_producer_dupes = dedupe_by_video_id(all_tracks)
    if cross_producer_dupes:
        log(f"Skipping {len(cross_producer_dupes)} track(s) already counted for another producer in this plan: "
            + ", ".join(f'\"{t["title"]}\"' for t in cross_producer_dupes))

    removed_count, removal_failures = 0, []

    if args.mode == "create":
        producer_names = ", ".join(p["producer"] for p in plan["producers"] if "tracks" in p)
        title = (args.title or f"Produced by {producer_names}")[:150]
        try:
            resp = requests.post(
                f"{YT_API_BASE}/playlists",
                params={"part": "snippet,status"},
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json={
                    "snippet": {"title": title, "description": "Generated by mario-music-producer-playlist."},
                    "status": {"privacyStatus": args.privacy},
                },
                timeout=args.timeout,
            )
        except requests.exceptions.Timeout:
            die(f"Playlist creation timed out after {args.timeout}s. Stopping — nothing was created yet.")
        resp.raise_for_status()
        playlist_id = resp.json()["id"]
    else:
        # replace or merge: --playlist-id is required (validated below)
        playlist_id = args.playlist_id
        if args.mode == "replace":
            removed_count, removal_failures = delete_all_playlist_items(access_token, playlist_id, args, token_info)

    already_in_playlist = []
    if args.mode == "merge":
        existing_ids = existing_playlist_video_ids(access_token, playlist_id, args, token_info)
        still_to_add = []
        for t in all_tracks:
            if t["video_id"] in existing_ids:
                already_in_playlist.append(t)
            else:
                still_to_add.append(t)
        all_tracks = still_to_add
        if already_in_playlist:
            log(f"Skipping {len(already_in_playlist)} track(s) already in the target playlist: "
                + ", ".join(f'\"{t["title"]}\"' for t in already_in_playlist))

    added, failed = [], []
    for track in all_tracks:
        try:
            item_resp = requests.post(
                f"{YT_API_BASE}/playlistItems",
                params={"part": "snippet"},
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": track["video_id"]},
                    }
                },
                timeout=args.timeout,
            )
            if item_resp.ok:
                added.append(track)
            else:
                failed.append({**track, "error": item_resp.text})
        except requests.exceptions.Timeout:
            failed.append({**track, "error": f"timed out after {args.timeout}s"})

    result = {
        "playlist_id": playlist_id,
        "mode": args.mode,
        "added": len(added),
        "failed": failed,
        "skipped_duplicate_in_plan": len(cross_producer_dupes),
    }
    if args.mode == "merge":
        result["skipped_already_in_playlist"] = len(already_in_playlist)
    if args.mode == "replace":
        result["removed"] = removed_count
        result["removal_failures"] = removal_failures
    print(json.dumps(result, indent=2))
    print(f"\nhttps://music.youtube.com/playlist?list={playlist_id}")


def add_common_args(p):
    p.add_argument("--timeout", type=float, default=5, help="Per-request timeout in seconds (default 5)")
    p.add_argument("--token-cache", default=DEFAULT_TOKEN_CACHE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_auth = sub.add_parser(
        "auth", help="One-time browser consent flow (opens a real tab, no manual paste)"
    )
    p_auth.add_argument(
        "--consent-timeout",
        type=float,
        default=120,
        help="Seconds to wait for you to approve in the browser before giving up (default 120)",
    )
    p_auth.add_argument("--token-cache", default=DEFAULT_TOKEN_CACHE)
    p_auth.set_defaults(func=cmd_auth)

    p_resolve = sub.add_parser("resolve", help="Resolve a producer name to Genius artist candidates")
    p_resolve.add_argument("--producer", required=True)
    add_common_args(p_resolve)
    p_resolve.set_defaults(func=cmd_resolve)

    p_plan = sub.add_parser("plan", help="Resolve producers and build the credited-track plan (no writes)")
    p_plan.add_argument("--producer", action="append", required=True)
    p_plan.add_argument("--count", type=int, default=3)
    p_plan.add_argument("--sort", choices=["recent", "popular"], default="recent")
    p_plan.add_argument("--out", default="plan.json")
    p_plan.add_argument(
        "--youtube-search-fallback",
        action="store_true",
        default=False,
        help=(
            "Fall back to a YouTube search.list call (100 quota units) when a song has no "
            "Genius-provided video link. Off by default — a song without one is simply skipped "
            "instead of spending search quota on it."
        ),
    )
    add_common_args(p_plan)
    p_plan.set_defaults(func=cmd_plan)

    p_list_playlists = sub.add_parser(
        "list-playlists", help="List the authenticated user's existing playlists"
    )
    add_common_args(p_list_playlists)
    p_list_playlists.set_defaults(func=cmd_list_playlists)

    p_execute = sub.add_parser("execute", help="Create or update the real playlist from a saved plan")
    p_execute.add_argument("--plan-file", required=True)
    p_execute.add_argument(
        "--mode",
        choices=["create", "replace", "merge"],
        default="create",
        help=(
            "create: make a brand new playlist (default). replace: clear an existing playlist "
            "(--playlist-id) and add this plan's tracks. merge: add this plan's tracks into an "
            "existing playlist (--playlist-id) without removing what's already there."
        ),
    )
    p_execute.add_argument(
        "--playlist-id",
        default=None,
        help="Required for --mode replace|merge — the existing playlist to target. See list-playlists.",
    )
    p_execute.add_argument("--title", default=None, help="Only used with --mode create.")
    p_execute.add_argument("--privacy", choices=["private", "unlisted", "public"], default="public")
    add_common_args(p_execute)
    p_execute.set_defaults(func=cmd_execute)

    args = parser.parse_args()
    if getattr(args, "command", None) == "execute" and args.mode in ("replace", "merge") and not args.playlist_id:
        parser.error("--playlist-id is required when --mode is replace or merge")
    args.func(args)


if __name__ == "__main__":
    main()
