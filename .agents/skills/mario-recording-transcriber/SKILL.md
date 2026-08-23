---
name: mario-recording-transcriber
description: >-
  Convert a spoken audio recording into a text transcript with per-segment [MM:SS]
  timestamps by default, then read the transcript, propose five topic options for what it's
  mainly about, and once the user picks one, save the transcript and a copy of the source
  audio side by side under a filename prefixed with that topic and a timestamp. Use
  whenever the user says "transcribe this recording," "convert this audio to text," "speech
  to text this file," or points to / attaches an audio file and wants a written transcript.
  Defaults to ~/Recordings as both source and output location. Always show a step-by-step
  progress checklist so the user can see which step is running.
compatibility: >-
  macOS on Apple Silicon. Requires ffmpeg (installed via Homebrew if missing) and a local
  Python virtualenv with mlx-whisper — see references/dependency-setup.md. Never installs
  into system/Homebrew Python.
metadata:
  author: mario
  version: "1.0"
  category: productivity
---

# Recording Transcriber

Convert a spoken audio recording into a text transcript, let the user pick which topic best
names it, and keep the transcript and the source audio filed together under one
topic-and-timestamp name.

---

## Progress checklist

Print this before starting, then re-print it with boxes checked off after each step
completes, so the user always sees which step is running:

```
- [ ] Step 1: Resolve input audio
- [ ] Step 2: Verify/install dependencies
- [ ] Step 3: Transcribe audio
- [ ] Step 4: Propose topic options & get user's choice
- [ ] Step 5: Determine output filename & paths
- [ ] Step 6: Save transcript + copy audio
- [ ] Step 7: Deliver results
```

---

## Step 1: Resolve input audio

- Explicit file path given → use it.
- Folder given (or nothing) → default to `~/Recordings`, pick the most recently modified
  audio file in it; ask if it's ambiguous (e.g. several files modified around the same
  time).
- User wants to provide audio directly instead of a path → tell them to attach/drag the
  audio file into the chat, then resolve its actual saved local path — don't assume
  `~/Recordings` is still the right parent folder for output defaults in that case.
- No audio file found anywhere → stop and say so. Don't guess.

Also confirm two output options here, up front, before doing any work:

- **Verbose transcription progress** — live per-segment timestamps printed to the terminal
  while transcribing. **Default: off.** mlx-whisper has no dry-run/ETA API, so this is the
  only way to see live progress on a long recording; offer it, don't force it.
- **Timestamps in the transcript itself** — per-segment `[MM:SS]` prefixes in the output
  text. **Default: on.** Let the user opt out for flat plain-text output.

## Step 2: Verify/install dependencies

Follow [references/dependency-setup.md](references/dependency-setup.md) exactly. In short:
first confirm the platform is an Apple Silicon Mac (`uname -s` is `Darwin`, `uname -m` is
`arm64`) — if not, stop immediately, before touching Homebrew or Python at all. Then check
`ffmpeg` on PATH (install via Homebrew if missing), and check for a working mlx-whisper
virtualenv (create one and `pip install mlx-whisper` if missing). Never `pip install` into
system/Homebrew Python — it's blocked by PEP 668 anyway.

This skill is **mlx-whisper only** — there is no CPU/non-Apple-Silicon fallback. If the
platform check fails, or mlx-whisper otherwise cannot run on this machine, stop and tell
the user rather than degrading to a slower alternative.

## Step 3: Transcribe audio

The final filename depends on a topic the user hasn't chosen yet (Step 4), so transcribe to
a scratch path first — e.g. the session scratchpad — and move it into place in Step 6.

Run the bundled script through the persistent venv's Python (see
[references/dependency-setup.md](references/dependency-setup.md)):

```bash
~/.mario-skills/recording-transcriber/venv/bin/python scripts/transcribe.py <input_audio> <scratch_output.txt> [--verbose] [--no-timestamps]
```

- Pass `--verbose` only if the user opted into it in Step 1.
- Timestamps are on by default; pass `--no-timestamps` only if the user opted out in Step 1.
  With timestamps on, each line of the transcript is `[MM:SS] segment text`. With
  `--no-timestamps`, the output is one flat text block.
- Tell the user up front: the first run downloads the whisper model (roughly 1–2 minutes);
  subsequent runs are fast since the model is cached.
- A tail of repeated short phrases (e.g. "Thank you." over and over) is a known
  hallucination-on-silence artifact from whisper, not a transcription error — mention it in
  the delivery caption rather than silently editing it out of the transcript.

## Step 4: Propose topic options & get user's choice

- Read the scratch transcript from Step 3.
- Propose exactly **five** short topic options describing what the recording is mainly
  about — think section/label names (2-4 words each), not full sentences, and not a rehash
  of the whole transcript. Ground them in what's actually discussed, not generic guesses.
- Ask the user to pick one, e.g. via `AskUserQuestion` (which also lets them supply their
  own topic instead if none of the five fit).
- The chosen topic becomes the filename prefix in Step 5 — slugify it for filesystem safety
  (spaces → hyphens, drop characters that aren't alphanumeric/hyphen/underscore, keep it
  short).

## Step 5: Determine output filename & paths

- Output folder defaults to the **same folder as the source audio**.
- Filename = `<topic-slug>_<timestamp>`, where `<timestamp>` is the **source audio file's
  own modification timestamp**, formatted `YYYYMMDD_HHMMSS` — not "now." This keeps the
  name tied to when the recording actually happened, even if transcription runs later.
- Transcript → `<topic-slug>_<timestamp>.txt`; copied audio →
  `<topic-slug>_<timestamp><original-extension>`.
- Honor a user-specified output folder or filename format if one was given instead.
- If the target transcript or audio-copy file already exists, **ask before overwriting**
  (this is the one destructive edge case in this skill).

## Step 6: Save transcript + copy audio

- Move (or copy) the scratch transcript from Step 3 to
  `<output_folder>/<topic-slug>_<timestamp>.txt`.
- Copy — not move, unless the user explicitly asked to move the source — the source audio
  to `<output_folder>/<topic-slug>_<timestamp><original-extension>`.
- If source and destination already coincide (same folder, same name), skip the audio copy.

## Step 7: Deliver results

- Mark every checklist step complete.
- Use `SendUserFile` to deliver the transcript `.txt` (and the audio copy, if one was newly
  created).
- Give a one-line summary of what was created and where, including a note if verbose output
  or the hallucination artifact came up during the run.

---

## Gotchas

- mlx-whisper is Apple-Silicon-only and this skill has no fallback engine — if it can't
  run, stop and tell the user rather than trying something slower or different.
- Always use a project-local venv for installs, never system/Homebrew Python.
- Repeated-phrase / "Thank you." loops at a transcript's tail are a known artifact of
  whisper hallucinating on trailing silence — call it out, don't silently rewrite the text.
- Default output is timestamped `[MM:SS] text` per line, not flat prose — mention this if
  the user expects plain text, and point them at the Step 1 opt-out (`--no-timestamps`).
- When audio arrives via chat attachment, resolve its real saved path before treating its
  parent folder as the output default — it usually isn't `~/Recordings`.
- The final filename isn't known until *after* transcription (it depends on the topic the
  user picks in Step 4), so Step 3 must write to a scratch path, not directly into the
  output folder.
- Slugify the chosen topic before using it in a filename — don't write raw spaces or
  punctuation from the user's chosen option straight into a path.
