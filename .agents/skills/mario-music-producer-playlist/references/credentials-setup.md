# Credentials setup

Two credentials are required: a Genius API access token (producer-credit source of truth) and a YouTube Data API v3 OAuth client (matching + playlist creation).

## 0. Python dependencies

```bash
pip install -r scripts/requirements.txt
```

## 1. Genius API access token

1. Go to [genius.com/api-clients](https://genius.com/api-clients), sign in, click "New API Client" (any app name/URL works — this is for read-only credit lookups).
2. Generate a **Client Access Token** from the client's page.
3. Export it:
   ```bash
   export GENIUS_ACCESS_TOKEN="<token>"
   ```

This token is read-only and has no write scope.

## 2. YouTube Data API v3 OAuth client

Reading public data (search, channel/video lookups) is possible with a plain API key, but **creating a playlist writes to a specific user's own account**, which Google's platform requires real OAuth user consent for — there's no API-key-only or client-secret-only path around this. It only needs to happen once per machine.

1. In the [Google Cloud Console](https://console.cloud.google.com/), create or select a project.
2. Enable the **YouTube Data API v3** for that project (APIs & Services → Library).
3. Under APIs & Services → Credentials, create an **OAuth client ID** of type "Desktop app". Download the JSON.
4. If the OAuth consent screen is in "Testing" publishing status (the common case for a personal project), add the account you'll authorize with under **Audience → Test users** (this section moved out of the old "OAuth consent screen" page in Google's newer Auth Platform UI — look under **Audience**, not "Verification Center").
5. Export the downloaded JSON's path:
   ```bash
   export YOUTUBE_CLIENT_SECRETS="/path/to/client_secret.json"
   ```

## 3. Run the one-time browser auth

```bash
python scripts/build_playlist.py auth
```

This opens a real browser tab for the user to approve access, then caches the resulting refresh token (default `~/.cache/mario-music-producer-playlist/youtube_token.json`). Every later command reuses it silently — no more browser steps, and expired access tokens are refreshed automatically.

**If this hangs or fails almost instantly:** the root cause we diagnosed once already is `localhost` resolving to IPv6 `::1` before IPv4 `127.0.0.1` — a browser navigating to `http://localhost:<port>/` can end up trying an address nothing is actually listening on. `build_playlist.py auth` already binds explicitly to `127.0.0.1` for both the callback server and the redirect URI to avoid this; if it ever recurs, verify with:
```bash
python3 -c "import socket; print(socket.getaddrinfo('localhost', 0))"
```
and confirm the auth flow is still binding to `127.0.0.1`, not `localhost`, before reaching for a workaround (e.g. a manual copy-paste flow) — that's treating a symptom, not the cause.

**This OAuth client and its cached token only need to be set up once.** If a valid token is already cached, skip straight to using `resolve` / `plan` / `execute`.

## A note on YouTube Data API quota

The free daily quota is 10,000 units, and `search.list` costs 100 units per call — meaning **exactly 100 searches per day**, by default, for every project. `plan` calls `search.list` once per confirmed Genius credit per producer, so a handful of full runs can exhaust it. A `429` with `reason: rateLimitExceeded` and `quota_metric: youtube.googleapis.com/search_list` in the response body means the daily quota is exhausted, not a transient burst limit — no retry or backoff fixes this; only the midnight Pacific reset does, or a quota increase request (free to submit at [Google Cloud Console → IAM & Admin → Quotas](https://console.cloud.google.com/iam-admin/quotas), but manually reviewed and not a same-day fix).

## Verifying before use

```bash
test -n "$GENIUS_ACCESS_TOKEN" && echo "Genius token OK" || echo "Missing GENIUS_ACCESS_TOKEN"
test -n "$YOUTUBE_CLIENT_SECRETS" && test -f "$YOUTUBE_CLIENT_SECRETS" && echo "YouTube client secrets OK" || echo "Missing YOUTUBE_CLIENT_SECRETS"
test -f ~/.cache/mario-music-producer-playlist/youtube_token.json && echo "Cached token found (auth already done)" || echo "No cached token — run 'auth' first"
```
