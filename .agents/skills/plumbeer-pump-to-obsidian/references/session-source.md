# Source: Claude session

Use when the source is the **current Claude session** (Claude Code, cowork,
or chat) — this is the default when no other source is named.

## Gather context

Pull from **this session's** conversation and tool history. Do not invent
content — only capture what actually happened or was discussed. Default scope:

- **Decisions & insights** — key conclusions, takeaways, choices made and the
  reasoning behind them.
- **Code & commands** — relevant snippets, commands run, and file changes worth
  remembering. Keep them runnable; fence with the right language.
- **Open questions / TODOs** — unresolved threads and follow-up actions.

Skip the full verbatim transcript unless the user explicitly asks for it.

If the session is long or covers several topics, ask the user whether to scope
the note to a specific topic before drafting.

## Destination

`Inbox/YYYY-MM-DD-<kebab-slug>.md` using today's date and a short slug from
the topic (e.g. `Inbox/2026-05-29-retry-backoff-design.md`). If a file with
that exact path already exists, append a short disambiguator (`-2`, `-3`)
rather than overwriting.

## Template

```markdown
---
title: <human-readable title>
date: <YYYY-MM-DD>
source: <URL of the source — leave empty if there is no URL>
tags: [from-claude, <topic-tags>]
---

# <title>

## Summary
<2–4 sentence distillation of what this session was about.>

## Decisions & insights
- <decision/insight + brief why>

## Code & commands
```<lang>
<snippet>
```

## Open questions / TODOs
- [ ] <follow-up>

## References
- <links, file paths, PRs, or [[wikilinks]] to related notes>
```

Drop any section that has no real content — don't ship empty headers.
