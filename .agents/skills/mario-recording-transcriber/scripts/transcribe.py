#!/usr/bin/env python3
import argparse
import mlx_whisper


def format_timestamp(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def transcribe(input_path, output_path, verbose, timestamps):
    result = mlx_whisper.transcribe(
        input_path,
        path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
        verbose=verbose,
    )
    if timestamps:
        lines = [
            f"[{format_timestamp(seg['start'])}] {seg['text'].strip()}"
            for seg in result["segments"]
        ]
        text = "\n".join(lines)
    else:
        text = result["text"].strip()
    with open(output_path, "w") as f:
        f.write(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")
    parser.add_argument("output_path")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--no-timestamps", action="store_true")
    args = parser.parse_args()
    transcribe(args.input_path, args.output_path, args.verbose, not args.no_timestamps)
