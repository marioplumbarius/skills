---
name: plumbeer-article-reference-finder
description: >-
  Read an article (from a URL, pasted text, or a local file) and find
  external, independently-sourced references that support, relate to, or
  contradict what it says — not just the links the article already cites.
  Use this whenever the user says "find references for this article," "what
  sources back this up," "fact-check this piece," "find further reading for
  X article," or hands over an article/link and wants a sourced list of what
  backs it up. Always ask which categories to extract first — named people
  and named organizations by default, with factual claims/statistics and the
  article's own existing citations as opt-in extras. For every person named
  in the article, prefer linking to their Wikipedia page over any other
  source. Produces a numbered reference list plus a table mapping each
  article mention to the reference found and how it matches.
compatibility: >-
  Requires WebFetch (to read a URL) and WebSearch (to find external
  references). Reads pasted text or local files directly — no special
  compatibility needed for those input types.
metadata:
  author: plumbeer
  version: "1.0"
  category: research
---

# Article Reference Finder

Plumbeer uses this to fact-check and enrich articles before publishing or
sharing them: read the piece, pull out its claims and named people, then find
independent sources — Wikipedia for people, the best available source for
everything else — and show exactly how each reference matches what the
article says. The output is a citation list a human can drop straight into a
References section.

This skill finds **external supporting/related sources**, not the links the
article already contains. If the article cites its own sources inline (and
the user opted into that category in Phase 2), note them separately — the
deliverable is the independently-found reference table (Phases 4–5).

```
- [ ] Phase 1: Get the article
- [ ] Phase 2: Confirm what to extract
- [ ] Phase 3: Extract claims and named entities
- [ ] Phase 4: Find a reference for each
- [ ] Phase 5: Build the list + table
- [ ] Phase 6: Present for review
```

## Phase 1 — Get the article

Accept any of:
- **URL** — fetch with `WebFetch`. If the page is paywalled or won't render
  (common on some news/Substack sites), say so and ask the user to paste the
  text instead rather than guessing at the content.
- **Pasted text** — use as-is.
- **Local file** — `Read` it. Handle `.md`/`.txt` directly; for `.pdf` or
  `.docx`, use the matching bundled skill (`pdf`, `docx`) to extract text
  first if a direct read doesn't give clean text.

Confirm you have the full article, not a truncated excerpt, before moving on
— a partial read produces a partial (and misleading) reference list.

## Phase 2 — Confirm what to extract

Ask the user which categories to extract before reading for content. Default
— if the user doesn't say, or says something like "just do the usual" —
is **named people + named organizations only**. Offer the rest as opt-in:

- **Named people** (default on)
- **Named organizations, places, or works** (default on)
- **Factual claims and statistics** (opt-in)
- **Existing citations already in the article** (opt-in — separate bookkeeping,
  see Phase 3 step 4)

Don't silently expand scope: a user who asked for "references for this
article" without specifying gets people + orgs only, not a full fact-check.
If they ask to add a category mid-run, extend Phase 3 onward for the new
category without re-doing work already confirmed for the others.

## Phase 3 — Extract claims and named entities

Go through the article once and list, in order of appearance, only the
categories confirmed in Phase 2:

1. **Named people** — every person mentioned by name. Highest priority
   category when included (see Phase 4: Wikipedia-first sourcing).
2. **Named organizations, places, or works** — companies, institutions,
   books, papers — anything a reader might want a reference for.
3. **Factual claims** — statistics, studies, historical facts, quotes
   attributed to a source, or specific events described as fact. Only if the
   user opted in.
4. **Existing citations** — any links or attributions the article already
   makes. Only if the user opted in. Keep these separate from your findings;
   don't re-present the article's own links as if you found them
   independently.

Skip generic statements with nothing concrete to source (opinions, framing,
transitions) — every row in the final table must trace to a specific claim or
name in the text.

## Phase 4 — Find a reference for each

Read [references/sourcing.md](references/sourcing.md) before searching — it
has the per-category sourcing rules and quality bar. In short:

- **Named people → Wikipedia first.** Search `<name> wikipedia` and use the
  Wikipedia article if one exists and is clearly the same person (check
  context — occupation, era, nationality — to avoid linking the wrong person
  with a shared name). Only fall back to another source (official bio,
  reputable news profile) when no Wikipedia page exists.
- **Factual claims / statistics → the original or most authoritative source.**
  Prefer the primary source (the study, the government dataset, the official
  report) over a news article summarizing it. If the article already names
  the source ("according to a 2023 WHO report"), find that exact source
  rather than a generic substitute.
- **Organizations / places / works → their Wikipedia page or official site**,
  whichever gives the reader more useful context for this article's mention.

Every reference must be a real, verifiable link found via `WebSearch`/
`WebFetch` — never invent a URL or an article title. If nothing credible
turns up for a claim, say so explicitly in the output instead of forcing a
weak or irrelevant match.

## Phase 5 — Build the list + table

Produce two things, in this order:

1. **Numbered reference list** — every distinct source found, deduplicated
   (the same person or study referenced twice in the article gets one entry):
   ```
   1. [Full Name – Wikipedia](url)
   2. [Study/Report Title – Publisher](url)
   ```
2. **Matching table** — one row per article mention, referencing the list
   above by number:

   | # | Article mentions | Reference | How it matches |
   |---|---|---|---|
   | 1 | "Jane Doe, the lead researcher..." | [Jane Doe – Wikipedia](url) | Identifies the person named in the article |
   | 2 | "...a 40% increase since 2019" | [Original Report – Publisher](url) | Primary source for the statistic cited |

   Keep "How it matches" specific — name the exact claim or phrase being
   backed, not a vague "related to this topic."

If a claim or name had no credible reference found, still list it in the
table with the Reference column marked "No credible source found" — don't
drop it silently.

## Phase 6 — Present for review

Show the full list and table to the user before saving anything to a file.
Ask if any match looks wrong (wrong person, weak source, missed claim) and
revise before finalizing. Only write the output to a file if the user asks
for one.

## Gotchas

- **Default scope is people + organizations only.** Don't extend to factual
  claims or existing citations unless the user opts in during Phase 2 — a
  full fact-check is a bigger job than a "who's mentioned here" pass, and
  assuming the bigger scope wastes searches the user didn't ask for.
- **Wikipedia disambiguation is the most common failure mode.** A common
  name (or a name shared with someone more famous) can silently link to the
  wrong person. Always verify against context in the article — occupation,
  organization, time period — before locking in a Wikipedia match.
- **Don't re-badge the article's own citations as your findings.** If the
  article already links to a source, that's bookkeeping (Phase 3, step 4),
  not an independent discovery — keep the two visually distinct if both
  appear in output.
- **No source found is a valid, reportable outcome.** Forcing a tenuous match
  to fill every row is worse than an honest "no credible source found."
- **Primary over secondary.** When a claim traces to a specific study or
  report, link that document itself, not a news article that merely mentions
  it — unless the primary source is unavailable.
- **A partial article read produces a partial reference list.** Confirm the
  fetch/paste actually captured the whole piece (watch for paywalls,
  truncated fetches, or "read more" cutoffs) before extracting claims.
