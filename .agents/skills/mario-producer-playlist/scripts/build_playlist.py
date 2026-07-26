#!/usr/bin/env python3
"""
Build a YouTube Music playlist from songs released by one or more producers,
using YouTube itself as the only source of truth (no external credit DB).

Producer name -> YouTube channel identity is inherently ambiguous (common
names, fan channels, VEVO channels, etc.), so the core job here is
disambiguation: search for channels matching the name, keep only the ones
YouTube itself categorizes as Music, and pick the one with the most
subscribers. That's it — simple and cheap, no fuzzy scoring beyond that.

Every network call has a hard timeout (default 5s). A timeout aborts the
run with a clear message instead of retrying or silently degrading — the
caller (the agent driving this script) is expected to stop and ask the
user what to do next, per mario-producer-playlist/SKILL.md.

Subcommands:
  auth  resolve  plan  execute
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import requests

API_BASE = "https://www.googleapis.com/youtube/v3"
TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/youtube"
DEFAULT_TOKEN_CACHE = os.path.expanduser("~/.cache/mario-producer-playlist/youtube_token.json")


def die(msg):
    sys.exit(msg)


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


def api_get(path, access_token, params, timeout, retry_token_info=None, args=None):
    resp = requests.get(
        f"{API_BASE}/{path}",
        params=params,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=timeout,
    )
    if resp.status_code == 401 and retry_token_info is not None:
        refreshed = refresh_access_token(retry_token_info, timeout)
        save_token(args.token_cache, refreshed)
        resp = requests.get(
            f"{API_BASE}/{path}",
            params=params,
            headers={"Authorization": f"Bearer {refreshed['access_token']}"},
            timeout=timeout,
        )
    resp.raise_for_status()
    return resp.json()


# --- auth ---------------------------------------------------------------
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


# --- resolve --------------------------------------------------------------

MUSIC_TOPIC_HINT = "music"


def is_music_channel(channel):
    categories = channel.get("topicDetails", {}).get("topicCategories", [])
    return any(MUSIC_TOPIC_HINT in cat.lower() for cat in categories)


def channel_subs(channel):
    stats = channel.get("statistics", {})
    if stats.get("hiddenSubscriberCount"):
        return 0
    try:
        return int(stats.get("subscriberCount", 0))
    except ValueError:
        return 0


def channel_url(channel):
    custom_url = channel.get("snippet", {}).get("customUrl")
    if custom_url:
        handle = custom_url if custom_url.startswith("@") else f"@{custom_url}"
        return f"https://www.youtube.com/{handle}"
    return f"https://www.youtube.com/channel/{channel['id']}"


def video_url(video_id):
    return f"https://music.youtube.com/watch?v={video_id}"


def days_ago(iso_timestamp):
    if not iso_timestamp:
        return None
    published = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - published).days


def find_topic_channel(channels, winner):
    """Find the artist's auto-generated "<Name> - Topic" channel among the
    search candidates. Matches by the "- Topic" suffix + Music tagging
    rather than exact name equality, because YouTube's auto-generated
    channel sometimes uses a shortened stage name (e.g. "Pharrell - Topic"
    for "Pharrell Williams"). Ranks by subscriber count in case of
    impostor/copycat channels squatting on the same "- Topic" title."""
    winner_title = winner["snippet"]["title"].strip()
    if winner_title.lower().endswith("- topic"):
        return winner
    candidates = [
        c
        for c in channels
        if c["id"] != winner["id"]
        and c["snippet"]["title"].strip().lower().endswith("- topic")
        and is_music_channel(c)
    ]
    if not candidates:
        return None
    return max(candidates, key=channel_subs)


def cmd_resolve(args):
    token_info = get_access_token(args)
    access_token = token_info["access_token"]

    def call(path, params):
        return api_get(path, access_token, params, args.timeout, retry_token_info=token_info, args=args)

    try:
        search = call(
            "search",
            {"part": "snippet", "q": args.producer, "type": "channel", "maxResults": 10},
        )
    except requests.exceptions.Timeout:
        die(
            f"YouTube channel search for '{args.producer}' timed out after {args.timeout}s. "
            "Stopping — tell me how you'd like to proceed."
        )

    candidate_ids = [item["id"]["channelId"] for item in search.get("items", [])]
    if not candidate_ids:
        die(f"No YouTube channels found for '{args.producer}'.")

    try:
        details = call(
            "channels",
            {"part": "snippet,statistics,topicDetails", "id": ",".join(candidate_ids)},
        )
    except requests.exceptions.Timeout:
        die(f"YouTube channel lookup timed out after {args.timeout}s. Stopping — tell me how you'd like to proceed.")

    channels = details.get("items", [])
    music_channels = [c for c in channels if is_music_channel(c)]

    if not music_channels:
        die(
            f"None of the channels found for '{args.producer}' are tagged as Music on YouTube. "
            "Candidates were: " + ", ".join(c["snippet"]["title"] for c in channels)
        )

    winner = max(music_channels, key=channel_subs)
    winner_title = winner["snippet"]["title"]
    topic_channel = find_topic_channel(channels, winner)

    result = {
        "producer": args.producer,
        "resolved_channel_id": winner["id"],
        "resolved_channel_title": winner_title,
        "resolved_subscriber_count": channel_subs(winner),
        "track_source_channel_id": (topic_channel or winner)["id"],
        "track_source_channel_title": (topic_channel or winner)["snippet"]["title"],
        "candidates_considered": [
            {
                "id": c["id"],
                "title": c["snippet"]["title"],
                "subscriber_count": channel_subs(c),
                "is_music_channel": is_music_channel(c),
            }
            for c in channels
        ],
    }
    print(json.dumps(result, indent=2))


# --- tracks / plan --------------------------------------------------------

def fetch_tracks(access_token, channel_id, count, sort, args, token_info):
    order = "viewCount" if sort == "popular" else "date"

    def call(path, params):
        return api_get(path, access_token, params, args.timeout, retry_token_info=token_info, args=args)

    try:
        search = call(
            "search",
            {
                "part": "snippet",
                "channelId": channel_id,
                "type": "video",
                "order": order,
                "maxResults": count,
                "videoCategoryId": "10",
            },
        )
    except requests.exceptions.Timeout:
        die(f"YouTube video search for channel {channel_id} timed out after {args.timeout}s. Stopping.")

    items = search.get("items", [])
    video_ids = [i["id"]["videoId"] for i in items if "videoId" in i.get("id", {})]
    if not video_ids:
        return []

    try:
        stats = call("videos", {"part": "statistics,snippet", "id": ",".join(video_ids)})
    except requests.exceptions.Timeout:
        die(f"YouTube video stats lookup timed out after {args.timeout}s. Stopping.")

    stats_by_id = {v["id"]: v for v in stats.get("items", [])}
    tracks = []
    for i in items:
        vid = i.get("id", {}).get("videoId")
        if not vid or vid not in stats_by_id:
            continue
        v = stats_by_id[vid]
        tracks.append(
            {
                "video_id": vid,
                "title": v["snippet"]["title"],
                "published_at": v["snippet"]["publishedAt"],
                "view_count": int(v["statistics"].get("viewCount", 0)),
                "url": video_url(vid),
            }
        )
    return tracks[:count]


def cmd_plan(args):
    token_info = get_access_token(args)
    access_token = token_info["access_token"]

    plan = {"filters": {"count": args.count, "sort": args.sort}, "producers": []}
    for name in args.producer:
        try:
            search = api_get(
                "search",
                access_token,
                {"part": "snippet", "q": name, "type": "channel", "maxResults": 10},
                args.timeout,
                retry_token_info=token_info,
                args=args,
            )
        except requests.exceptions.Timeout:
            die(f"YouTube channel search for '{name}' timed out after {args.timeout}s. Stopping.")

        candidate_ids = [item["id"]["channelId"] for item in search.get("items", [])]
        if not candidate_ids:
            plan["producers"].append({"producer": name, "error": "No YouTube channels found."})
            continue

        details = api_get(
            "channels",
            access_token,
            {"part": "snippet,statistics,topicDetails", "id": ",".join(candidate_ids)},
            args.timeout,
            retry_token_info=token_info,
            args=args,
        )
        channels = details.get("items", [])
        music_channels = [c for c in channels if is_music_channel(c)]
        if not music_channels:
            plan["producers"].append(
                {"producer": name, "error": "No candidate channel is tagged as Music."}
            )
            continue

        winner = max(music_channels, key=channel_subs)
        winner_title = winner["snippet"]["title"]
        topic_channel = find_topic_channel(channels, winner)
        source = topic_channel or winner

        tracks = fetch_tracks(access_token, source["id"], args.count, args.sort, args, token_info)
        most_recent = max((t["published_at"] for t in tracks), default=None)

        plan["producers"].append(
            {
                "producer": name,
                "resolved_channel_title": winner_title,
                "resolved_channel_url": channel_url(winner),
                "resolved_subscriber_count": channel_subs(winner),
                "track_source_channel_title": source["snippet"]["title"],
                "track_source_channel_url": channel_url(source),
                "tracks_found": len(tracks),
                "most_recent_release_date": most_recent,
                "most_recent_release_days_ago": days_ago(most_recent),
                "tracks": tracks,
            }
        )

    out_path = args.out
    with open(out_path, "w") as f:
        json.dump(plan, f, indent=2)
    print(json.dumps(plan, indent=2))
    print(f"\nPlan written to {out_path}", file=sys.stderr)


# --- execute --------------------------------------------------------------

def cmd_execute(args):
    token_info = get_access_token(args)
    access_token = token_info["access_token"]

    with open(args.plan_file) as f:
        plan = json.load(f)

    all_tracks = [t for p in plan["producers"] if "tracks" in p for t in p["tracks"]]
    if not all_tracks:
        die("Plan has no tracks — nothing to create.")

    producer_names = ", ".join(p["producer"] for p in plan["producers"] if "tracks" in p)
    title = (args.title or f"Produced by {producer_names}")[:150]

    try:
        resp = requests.post(
            f"{API_BASE}/playlists",
            params={"part": "snippet,status"},
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json={
                "snippet": {"title": title, "description": "Generated by mario-producer-playlist."},
                "status": {"privacyStatus": args.privacy},
            },
            timeout=args.timeout,
        )
    except requests.exceptions.Timeout:
        die(f"Playlist creation timed out after {args.timeout}s. Stopping — nothing was created yet.")
    resp.raise_for_status()
    playlist_id = resp.json()["id"]

    added, failed = [], []
    for track in all_tracks:
        try:
            item_resp = requests.post(
                f"{API_BASE}/playlistItems",
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

    print(json.dumps({"playlist_id": playlist_id, "added": len(added), "failed": failed}, indent=2))
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

    p_resolve = sub.add_parser("resolve", help="Resolve a producer name to a YouTube channel")
    p_resolve.add_argument("--producer", required=True)
    add_common_args(p_resolve)
    p_resolve.set_defaults(func=cmd_resolve)

    p_plan = sub.add_parser("plan", help="Resolve producers and build the track plan (no writes)")
    p_plan.add_argument("--producer", action="append", required=True)
    p_plan.add_argument("--count", type=int, default=10)
    p_plan.add_argument("--sort", choices=["recent", "popular"], default="recent")
    p_plan.add_argument("--out", default="plan.json")
    add_common_args(p_plan)
    p_plan.set_defaults(func=cmd_plan)

    p_execute = sub.add_parser("execute", help="Create the real playlist from a saved plan")
    p_execute.add_argument("--plan-file", required=True)
    p_execute.add_argument("--title", default=None)
    p_execute.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    add_common_args(p_execute)
    p_execute.set_defaults(func=cmd_execute)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
