#!/usr/bin/env python3
"""
Recursively converts all .wav files under a directory to .ogg (libvorbis),
then deletes the original .wav.

Requirements: ffmpeg must be on PATH.
  Windows: winget install ffmpeg
  Or download from https://ffmpeg.org/download.html

Usage:
  python convert_wav_to_ogg.py [DIR]
  python convert_wav_to_ogg.py [DIR] --dry-run

If `DIR` is not provided, defaults to `gamedata/sounds` relative to this script.
"""

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_SOUNDS_DIR = Path(__file__).parent / "../gamedata" / "sounds"
QUALITY = 6  # libvorbis quality, 0-10 (6 ≈ ~192 kbps VBR, fine for game audio)


def convert(wav: Path, dry_run: bool) -> bool:
    ogg = wav.with_suffix(".ogg")
    if dry_run:
        return True
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(wav),
            "-c:a", "libvorbis",
            "-q:a", str(QUALITY),
            str(ogg),
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        print(f"  FAILED: {wav.name}")
        print(result.stderr.decode(errors="replace"))
        return False
    wav.unlink()
    return True


def main():
    parser = argparse.ArgumentParser(description="Convert WAV files to OGG under a directory.")
    parser.add_argument(
        "dir",
        nargs="?",
        default=str(DEFAULT_SOUNDS_DIR),
        help="Directory to search for .wav files (default: `gamedata/sounds`)",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="List files that would be converted without touching them.")
    args = parser.parse_args()

    sounds_dir = Path(args.dir).resolve()

    if not sounds_dir.exists():
        print(f"Directory not found: {sounds_dir}")
        sys.exit(1)

    wavs = list(sounds_dir.rglob("*.wav"))
    if not wavs:
        print("No .wav files found.")
        return

    try:
        ffmpeg_ok = subprocess.run(["ffmpeg", "-version"], capture_output=True).returncode == 0
    except FileNotFoundError:
        ffmpeg_ok = False
    if not ffmpeg_ok:
        print("ERROR: ffmpeg not found on PATH.")
        print("Install it with:  winget install ffmpeg")
        print("Or download from: https://ffmpeg.org/download.html")
        sys.exit(1)

    dry_run = args.dry_run
    if dry_run:
        print("[dry run] no files will be changed\n")

    print(f"Found {len(wavs)} .wav file(s) under {sounds_dir}\n")
    ok = fail = 0
    for wav in wavs:
        rel = wav.relative_to(sounds_dir)
        print(f"  {rel}", end=" ... ", flush=True)
        if convert(wav, dry_run):
            print("ok" if not dry_run else "(skipped)")
            ok += 1
        else:
            fail += 1

    label = "would be converted" if dry_run else "converted"
    print(f"\nDone: {ok} {label}, {fail} failed.")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
