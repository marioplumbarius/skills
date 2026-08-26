# One-time credential setup

Substack has no official API and no OAuth flow for third-party publishing, so
authentication piggybacks on the same session cookie the browser uses. This
is a one-time setup per machine/account.

## 1. Get the `substack.sid` cookie

**macOS + Firefox:** log into the target Substack publication first, then
run [../scripts/extract_firefox_cookie.py](../scripts/extract_firefox_cookie.py):

```bash
python3 <path-to-skill>/scripts/extract_firefox_cookie.py
```

It auto-detects the default Firefox profile, reads a copy of
`cookies.sqlite` (works fine with Firefox still open), and writes
`~/.config/plumbeer/substack/cookies.json` directly — the cookie value is
never printed or passed through chat. Pass `--profile <path>` if you have
multiple profiles and the wrong one gets picked.

The script checks it's running on macOS with Firefox actually installed and
stops immediately with an explanation if not — it won't install Firefox or
try to guess where another OS/browser keeps its cookies. On any other
platform, or a different browser, skip straight to the manual steps below.

**Any other platform/browser:** do it manually —

1. Log into the target Substack publication in a normal browser, as the
   account that owns/co-authors it.
2. Open DevTools → Application (Chrome) or Storage (other browsers) →
   Cookies → `https://substack.com`.
3. Find the cookie named `substack.sid` and copy its value.
4. Save it yourself into `~/.config/plumbeer/substack/cookies.json` (below)
   — do this in the browser/terminal, not through chat; the value should
   never pass through the agent.

## 2. Save the publication URL

If you used the script above, `cookies.json` is already in place — this
step just needs `config.json` too. If you did the manual path, create
`~/.config/plumbeer/substack/cookies.json` yourself:

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

Requires `python-substack` (`pip install python-substack`; on Homebrew
Python this needs a venv — see the SKILL.md Gotchas). Run a read-only check
before attempting any writes:

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
