#!/usr/bin/env python3
"""
normalize_loudness.py

Reduces integrated loudness of OGG files to a target LUFS value.
Only non-muffled files (no m_ prefix) are processed; muffled variants are skipped.
Files already at or below the target are left untouched (reduce-only).

Requirements: ffmpeg must be on PATH.
"""

import re
import argparse
import subprocess
from pathlib import Path

MEAN_VOL_RE = re.compile(r'mean_volume:\s*([-\d.]+)\s*dB')

# Per-folder target overrides. Key = subcategory folder name, value = target dBFS.
# Folders not listed here use the --target argument.
FOLDER_TARGETS: dict[str, float] = {
    "kill_comment_common_squad": -22.5,
    "kill_comment_mutant_squad": -22.5,
    "kill_comment_stalker_squad": -22.5,
    "kill_confirm_common_squad": -20,
    "kill_confirm_mutant_squad": -20,
    "kill_confirm_stalker_squad": -20,

    "kill_comment_common_state1": -20,
    "kill_comment_mutant_state1": -20,
    "kill_comment_stalker_state1": -20,
    "kill_confirm_common_state1": -17.5,
    "kill_confirm_mutant_state1": -17.5,
    "kill_confirm_stalker_state1": -17.5,

    "kill_comment_common_state2": -17.5,
    "kill_comment_mutant_state2": -17.5,
    "kill_comment_stalker_state2": -17.5,
    "kill_confirm_common_state2": -15,
    "kill_confirm_mutant_state2": -15,
    "kill_confirm_stalker_state2": -15,

    "kill_comment_common_state3": -15,
    "kill_comment_mutant_state3": -15,
    "kill_comment_stalker_state3": -15,
    "kill_confirm_common_state3": -12.5,
    "kill_confirm_mutant_state3": -12.5,
    "kill_confirm_stalker_state3": -12.5
}


def check_ffmpeg() -> bool:
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def measure_db(path: Path) -> float | None:
    result = subprocess.run(
        ['ffmpeg', '-i', str(path), '-af', 'volumedetect', '-f', 'null', '-'],
        capture_output=True,
        text=True,
    )
    m = MEAN_VOL_RE.search(result.stderr)
    if m:
        return float(m.group(1))
    return None


def reduce_file(path: Path, gain_db: float) -> bool:
    temp = path.with_suffix('.tmp.ogg')
    result = subprocess.run(
        [
            'ffmpeg', '-i', str(path),
            '-af', f'volume={gain_db:.2f}dB',
            '-c:a', 'libvorbis', '-q:a', '6',
            '-y', str(temp),
        ],
        capture_output=True,
    )
    if result.returncode == 0:
        temp.replace(path)
        return True
    if temp.exists():
        temp.unlink()
    print(f'  ffmpeg error: {result.stderr.decode(errors="replace").strip()}')
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Reduce OGG voice file loudness to a target LUFS (reduce-only, skips m_ files).'
    )
    parser.add_argument(
        '--sounds',
        default='test',
        help='Root directory to scan for OGG files',
    )
    parser.add_argument(
        '--target',
        type=float,
        default=-25.0,
        help='Target mean volume in dBFS (default: -18.0)',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Process only the first N files (useful for testing)',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would change without modifying any files',
    )
    args = parser.parse_args()

    if not check_ffmpeg():
        print('Error: ffmpeg not found on PATH.')
        print('Install via winget: winget install Gyan.FFmpeg')
        return 1

    sounds_root = Path(args.sounds)
    if not sounds_root.is_dir():
        print(f'Error: sounds dir not found: {sounds_root}')
        return 1

    ogg_files = sorted(
        f for f in sounds_root.rglob('*.ogg')
        if not f.name.startswith('m_')
    )

    if args.limit:
        ogg_files = ogg_files[:args.limit]

    if not ogg_files:
        print('No OGG files found.')
        return 0

    mode = '(dry run) ' if args.dry_run else ''
    print(f'Scanning {sounds_root}  {mode}default target: {args.target:+.1f} dBFS')
    if FOLDER_TARGETS:
        for folder, t in sorted(FOLDER_TARGETS.items()):
            print(f'  {folder}: {t:+.1f} dBFS')
    print()

    reduced = skipped = errors = 0

    for path in ogg_files:
        rel = path.relative_to(sounds_root)
        target = FOLDER_TARGETS.get(path.parent.name, args.target)
        db = measure_db(path)

        if db is None:
            print(f'  ERROR   {rel}  (could not measure)')
            errors += 1
            continue

        if db <= target:
            print(f'  SKIP    {rel}  {db:+.1f} dB')
            skipped += 1
            continue

        gain_db = target - db
        print(f'  REDUCE  {rel}  {db:+.1f} dB  ->  {target:+.1f} dBFS  (gain: {gain_db:+.1f} dB)', end='')

        if args.dry_run:
            print()
            reduced += 1
            continue

        ok = reduce_file(path, gain_db)
        if ok:
            print('  OK')
            reduced += 1
        else:
            print('  FAILED')
            errors += 1

    print(f'\nDone.  Reduced: {reduced}  |  Skipped: {skipped}  |  Errors: {errors}')
    return 0 if errors == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
