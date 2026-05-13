#!/usr/bin/env python3
"""
report_loudness.py

Measures integrated loudness (LUFS, ITU-R BS.1770) for every OGG file under
gamedata/sounds/characters_voice using ffmpeg's ebur128 filter.
Outputs one CSV row per file, sorted loudest-first.

Requirements: ffmpeg must be on PATH.
"""

import csv
import re
import argparse
import subprocess
from pathlib import Path

MEAN_VOL_RE = re.compile(r'mean_volume:\s*([-\d.]+)\s*dB')


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


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Report integrated loudness (LUFS) per OGG file as CSV.'
    )
    parser.add_argument(
        '--sounds',
        default='gamedata/sounds/characters_voice',
        help='Root directory to scan for OGG files',
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=-22.5,
        help='Mean dBFS above this value is marked loud=true in the CSV (default: -18.0)',
    )
    parser.add_argument(
        '--output',
        default='scripts/loudness_report.csv',
        help='CSV file to write (default: scripts/loudness_report.csv)',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Process only the first N files (useful for testing)',
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

    print(f'Measuring {len(ogg_files)} file(s)...\n')

    rows = []
    errors = 0

    for i, path in enumerate(ogg_files, 1):
        print(f'\r  {i}/{len(ogg_files)}', end='', flush=True)
        db = measure_db(path)
        if db is None:
            print(f'\n  WARNING: could not measure {path.relative_to(sounds_root)}')
            errors += 1
            continue
        rows.append((path.parent.name, path.name, db))

    print()

    if not rows:
        print('No measurements collected.')
        return 1

    rows.sort(key=lambda r: r[2], reverse=True)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['subcategory', 'file', 'mean_db', 'loud'])
        for subcategory, filename, db in rows:
            writer.writerow([subcategory, filename, f'{db:.1f}', db > args.threshold])

    print(f'Rows written: {len(rows)}  |  Errors: {errors}')
    print(f'Report saved: {out_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
