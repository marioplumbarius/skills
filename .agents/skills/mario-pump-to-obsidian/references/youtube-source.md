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

1. **Fetch metadata** (title, channel, upload date, video URL) with:
   ```
   yt-dlp --skip-download --print "%(title)s|||%(uploader)s|||%(upload_date)s|||%(webpage_url)s" <url>
   ```
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
5. **Extract, don't transcribe.** The note never includes the full
   transcript (see Template below). Read the cleaned transcript and pull out
   the real content: the argument, the concrete insights/decisions, named
   examples, and any direct quotes worth preserving verbatim (short,
   load-bearing lines — not paragraphs). Everything else gets paraphrased
   into prose.
6. Note every external thing the video cites that a reader might want to
   follow up on — other people, companies, tools, documents, other videos —
   so the Template's References section can cite them.

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

### 1. <insight title>
<prose explanation of the point, with a concrete example if the video gives
one.>

> "<short, load-bearing verbatim quote, only if it earns its place>"

### 2. <insight title>
...

---

## Key takeaways
1. <bullet>
2. <bullet>

## References
- [<video title> (video)](<video URL>)
- <any other external source the video cites that's worth following up on —
  articles, docs, other talks — as a markdown link>
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
- **Citations are not optional.** Every note cites its video (Summary line +
  References) and anything else it draws on, external or internal
  (`[[wikilink]]`). A drafted note with no References section is not ready
  to present.
