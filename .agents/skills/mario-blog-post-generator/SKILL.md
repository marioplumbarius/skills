---
name: mario-blog-post-generator
description: >-
  Research a topic across the web, X/Twitter, Instagram, YouTube, and images,
  then draft a cited, publish-ready blog post. Use this whenever the user
  asks to "write a blog post about X," "turn this research into a post,"
  "summarize what people are saying about X into an article," or gives a
  topic plus one or more sources (a search, a thread, a video, a set of
  posts) and wants a written piece out of it. Always confirm sort order
  (recency vs. popularity) before researching — never assume it. Produces
  Markdown by default, with inline hyperlink citations, a References list,
  and a table of contents; can add a generated hero image (with in-image
  labels in the post's own language) and an embedded YouTube iframe on
  request.
compatibility: >-
  Requires WebSearch/WebFetch for research (no dedicated X/Instagram/YouTube
  API keys needed today — see Credentials below), and the Canva MCP connector
  if a hero image is requested. Extending output format support touches this
  skill's own reference files, not an external repo.
metadata:
  author: mario
  version: "1.1"
  category: content-creation
---

# Blog Post Generator

Turn a topic and a set of sources into a cited, structured blog post. Mario
writes these regularly from social and web research — the skill exists so
every post gets the same rigor: real citations, no invented facts, no
skipped confirmation on the details that change the output.

Work through the phases in order. Do not skip Phase 4's gate.

```
- [ ] Phase 1: Gather inputs (topic, sources, sort order, format, extras)
- [ ] Phase 2: Research each source
- [ ] Phase 3: Draft the post (citations, ToC, format)
- [ ] Phase 4: Present draft for approval (GATE)
- [ ] Phase 5: Finalize + save
```

## Phase 1 — Gather inputs

Ask for whatever the user hasn't already stated. Don't silently assume a
value the user might disagree with — that's the difference between the
fields with defaults and the one field that has none.

| Input | Default | Notes |
|---|---|---|
| Topic / query | — required | The angle for the post, not just a keyword. |
| Source(s) | Web search | One or more of: web search, X/Twitter, Instagram, YouTube, images. Multiple sources are fine — research each. |
| Items per source | 5 | User can raise or lower this. Applies per source, not total. |
| Sort order | **none — must ask** | "Recency" or "popularity." Changes which 5 items you'd pick, so a wrong guess produces a materially different post. Always ask if not stated. |
| Output format | Markdown | See [references/formats.md](references/formats.md) if the user wants something else. |
| Hero image | No | If yes, exactly one image, placed at the very top of the post. Generated via Canva — see Phase 3. |
| YouTube embed | No | If yes, embed as an `<iframe>` using the standard `youtube.com/embed/<id>` pattern, placed where the video is most relevant to the text — not necessarily at the top. |

## Phase 2 — Research each source

For every source the user named, run the research and cap it at the item
limit from Phase 1, ordered by the confirmed sort order:

- **Web search (default)**: `WebSearch` for the topic; prefer results that
  are themselves citable (articles, docs, studies) over aggregator pages.
- **X/Twitter**: `WebSearch`/`WebFetch` against `site:x.com` or `site:twitter.com`,
  or a direct thread/profile URL the user gave you. Read the actual posts,
  not just search snippets.
- **Instagram**: same approach, `site:instagram.com` or a direct post/profile
  URL. Instagram often blocks unauthenticated fetches — if a post won't
  load, say so and skip it rather than guessing at its content.
- **YouTube video**: fetch the transcript/captions via `WebFetch` on the
  video URL, or search for the video first if the user only gave a topic.
  Note the video ID — you'll need it later if an iframe embed is requested.
  If the transcript genuinely won't load through available tools, say so and
  skip the video as a source rather than inventing what it says.
- **Images**: search for and view relevant images (charts, photos, screenshots)
  that support the topic; describe what they show so the draft can reference
  them accurately. This is source material, not the hero image from Phase 3.

There is no dedicated API for X, Instagram, or YouTube in this environment —
everything above runs through Claude's own search/fetch tools. If the user's
environment does have dedicated MCP tools for one of these platforms, prefer
those over `WebSearch` when available, since they'll give cleaner, more
current results.

As you gather each item, note: source URL, publish date (for recency
sorting), and engagement signal if visible (for popularity sorting) — you'll
need these to justify the sort order and to build citations later.

## Phase 3 — Draft the post

Read [references/citations.md](references/citations.md) before writing a
single citation — it defines which sources are trustworthy enough to support
a factual or scientific claim, and what to do when none qualify (drop the
claim, don't soften it into an uncited one).

Structure, in order:

1. **Title**
2. **Table of contents** — links to each `##` section below it, generated
   from the section headers you actually use. Every post gets one, regardless
   of length.
3. **Hero image**, if requested — immediately under the title/ToC, one image.
   Generate it with the Canva MCP connector (`generate-design`), not a raw
   image-generation API — this environment has no bare image-gen tool, and
   Canva also gives editable, on-brand output:
   - Write the `query` in the post's own language, and explicitly ask for any
     in-image text/labels (titles, technique names, comparison labels) to be
     in that same language — Canva's model won't infer this on its own.
   - Pick a `design_type` matching a landscape blog header (e.g.
     `youtube_thumbnail` for a clean 16:9 canvas); avoid portrait-oriented
     types.
   - `generate-design` returns several candidates. Show the user the
     candidate thumbnails/URLs and let them pick one — don't auto-select.
   - Once chosen, `create-design-from-candidate` to save it, then
     `get-export-formats` + `export-design` (type `png`) to get a download
     URL, and fetch that file locally so it can be embedded in the post
     (e.g. `![alt text](hero.png)`, with the alt text also in the post's
     language).
4. **Body** — organized under `##` sections that make sense for the topic
   (not a fixed template; a news roundup and a how-to don't share a shape).
   Cite inline at the point of use: `... as reported by [Reuters](url)`, not
   a bare link and not a footnote marker with no visible source name.
5. **YouTube embed**, if requested — placed in the section where the video
   is actually relevant, as `<iframe src="https://www.youtube.com/embed/<id>" ...></iframe>`.
6. **References** — a `##` section at the bottom listing every citation used
   in the body, in order of first appearance, each as
   `1. [Publisher/Title](url) — one-line description of what it supports`.
   Every inline citation must have a matching entry here, and vice versa —
   no orphans either direction.

Render the whole thing per [references/formats.md](references/formats.md)
for the confirmed output format.

## Phase 4 — Present draft for approval (GATE)

Show the user the full draft before saving anything. This is the moment to
catch a wrong sort order, a missing angle, or a citation that reads oddly —
much cheaper to fix here than after the file exists. Ask explicitly: does
this look right, or does anything need to change? Revise and re-show if they
ask for changes. Do not proceed to Phase 5 without a clear go-ahead.

## Phase 5 — Finalize + save

Save the approved draft to the format's file extension (e.g. `post.md`), and
the hero image file alongside it if one was generated. Report the file
path(s), word count, source count per platform, and citation count.

## Credentials

Research needs no API keys — it runs on `WebSearch`/`WebFetch`. The hero
image uses the Canva MCP connector, authenticated through the user's own
Canva connection (not a key this skill manages). If a future version adds a
dedicated X, Instagram, or YouTube API integration, its required credential
names belong in `marioplumbeer/skills` (read via the GitHub MCP), not
hardcoded into this skill or typed into chat. Cross that bridge when a real
dedicated-API source is actually added — don't invent a credentials scheme
for tools that aren't in use yet.

## Gotchas

- **Sort order has no default on purpose.** "Popular" and "recent" surface
  different items from the same search; guessing wrong means re-researching,
  not just re-sorting. Always confirm.
- **A tweet is not a scientific source.** Social posts are valid for "here's
  what people are saying" claims, never as the sole support for a factual or
  scientific claim — see [references/citations.md](references/citations.md).
- **No citation, no claim.** If nothing trustworthy backs a fact, cut the
  fact. Don't hedge it in with "reportedly" and no link.
- **Unsupported format requests get a real offer, not a refusal.** If the
  user wants a format not in [references/formats.md](references/formats.md),
  say so, offer to add support for it (a short addition to that file), do it
  once they agree, then produce the post in it.
- **One hero image, always at the top.** Don't generate more than one, and
  don't place it mid-post — that's what the source-material images from
  Phase 2 are for.
- **Hero image language must match the post.** Canva won't automatically
  write in-image labels in the post's language — say so explicitly in the
  `generate-design` query, and check the returned thumbnail before locking
  in a candidate.
- **Video ID vs. video page.** The iframe embed needs the bare video ID
  (`youtube.com/embed/VIDEO_ID`), not the full watch URL — don't paste the
  `watch?v=` link into the `src`.
