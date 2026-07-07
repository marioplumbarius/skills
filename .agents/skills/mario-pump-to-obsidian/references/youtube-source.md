# Source: YouTube video

Use when the user gives a YouTube URL, or asks to "pump this video" to
Obsidian. Requires `yt-dlp` on PATH.

## Contents
- Gather context (transcript via yt-dlp)
- Destination & folder choice
- Template
- Gotchas specific to this source

## Gather context

Transcription is **mandatory** — this source type only works if a real
transcript can be pulled from the video. Never fabricate or summarize from
the title/description alone.

1. **Fetch metadata and chapters** (title, channel, upload date, video URL,
   chapter markers) with:
   ```
   yt-dlp --skip-download --print "%(title)s|||%(uploader)s|||%(upload_date)s|||%(webpage_url)s" <url>
   yt-dlp --skip-download --print "%(chapters)j" <url>
   ```
   `chapters` is `null`/empty if the uploader didn't add any — that's the
   common case, not an error.
2. **Fetch the transcript** by downloading subtitles, preferring manual
   captions and falling back to auto-generated ones:
   ```
   yt-dlp --skip-download --write-subs --write-auto-subs --sub-lang en \
     --sub-format vtt --convert-subs srt -o "<scratch-dir>/%(id)s" <url>
   ```
   Run this in a scratch/temp directory, not the vault checkout.
3. **Check yt-dlp actually produced a subtitle file.** If none exists (no
   captions in any language, private/unavailable video, yt-dlp not installed),
   **stop and tell the user** — do not proceed with a note that has no
   transcript. Offer to retry with a different `--sub-lang` if the video has
   non-English captions only.
4. **Clean the transcript**: strip VTT/SRT timestamps, cue numbers, and
   duplicate overlapping lines, but keep the spoken content verbatim — this
   cleaned transcript is working material for extraction, not something that
   goes into the note.
5. **Build the outline for `## Decisions & insights` before extracting
   content:**
   - **Chapters present** — use them as the sitemap. Each chapter becomes one
     `### N. <insight title>` subsection, in chapter order. The chapter title
     is a starting point, not a mandatory heading — rephrase it as an insight
     if the raw chapter title is a vague label (e.g. "Intro", "Q&A") rather
     than a claim; skip a chapter entirely if it has no real
     insight/decision content (throat-clearing intros, outros, filler).
   - **No chapters** — generate the same kind of outline yourself: read the
     full cleaned transcript first, identify the distinct
     arguments/decisions/beats the video makes, and turn each into its own
     `### N. <insight title>` subsection. Don't default to one subsection per
     transcript paragraph — group by idea, the way a chapter list would.
6. **Extract, don't transcribe.** The note never includes the full
   transcript (see Template below). For each subsection in the outline from
   step 5, pull out the real content: the argument, the concrete
   insight/decision, named examples, and any direct quotes worth preserving
   verbatim (short, load-bearing lines — not paragraphs). Everything else
   gets paraphrased into prose.
7. **Research citations — don't just note them, find them.** List every
   named person, company, product, quote, or claim the video mentions in
   passing without a link (e.g. "Blake Scholl, CEO of Boom Supersonic",
   "Paul Graham's well-known quote", a specific funding round). For each one,
   run a web search to find the real, specific source: the company's site,
   the original essay/post a paraphrased quote comes from, the news coverage
   of a funding round mentioned, etc. Prefer the primary source over a
   general search-results page. Skip anything you can't confidently confirm
   rather than guessing a URL.
8. **Cite inline, at the point of mention** — link the researched source
   directly on the name/claim in the prose (e.g. "...founding
   [Boom Supersonic](https://boomsupersonic.com/company/blake-scholl)..."),
   not as a separate bulleted list at the end. See Template below —
   `## References` stays reserved for the video itself and vault wikilinks.

If the video covers several distinct topics, ask the user whether to scope
the note to a specific segment before drafting.

## Destination

The vault has no `Inbox/` for video notes — real notes here live under a
topic/person folder (`people/<person-slug>/<topic-slug>.md`,
`startups/<topic-slug>.md`, `leadership/...`, etc.), one file per topic, no
date prefix, lowercase folders always. Pick the folder the same way the
existing notes do:

- If the video is centered on a specific named person (an interview, a
  profile, their stated views), use `people/<person-slug>/<topic-slug>.md`.
- Otherwise pick (or, if genuinely new, propose) the topic folder that best
  fits the subject — e.g. `startups/`, `leadership/` — matching the vault's
  existing categories before inventing a new one.
- If a note on this exact person/topic already exists, treat it as a living
  document: propose extending that file instead of creating a duplicate, and
  say so explicitly in the plan.

## Template

Modeled directly on the vault's existing video/podcast notes (e.g.
`startups/yc-startup-fundraising-myths.md`,
`people/kelsey-hightower/pragmatic-engineer-interview.md`):

```markdown
---
title: <human-readable title>
date: <YYYY-MM-DD>
tags: [<topic-tags>, <person-or-org-slug>]
---

# <title>

## Summary
<2–4 sentence distillation of the video's core argument or story — who's
speaking, what they're arguing, why it's worth keeping.>

Source: [<descriptive label — channel, series, or person>](<video URL>)

---

## Decisions & insights

<one `### N. <insight title>` per entry in the outline built in Gather
context step 5 — from the video's chapters if it has them, otherwise from
your own generated outline. Skip entries that turned out to have no real
content once you looked closer.>

### 1. <insight title>
<prose explanation of the point, with a concrete example if the video gives
one — link named people/companies/claims inline at the point of mention,
e.g. "...founding [Boom Supersonic](https://boomsupersonic.com/company/blake-scholl),
now a billion-dollar company.">

> "<short, load-bearing verbatim quote, only if it earns its place>"

### 2. <insight title>
...

---

## Key takeaways
1. <bullet>
2. <bullet>

## References
- [<video title> (video)](<video URL>)
- <[[wikilink]] to a related vault note, if one exists>
```

Drop `## Key takeaways` if `## Decisions & insights` already reads as a
complete, skimmable list on its own — it's a convenience for longer notes,
not a mandatory section.

## Gotchas specific to this source

- **No transcript, no note.** A real transcript from yt-dlp is required to
  draft the note — if captions aren't available, stop and report rather than
  drafting from the title/description alone.
- **No full transcript in the output, ever.** The transcript is extraction
  material only; the note only ever contains what was pulled from it.
- **Clean up scratch files.** Delete any subtitle files yt-dlp wrote to the
  scratch directory once the transcript has been captured into the note.
- **Citations are not optional, and the video link alone doesn't count.**
  The video itself is cited in the Summary line and `## References`. Every
  other named person/company/claim mentioned in passing (Gather context step
  7) needs a researched link **inline, in the prose where it's mentioned** —
  not bundled into References. `## References` only ever holds the video and
  `[[wikilinks]]`; if a note's prose has no inline links at all, the citation
  research step was skipped.
