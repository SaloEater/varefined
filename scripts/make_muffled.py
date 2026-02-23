#!/usr/bin/env python3
"""
make_muffled.py

Creates helmet (m_) variants of .ogg voice files by simulating speech
heard inside a sealed full-body helmet:

  1. High-pass  @ 350 Hz   — removes bass that a sealed helmet blocks
  2. Low-pass   @ 2200 Hz  — softens highs but keeps voice presence
  3. Resonance peak         — cavity resonance of the helmet interior
  4. Early reflections      — short echoes of sound bouncing off the visor

Requires one of:
  - soundfile + scipy + numpy  (preferred — pure Python, no external binary)
  - pydub + ffmpeg on PATH     (fallback, no resonance or echo)

Install:
  pip install soundfile scipy numpy
  -- or --
  pip install pydub  (and put ffmpeg on PATH)

Usage:
  python make_muffled.py gamedata/sounds/characters_voice/player/death
  python make_muffled.py player/death/death_1.ogg
  python make_muffled.py player/death --resonance 2000
  python make_muffled.py player/death --overwrite --dry-run
"""

import argparse
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# DSP
# ---------------------------------------------------------------------------

def _apply_sos(sos, data):
    """Apply SOS filter to mono or stereo float64 numpy array."""
    import numpy as np
    from scipy import signal
    if data.ndim == 1:
        return signal.sosfilt(sos, data)
    return np.column_stack(
        [signal.sosfilt(sos, data[:, ch]) for ch in range(data.shape[1])]
    )


def _apply_ba(b, a, data):
    """Apply (b, a) filter to mono or stereo float64 numpy array."""
    import numpy as np
    from scipy import signal
    if data.ndim == 1:
        return signal.lfilter(b, a, data)
    return np.column_stack(
        [signal.lfilter(b, a, data[:, ch]) for ch in range(data.shape[1])]
    )


def _helmet_scipy(data, samplerate: int, resonance_hz: int):
    import numpy as np
    from scipy import signal

    data = data.astype(np.float64)

    # 1. High-pass: remove low-end bass (sealed helmet blocks it)
    hp = signal.butter(2, 350, btype='high', fs=samplerate, output='sos')
    data = _apply_sos(hp, data)

    # 2. Low-pass: soften high frequencies while keeping voice presence
    lp = signal.butter(3, 2200, btype='low', fs=samplerate, output='sos')
    data = _apply_sos(lp, data)

    # 3. Resonance peak: helmet interior acts as a resonant cavity
    b, a = signal.iirpeak(resonance_hz, Q=3.5, fs=samplerate)
    data = _apply_ba(b, a, data)

    # 4. Early reflections: sound bouncing off the visor / helmet walls
    #    (delay_seconds, gain) — short, quiet copies of the signal
    reflections = [(0.005, 0.22), (0.011, 0.12), (0.019, 0.06), (0.030, 0.03)]
    result = data.copy()
    for delay_s, gain in reflections:
        delay_smp = int(delay_s * samplerate)
        if delay_smp <= 0:
            continue
        if data.ndim == 1:
            delayed = np.zeros_like(data)
            delayed[delay_smp:] = data[:-delay_smp]
        else:
            delayed = np.zeros_like(data)
            delayed[delay_smp:] = data[:-delay_smp]
        result = result + delayed * gain

    return np.clip(result, -1.0, 1.0)


# ---------------------------------------------------------------------------
# I/O backends
# ---------------------------------------------------------------------------

def _process_soundfile(src: Path, dst: Path, resonance_hz: int) -> None:
    import soundfile as sf

    data, samplerate = sf.read(str(src))
    processed = _helmet_scipy(data, samplerate, resonance_hz)
    sf.write(str(dst), processed, samplerate, format='OGG', subtype='VORBIS')


def _process_pydub(src: Path, dst: Path) -> None:
    """Fallback: pydub with high-pass + low-pass only (no resonance/echo)."""
    from pydub import AudioSegment
    from pydub.effects import high_pass_filter, low_pass_filter

    audio = AudioSegment.from_file(str(src), format='ogg')
    audio = high_pass_filter(audio, 350)
    audio = low_pass_filter(audio, 2200)
    audio.export(str(dst), format='ogg')


def _process(src: Path, dst: Path, resonance_hz: int) -> None:
    errors = []

    try:
        _process_soundfile(src, dst, resonance_hz)
        return
    except Exception as e:
        errors.append(f'soundfile+scipy: {e}')

    try:
        _process_pydub(src, dst)
        return
    except Exception as e:
        errors.append(f'pydub: {e}')

    raise RuntimeError('\n  '.join(errors))


# ---------------------------------------------------------------------------
# File logic
# ---------------------------------------------------------------------------

def process_file(src: Path, resonance_hz: int, overwrite: bool, dry_run: bool) -> bool:
    if src.name.lower().startswith('m_'):
        return False  # already a helmet variant, skip silently

    dst = src.parent / f'm_{src.name}'

    if dst.exists() and not overwrite:
        return False

    print(f'  {src.name}  ->  {dst.name}')
    if dry_run:
        return True

    try:
        _process(src, dst, resonance_hz)
        return True
    except RuntimeError as e:
        print(f'    ERROR: {e}', file=sys.stderr)
        return False


def process_directory(directory: Path, resonance_hz: int, overwrite: bool, dry_run: bool) -> None:
    created = 0
    for src in sorted(directory.rglob('*.ogg')):
        if process_file(src, resonance_hz, overwrite, dry_run):
            created += 1
    verb = 'Would create' if dry_run else 'Created'
    print(f'\n{verb} {created} helmet variant(s).')


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description='Generate m_ helmet variants of .ogg voice files.'
    )
    parser.add_argument(
        'path',
        help='OGG file or directory to process',
    )
    parser.add_argument(
        '--resonance',
        type=int,
        default=3500,
        metavar='HZ',
        help='Helmet cavity resonance frequency in Hz (default: 3500). '
             'Higher = brighter resonance (try 1200–2500).',
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing m_ files',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without writing anything',
    )
    args = parser.parse_args()

    target = Path(args.path)
    prefix = '[DRY RUN] ' if args.dry_run else ''

    if target.is_file():
        if target.suffix.lower() != '.ogg':
            print(f'Error: not an .ogg file: {target}')
            return 1
        print(f'{prefix}Processing: {target}  (resonance {args.resonance} Hz)')
        process_file(target, args.resonance, args.overwrite, args.dry_run)

    elif target.is_dir():
        print(f'{prefix}Processing directory: {target.resolve()}  (resonance {args.resonance} Hz)')
        process_directory(target, args.resonance, args.overwrite, args.dry_run)

    else:
        print(f'Error: path not found: {target}')
        return 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
