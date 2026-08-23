# Dependency setup

This skill needs `ffmpeg` (for audio decoding) and a Python virtualenv with `mlx-whisper`
installed. Both should be verified before Step 4 of `SKILL.md` runs, and reused across
sessions rather than reinstalled every time.

## 0. Platform check (do this first)

`mlx-whisper` only runs on Apple Silicon Macs. Check before touching Homebrew or Python at
all — there's no point installing anything if the platform can't run it:

```bash
uname -s   # must be Darwin (macOS)
uname -m   # must be arm64 (Apple Silicon)
```

If either check fails — not macOS, or an Intel Mac — **stop immediately** and tell the user
plainly that this skill requires an Apple Silicon Mac and can't run on their machine. Don't
attempt `brew install` or venv setup on a platform that will never satisfy `mlx-whisper`.

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
reinstalling on every run. Use `~/.plumbeer-skills/recording-transcriber/venv`.

Check whether it already works:

```bash
~/.plumbeer-skills/recording-transcriber/venv/bin/python -c "import mlx_whisper" 2>&1
```

If that fails (venv doesn't exist yet, or the import fails), create/repair it:

```bash
mkdir -p ~/.plumbeer-skills/recording-transcriber
python3 -m venv ~/.plumbeer-skills/recording-transcriber/venv
~/.plumbeer-skills/recording-transcriber/venv/bin/pip install --quiet mlx-whisper
```

Do **not** `pip install` into system or Homebrew Python — Homebrew's Python refuses
system-wide installs (PEP 668), and even where it doesn't, polluting system Python is
avoidable.

## 3. Verify before proceeding

Re-run the import check:

```bash
~/.plumbeer-skills/recording-transcriber/venv/bin/python -c "import mlx_whisper; print('ok')"
```

If this still fails despite the Step 0 platform check passing, stop and tell the user the
install itself is broken rather than guessing further. There is no fallback transcription
engine; don't try to install one.

Once both checks pass, proceed to Step 4 in `SKILL.md`, invoking
`scripts/transcribe.py` through this venv's Python.
