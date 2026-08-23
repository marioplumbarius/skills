#!/usr/bin/env python3
"""Transcribe an audio file with mlx-whisper.

Segment timestamps are the default output because the skill's transcripts are meant to be
navigable afterward (e.g. jumping to a moment in a long recording) rather than just a
readable block of prose; --no-timestamps exists for callers who want plain text instead.
verbose is opt-in rather than always-on because mlx-whisper has no dry-run/ETA API, so it's
the only way to see live progress on a long recording, but printing it unconditionally
would be noisy for short ones.
"""
import argparse

import mlx_whisper


def format_timestamp(seconds: float) -> str:
    """mlx-whisper reports segment times as float seconds; transcripts read as MM:SS."""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def transcribe(input_path: str, output_path: str, verbose: bool, timestamps: bool) -> None:
    """Transcribe input_path and write the result to output_path.

    Runs "large-v3-turbo" specifically: it's the mlx-community checkpoint tuned for
    Apple Silicon throughput, which matters here since this skill has no CPU fallback.
    """
    result = mlx_whisper.transcribe(
        audio=input_path,
        path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
        verbose=verbose,
    )
    if timestamps:
        lines = [
            f"[{format_timestamp(seconds=seg['start'])}] {seg['text'].strip()}"
            for seg in result["segments"]
        ]
        text = "\n".join(lines)
    else:
        text = result["text"].strip()
    with open(output_path, "w") as f:
        f.write(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str)
    parser.add_argument("output_path", type=str)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--no-timestamps", action="store_true")
    args = parser.parse_args()
    transcribe(
        input_path=args.input_path,
        output_path=args.output_path,
        verbose=args.verbose,
        timestamps=not args.no_timestamps,
    )
