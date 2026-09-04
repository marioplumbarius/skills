---
name: plumbeer-video-metadata-tagger
description: >-
  Watch a video file to figure out what it actually shows, then write a confirmed
  description into the file's embedded metadata and rename it (or a copy) using a
  topic-language-timestamp convention. Use whenever the user says "figure out what this
  video is about," "add a description to this video," "tag this video's metadata," "rename
  this video based on its content," or hands over an unlabeled clip (e.g. from a Google
  Takeout export, phone backup, or camera roll dump) and wants it identified and organized.
  Combines frame extraction, multimodal frame reading, and optional audio transcription via
  the plumbeer-recording-transcriber skill into one hypothesis, which is always confirmed
  with the user before anything is written to disk.
compatibility: >-
  Requires ffmpeg and exiftool on PATH (install via Homebrew if missing). Audio
  transcription step delegates to the plumbeer-recording-transcriber skill (macOS Apple
  Silicon, mlx-whisper) — skip that step entirely if the video is silent or that skill is
  unavailable.
metadata:
  author: plumbeer
  version: "1.0"
  category: productivity
---

# Video Metadata Tagger

Determine what a video actually shows — from its frames and, if present, its audio — then
write a confirmed description into the file's embedded metadata and rename it using a
consistent, content-derived filename. Every write to disk is gated on the user confirming
the description first; nothing gets renamed or tagged on a guess.

---

## Progress checklist

Print this before starting, then re-print it with boxes checked off after each step
completes:

```
- [ ] Step 1: Resolve input video & check existing metadata
- [ ] Step 2: Extract representative frames
- [ ] Step 3: Describe the visual content
- [ ] Step 4: Transcribe audio (if present)
- [ ] Step 5: Form a hypothesis
- [ ] Step 6: Confirm with the user
- [ ] Step 7: Write description into embedded metadata
- [ ] Step 8: Rename file(s)
- [ ] Step 9: Deliver results
```

## Step 1: Resolve input video & check existing metadata

- Explicit file path given → use it. Otherwise ask which video, or resolve the one just
  attached/discussed in the conversation.
- Before touching anything else, inspect what's already embedded — it's often faster than
  guessing and it's where the real recording timestamp lives (needed for Step 8):

```bash
ffprobe -v quiet -print_format json -show_format -show_streams "<input>"
exiftool "<input>"
```

- Note the container's `creation_time` (or exiftool's equivalent date field), duration,
  resolution, and rotation. If there's already a meaningful `Description` field, surface it
  to the user and ask whether they want it kept, replaced, or used as a starting hypothesis
  — don't silently overwrite existing metadata.

## Step 2: Extract representative frames

- Sample frames spread across the clip's timeline (start/mid/end at minimum — more for a
  longer or more eventful clip) into the session scratchpad, not the source folder:

```bash
ffmpeg -i "<input>" -vf "select='not(mod(n\,K))'" -fps_mode vfr "<scratchpad>/frame_%02d.png"
```

- Pick `K` so you get roughly 5–10 frames spread across the whole duration (from Step 1's
  duration), not just the first second — a fixed small `K` on a long video only samples the
  opening.

## Step 3: Describe the visual content

- Read the extracted frames directly (multimodal) — don't just describe one frame in
  isolation. Compare frames across the timeline to infer motion, action, and intent (e.g.
  "subject moves from sitting to reaching toward the edge" tells you more than either frame
  alone).
- Note subjects, setting, and what's changing between frames. This is raw observation, not
  yet the hypothesis — keep it separate from the interpretive leap in Step 5.

## Step 4: Transcribe audio (if present)

- Confirm there's actual signal before spending time transcribing — don't transcribe
  near-silent audio:

```bash
ffmpeg -i "<input>" -af volumedetect -f null -
```

- Check the reported `mean_volume` / `max_volume`; if it's effectively silence, skip
  transcription and say so rather than running it anyway.
- If there's real audio, extract it and hand it to the `plumbeer-recording-transcriber`
  skill rather than reimplementing transcription here — reuse its language-detection and
  transcript output.
- If that skill's platform requirement (Apple Silicon + mlx-whisper) isn't met, skip
  transcription and proceed on visual content alone — don't block the whole task on it.

## Step 5: Form a hypothesis

- Combine Step 3's visual observations with Step 4's transcript (if any) into one concrete,
  best-guess sentence of what's happening — subject, action, and setting. E.g. "baby
  reaching down off the bed, likely trying to climb down."
- This is explicitly a guess pending confirmation — don't present it to the user as
  established fact yet, and don't write anything to disk based on it yet.

## Step 6: Confirm with the user

- Ask the user to confirm or correct the Step 5 hypothesis before treating it as fact.
  Show them the hypothesis plus whatever grounded it (key frame description, transcript
  excerpt) so they can judge it, not just a bare guess.
- If they correct it, the corrected version — not the original guess — is what gets written
  in Steps 7–8. Don't proceed past this step without an explicit confirmation.

## Step 7: Write description into embedded metadata

- Write the confirmed description (from Step 6) into the file's embedded metadata:

```bash
exiftool -Description="<confirmed description>" "<input>"
```

- exiftool creates a `<file>_original` backup by default. Verify the write, then remove the
  backup — don't leave stray backup files behind:

```bash
exiftool -Description "<input>"
rm "<input>_original"
```

- This step modifies the user's file in place. It's covered by the confirmation gate in
  Step 6, but flag to the user that you're about to write to the file itself before running
  it, since it's not easily undone once the backup is removed.

## Step 8: Rename file(s)

- Naming convention: `<topic-slug>_<language-code>_<timestamp>.<ext>`
  - `topic-slug`: derived from the confirmed description (Step 6), slugified (lowercase,
    hyphens, alphanumeric only). If there are multiple reasonable short names, propose 2–3
    options and let the user pick rather than guessing one silently.
  - `language-code`: from Step 4's transcript language, if transcription ran; omit that
    segment entirely if there's no audio/transcript.
  - `timestamp`: the video's **embedded recording date** (`creation_time` from Step 1),
    formatted `YYYYMMDD_HHMMSS` — never the filesystem `mtime`. The mtime is unreliable here
    specifically because Step 7 just wrote to the file, which touches mtime regardless of
    when it was actually recorded.
- Ask the user whether to:
  - rename the original file in place, or
  - keep the original filename untouched for provenance (e.g. `IMG_4082.MOV` from a Takeout
    export) and apply the descriptive name only to a copy or to derived artifacts
    (transcript file, video copy).
- Don't rename without this confirmation — it's the one step here that changes how the user
  finds the file afterward.

## Step 9: Deliver results

- Mark every checklist step complete.
- Report: the confirmed description, the final filename(s) and path(s), and whether the
  original was renamed in place or preserved alongside a renamed copy.
- If transcription was skipped (silent audio, or the transcriber skill unavailable), say so
  explicitly rather than leaving it ambiguous whether audio was considered.

---

## Gotchas

- Use the embedded `creation_time`, not filesystem `mtime`, for the filename timestamp —
  writing metadata in Step 7 touches mtime, which would otherwise make the rename look like
  it happened "now" instead of when the video was actually recorded.
- Don't skip Step 1's existing-metadata check — a video may already carry a meaningful
  `Description`, and silently overwriting it loses information the user may have set
  deliberately.
- A single sampled frame is not enough to describe action or intent — always compare frames
  across the timeline (Step 3) before forming a hypothesis.
- Confirm real audio signal (`volumedetect`) before transcribing — near-silent ambient audio
  wastes time and can produce a misleading whisper hallucination as if it were meaningful
  speech.
- The hypothesis (Step 5) is a guess, not a fact — always route it through user confirmation
  (Step 6) before either the metadata write (Step 7) or the rename (Step 8); those two steps
  touch the user's actual file and are the fragile, hard-to-reverse points in this skill.
- exiftool's `_original` backup file must be explicitly removed after verifying the write —
  otherwise it's left behind as clutter next to the real file.
- Renaming is a user choice, not a default — always ask whether to rename in place or
  preserve the original filename for provenance, especially for files sourced from an
  export/backup where the original name carries meaning (e.g. Google Takeout's `IMG_####`
  numbering).
