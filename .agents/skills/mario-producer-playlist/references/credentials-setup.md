# Credentials setup

Two separate credentials are required. Neither should be assumed present — check for both before running any pipeline step.

## 0. Python dependencies

```bash
pip install -r scripts/requirements.txt
```

## 1. Genius API access token

1. Go to https://genius.com/api-clients and sign in (or create a Genius account).
2. Click "New API Client", fill in any app name/URL (this is for read-only credit lookups, not a public-facing app).
3. Generate a **Client Access Token** from the client's page — this is the token needed, not the client ID/secret.
4. Export it:
   ```bash
   export GENIUS_ACCESS_TOKEN="<token>"
   ```

This token is read-only and has no write scope — it can't modify anything on Genius.

## 2. YouTube Data API v3 OAuth client

Creating and modifying playlists on a specific user's account requires OAuth (an API key alone only allows read-only calls).

1. In the [Google Cloud Console](https://console.cloud.google.com/), create or select a project.
2. Enable the **YouTube Data API v3** for that project (APIs & Services → Library).
3. Under APIs & Services → Credentials, create an **OAuth client ID** of type "Desktop app".
4. Download the resulting JSON as `client_secret.json` and note its path.
5. Export the path:
   ```bash
   export YOUTUBE_CLIENT_SECRETS="/path/to/client_secret.json"
   ```
6. The first time `scripts/build_playlist.py execute` runs, it opens a browser consent screen for the `https://www.googleapis.com/auth/youtube` scope. Approve it once — the resulting token is cached locally (see `--token-cache` in the script, defaults to `~/.cache/mario-producer-playlist/youtube_token.json`) so future runs don't re-prompt.

**This OAuth client only needs to be set up once per machine/account.** If the user already has a `client_secret.json` and cached token from a prior run, reuse them — don't walk through this setup again unless the token has expired or been revoked.

## Verifying before use

Before running Step 3 onward, confirm both are present:

```bash
test -n "$GENIUS_ACCESS_TOKEN" && echo "Genius token OK" || echo "Missing GENIUS_ACCESS_TOKEN"
test -f "$YOUTUBE_CLIENT_SECRETS" && echo "YouTube client secrets OK" || echo "Missing YOUTUBE_CLIENT_SECRETS"
```

If either is missing, stop and walk the user through the relevant section above rather than guessing a path or proceeding without it.
