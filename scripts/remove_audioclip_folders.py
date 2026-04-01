"""
Recursively removes all folders named 'AudioClip' under gamedata/sounds/characters_voice.
"""

import shutil
import sys
from pathlib import Path

VOICE_DIR = Path(__file__).parent / "../gamedata/sounds/characters_voice"


def main():
    if not VOICE_DIR.exists():
        print(f"Directory not found: {VOICE_DIR}")
        sys.exit(1)

    targets = [p for p in VOICE_DIR.rglob("AudioClip") if p.is_dir()]

    if not targets:
        print("No AudioClip folders found.")
        return

    print(f"Found {len(targets)} AudioClip folder(s):\n")
    for p in targets:
        print(f"  {p.relative_to(VOICE_DIR)}")

    print()
    for p in targets:
        shutil.rmtree(p)
        print(f"  removed: {p.relative_to(VOICE_DIR)}")

    print(f"\nDone: {len(targets)} folder(s) removed.")


if __name__ == "__main__":
    main()
