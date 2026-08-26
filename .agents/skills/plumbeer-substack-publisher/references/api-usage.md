# python-substack call pattern

Install once: `pip install python-substack`

## Create a draft from markdown

```python
from substack import Api

api = Api(
    publication_url="https://<subdomain>.substack.com",
    cookies_path="~/.config/plumbeer/substack/cookies.json",
)

result = api.create_draft_from_markdown(
    title="<title>",
    subtitle="<subtitle or None>",
    markdown="<full markdown body>",
    tags=["<tag1>", "<tag2>"],       # optional
    cover_image="<local path or URL>",  # optional
    api=api,                          # required for local image uploads to attach
)

draft_id = result["draft"]["id"]
draft_url = f"https://<subdomain>.substack.com/publish/post/{draft_id}"
```

Report `draft_id` and `draft_url` back to the user after this call —
this is the deliverable of Phase 4, and the deliverable of this skill.

**Do not call `publish_draft` or any other send/publish/email endpoint.**
This skill is draft-only by design; going live is left entirely to the user,
from the Substack editor.

## Error handling

- **401/403** → cookie expired or wrong publication. Point back to
  `references/setup.md`, do not retry with modified headers.
- **400 on draft creation** → usually a missing required field (title is
  mandatory; some versions require at least one byline — pass
  `draft_bylines` if the library version requires it, defaulting to the
  authenticated user's own byline).
- **Unexpected response shape** (KeyError, schema mismatch) → the unofficial
  API likely changed. Report the raw response/error to the user rather than
  guessing a workaround.
