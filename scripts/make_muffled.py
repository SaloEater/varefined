#!/usr/bin/env python3
"""
make_muffled.py

Creates helmet (m_) variants of .ogg voice files by simulating speech
heard through a closed helmet worn by *you* (the listener):

  1. High-pass      @ 100 Hz   — remove only sub-bass rumble, no muffling
  2. Presence boost @ 2500 Hz  — sealed cavity makes voice sound brighter/higher
  3. Resonance peak @ 1000 Hz  — cavity resonance of the helmet interior
  4. +30% loudness             — voice sounds louder and clearer inside
  5. Very short reverb (2–15 ms) — reflections off the visor/inner shell

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
    data_original = data.copy()

    # 1. Remove only sub-bass rumble — no muffling at all.
    #    Inside a helmet you hear your own voice clearly; there is no LP filter
    #    on your own voice the way there would be on an external sound source.
    hp = signal.butter(2, 100, btype='high', fs=samplerate, output='sos')
    data = _apply_sos(hp, data)

    # 2. Presence boost: the sealed cavity around your ears emphasizes upper-mids,
    #    which makes your voice sound slightly brighter / a touch higher in pitch.
    b, a = signal.iirpeak(2500, Q=1.5, fs=samplerate)
    presence_sos = signal.tf2sos(b, a)
    data = _apply_sos(presence_sos, data)

    # 3. Resonance peak: cavity resonance of the helmet interior.
    #    Convert to SOS — direct (b,a) form is numerically unstable at high Q.
    b, a = signal.iirpeak(resonance_hz, Q=6, fs=samplerate)
    peak_sos = signal.tf2sos(b, a)
    data = _apply_sos(peak_sos, data)

    # Boost by 30%: inside the helmet your voice sounds louder and clearer.
    original_rms = np.sqrt(np.mean(data_original ** 2))
    filtered_rms = np.sqrt(np.mean(data ** 2))
    if filtered_rms > 0:
        data = data * min(original_rms / filtered_rms * 1.3, 6)

    # 5. Very short reverb: sound bouncing off the visor/inner shell close to
    #    your ears. Delays are short (2–15 ms) and gains are noticeable so the
    #    sealed-space feel is apparent without sounding like an open room echo.
    reflections = [(0.002, 0.56), (0.005, 0.32), (0.009, 0.16), (0.015, 0.08)]
    result = data.copy()
    for delay_s, gain in reflections:
        delay_smp = int(delay_s * samplerate)
        if delay_smp <= 0:
            continue
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
        default=1000,
        metavar='HZ',
        help='Helmet cavity resonance frequency in Hz (default: 1000). '
             'Higher = brighter resonance (try 800–1500).',
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
