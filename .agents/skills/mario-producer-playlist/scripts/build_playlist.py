#!/usr/bin/env python3
"""
Build a YouTube Music playlist from songs credited to one or more producers.

Pipeline: Genius (producer credit ground truth) -> YouTube Data API v3
(video matching, popularity ranking, playlist creation).

Subcommands:
  resolve  - find Genius artist candidates for a producer name
  plan     - build and print the confirmed track plan (no writes)
  execute  - create the real playlist from a saved plan (writes to YouTube)

See ../SKILL.md for the workflow this script is meant to be driven by, and
references/credentials-setup.md for how to obtain GENIUS_ACCESS_TOKEN and
YOUTUBE_CLIENT_SECRETS.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import requests

GENIUS_API = "https://api.genius.com"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube"]
DEFAULT_TOKEN_CACHE = os.path.expanduser(
    "~/.cache/mario-producer-playlist/youtube_token.json"
)


def genius_token():
    token = os.environ.get("GENIUS_ACCESS_TOKEN")
    if not token:
        sys.exit(
            "GENIUS_ACCESS_TOKEN is not set. See references/credentials-setup.md."
        )
    return token


def genius_get(path, params=None):
    resp = requests.get(
        f"{GENIUS_API}{path}",
        params=params or {},
        headers={"Authorization": f"Bearer {genius_token()}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def resolve_producer_candidates(name, limit=5):
    """Return plausible Genius artist candidates for a producer name."""
    data = genius_get("/search", params={"q": name})
    seen = {}
    for hit in data.get("hits", []):
        result = hit["result"]
        for artist in [result["primary_artist"]] + result.get("featured_artists", []):
            if artist["id"] not in seen and name.lower() in artist["name"].lower():
                seen[artist["id"]] = {
                    "id": artist["id"],
                    "name": artist["name"],
                    "url": artist["url"],
                }
        if len(seen) >= limit:
            break
    return list(seen.values())[:limit]


def song_matches_producer(song_id, producer_artist_id):
    """Confirm via the song detail endpoint that this song actually credits
    the producer — Genius search results merely mention a name, they don't
    confirm the producer_artists credit."""
    song = genius_get(f"/songs/{song_id}", params={"text_format": "plain"})["song"]
    producer_ids = {p["id"] for p in song.get("producer_artists", [])}
    return producer_artist_id in producer_ids, song


def within_time_window(song, time_window):
    if time_window == "all-time":
        return True
    release = song.get("release_date_components")
    if not release or not release.get("year"):
        # Unknown release date: don't silently include or exclude — treat as
        # out of window for a recency filter, since we can't confirm it.
        return False
    try:
        released = datetime(
            release["year"],
            release.get("month") or 1,
            release.get("day") or 1,
            tzinfo=timezone.utc,
        )
    except ValueError:
        return False
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    return released >= cutoff


def find_producer_candidate_songs(producer_name, producer_artist_id, time_window, want):
    """Search Genius broadly, confirm producer credit per song, filter by
    time window. Paginates until `want` confirmed matches or search is
    exhausted."""
    confirmed = []
    seen_song_ids = set()
    page = 1
    max_pages = 10  # backstop against unbounded pagination
    while len(confirmed) < want and page <= max_pages:
        data = genius_get("/search", params={"q": producer_name, "page": page})
        hits = data.get("hits", [])
        if not hits:
            break
        for hit in hits:
            result = hit["result"]
            song_id = result["id"]
            if song_id in seen_song_ids:
                continue
            seen_song_ids.add(song_id)
            is_match, song = song_matches_producer(song_id, producer_artist_id)
            if not is_match:
                continue
            if not within_time_window(song, time_window):
                continue
            confirmed.append(
                {
                    "genius_song_id": song_id,
                    "title": song["title"],
                    "primary_artist": song["primary_artist"]["name"],
                    "url": song["url"],
                    "release_date": song.get("release_date"),
                }
            )
            if len(confirmed) >= want:
                break
        page += 1
    return confirmed


def youtube_client():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    client_secrets = os.environ.get("YOUTUBE_CLIENT_SECRETS")
    if not client_secrets or not os.path.isfile(client_secrets):
        sys.exit(
            "YOUTUBE_CLIENT_SECRETS is not set or file not found. "
            "See references/credentials-setup.md."
        )

    token_cache = os.environ.get("YOUTUBE_TOKEN_CACHE", DEFAULT_TOKEN_CACHE)
    os.makedirs(os.path.dirname(token_cache), exist_ok=True)

    creds = None
    if os.path.exists(token_cache):
        creds = Credentials.from_authorized_user_file(token_cache, YOUTUBE_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets, YOUTUBE_SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_cache, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def best_youtube_match(yt, artist, title, region):
    query = f"{artist} - {title}"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "videoCategoryId": "10",  # Music
        "maxResults": 5,
    }
    if region and region != "global":
        params["regionCode"] = region
    search = yt.search().list(**params).execute()
    items = search.get("items", [])
    if not items:
        return None

    video_ids = [item["id"]["videoId"] for item in items]
    stats = yt.videos().list(part="statistics,snippet", id=",".join(video_ids)).execute()
    ranked = sorted(
        stats.get("items", []),
        key=lambda v: int(v["statistics"].get("viewCount", 0)),
        reverse=True,
    )
    if not ranked:
        return None
    top = ranked[0]
    return {
        "video_id": top["id"],
        "title": top["snippet"]["title"],
        "view_count": int(top["statistics"].get("viewCount", 0)),
    }


def cmd_resolve(args):
    candidates = resolve_producer_candidates(args.producer)
    if not candidates:
        print(json.dumps({"producer": args.producer, "candidates": []}, indent=2))
        sys.exit(f"No Genius artist candidates found for '{args.producer}'.")
    print(json.dumps({"producer": args.producer, "candidates": candidates}, indent=2))


def cmd_plan(args):
    plan = {"filters": {"time_window": args.time_window, "region": args.region}, "producers": []}
    for producer_id, producer_name in zip(args.producer_id, args.producer_name):
        candidates = find_producer_candidate_songs(
            producer_name, producer_id, args.time_window, args.count
        )
        entry = {"producer_id": producer_id, "producer_name": producer_name, "tracks": [], "skipped": []}
        yt = None
        for song in candidates:
            try:
                if yt is None:
                    yt = youtube_client()
                match = best_youtube_match(yt, song["primary_artist"], song["title"], args.region)
            except Exception as exc:  # network/auth errors shouldn't kill the whole plan
                match = None
                song["skip_reason"] = f"YouTube lookup failed: {exc}"
            if match:
                entry["tracks"].append({**song, **match})
            else:
                song.setdefault("skip_reason", "No YouTube match found")
                entry["skipped"].append(song)
        entry["tracks"].sort(key=lambda t: t["view_count"], reverse=True)
        entry["tracks"] = entry["tracks"][: args.count]
        plan["producers"].append(entry)

    out_path = args.out or "plan.json"
    with open(out_path, "w") as f:
        json.dump(plan, f, indent=2)
    print(json.dumps(plan, indent=2))
    print(f"\nPlan written to {out_path}", file=sys.stderr)


def cmd_execute(args):
    with open(args.plan_file) as f:
        plan = json.load(f)

    yt = youtube_client()

    all_tracks = [t for p in plan["producers"] for t in p["tracks"]]
    if not all_tracks:
        sys.exit("Plan has no confirmed tracks — nothing to create.")

    producer_names = ", ".join(p["producer_name"] for p in plan["producers"])
    title = args.title or f"Produced by {producer_names}"

    playlist = (
        yt.playlists()
        .insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title[:150],
                    "description": "Generated by mario-producer-playlist.",
                },
                "status": {"privacyStatus": args.privacy},
            },
        )
        .execute()
    )
    playlist_id = playlist["id"]

    added, failed = [], []
    for track in all_tracks:
        try:
            yt.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": track["video_id"]},
                    }
                },
            ).execute()
            added.append(track)
        except Exception as exc:
            failed.append({**track, "error": str(exc)})

    print(json.dumps({"playlist_id": playlist_id, "added": len(added), "failed": failed}, indent=2))
    print(f"\nhttps://music.youtube.com/playlist?list={playlist_id}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_resolve = sub.add_parser("resolve", help="Find Genius artist candidates for a producer name")
    p_resolve.add_argument("--producer", required=True)
    p_resolve.set_defaults(func=cmd_resolve)

    p_plan = sub.add_parser("plan", help="Build the confirmed track plan (no writes)")
    p_plan.add_argument("--producer-id", type=int, action="append", required=True)
    p_plan.add_argument("--producer-name", action="append", required=True, help="Must align 1:1 with --producer-id")
    p_plan.add_argument("--count", type=int, default=10)
    p_plan.add_argument("--time-window", choices=["last-7-days", "all-time"], default="last-7-days")
    p_plan.add_argument("--region", default="global")
    p_plan.add_argument("--out", default="plan.json")
    p_plan.set_defaults(func=cmd_plan)

    p_execute = sub.add_parser("execute", help="Create the real playlist from a saved plan")
    p_execute.add_argument("--plan-file", required=True)
    p_execute.add_argument("--title", default=None)
    p_execute.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    p_execute.set_defaults(func=cmd_execute)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
