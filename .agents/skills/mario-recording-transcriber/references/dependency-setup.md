# Dependency setup

This skill needs `ffmpeg` (for audio decoding) and a Python virtualenv with `mlx-whisper`
installed. Both should be verified before Step 4 of `SKILL.md` runs, and reused across
sessions rather than reinstalled every time.

## 1. ffmpeg

```bash
which ffmpeg
```

If missing:

```bash
brew install ffmpeg
```

## 2. mlx-whisper virtualenv

Use a **persistent** location, not a per-session scratchpad — the whole point is not
reinstalling on every run. Use `~/.mario-skills/recording-transcriber/venv`.

Check whether it already works:

```bash
~/.mario-skills/recording-transcriber/venv/bin/python -c "import mlx_whisper" 2>&1
```

If that fails (venv doesn't exist yet, or the import fails), create/repair it:

```bash
mkdir -p ~/.mario-skills/recording-transcriber
python3 -m venv ~/.mario-skills/recording-transcriber/venv
~/.mario-skills/recording-transcriber/venv/bin/pip install --quiet mlx-whisper
```

Do **not** `pip install` into system or Homebrew Python — Homebrew's Python refuses
system-wide installs (PEP 668), and even where it doesn't, polluting system Python is
avoidable.

## 3. Verify before proceeding

Re-run the import check:

```bash
~/.mario-skills/recording-transcriber/venv/bin/python -c "import mlx_whisper; print('ok')"
```

If this still fails — most likely because the machine isn't Apple Silicon, since
`mlx-whisper` requires it — stop and tell the user plainly that this skill can't run on
their hardware. There is no fallback transcription engine; don't try to install one.

Once both checks pass, proceed to Step 4 in `SKILL.md`, invoking
`scripts/transcribe.py` through this venv's Python.
