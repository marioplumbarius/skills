# One-time credential setup

Substack has no official API and no OAuth flow for third-party publishing, so
authentication piggybacks on the same session cookie the browser uses. This
is a one-time setup per machine/account.

## 1. Get the `substack.sid` cookie

1. Log into the target Substack publication in a normal browser, as the
   account that owns/co-authors it.
2. Open DevTools → Application (Chrome) or Storage (Firefox) → Cookies →
   `https://substack.com`.
3. Find the cookie named `substack.sid` and copy its value.

Do this in the browser, not through this agent — the value should never pass
through chat.

## 2. Save it locally, outside the repo

Create (or have the user create) `~/.config/plumbeer/substack/cookies.json`:

```json
{
  "substack.sid": "<the cookie value>"
}
```

And `~/.config/plumbeer/substack/config.json`:

```json
{
  "publication_url": "https://<subdomain>.substack.com"
}
```

Set restrictive permissions:

```bash
chmod 600 ~/.config/plumbeer/substack/cookies.json
```

## 3. Verify

Run a read-only check before attempting any writes:

```python
from substack import Api

api = Api(
    publication_url="https://<subdomain>.substack.com",
    cookies_path="~/.config/plumbeer/substack/cookies.json",
)
print(api.get_publication_users())  # any read-only call works
```

If this raises 401/403, the cookie is invalid or expired — redo step 1.

## Cookie expiry

Substack session cookies are long-lived but not permanent. If a publish
attempt suddenly starts failing auth after previously working, the fix is
almost always: log in again in the browser, re-copy `substack.sid`, replace
the value in `cookies.json`. Don't try to work around an auth failure any
other way.
