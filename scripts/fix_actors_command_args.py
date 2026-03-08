#!/usr/bin/env python3
"""
fix_actors_command_args.py

Rewrites the first string argument of every axr_companions.actors_command(...)
call in gamedata/scripts from PascalCase to snake_case.

  axr_companions.actors_command("FireAtWill_ComClose", ...)
  ->
  axr_companions.actors_command("fire_at_will_com_close", ...)
"""

import re
import sys
import argparse
from pathlib import Path


# --------------------------------------------------------------------------- #
# PascalCase -> snake_case (shared logic with rename_to_snake_case.py)
# --------------------------------------------------------------------------- #

def to_snake_case(name: str) -> str:
    """Convert PascalCase / CamelCase (with optional _ separators) to snake_case."""
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)   # e.g. ComClose -> Com_Close
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)   # e.g. AICom   -> AI_Com
    return s.lower()


# --------------------------------------------------------------------------- #
# File processing
# --------------------------------------------------------------------------- #

# Matches the opening of the call followed by a double-quoted first argument.
# Capture groups:
#   1 - everything up to and including the opening quote  ("axr_companions.actors_command(\"")
#   2 - the argument value                                ("FireAtWill_ComClose")
#   3 - the closing quote + rest of match                 ("\"")
CALL_RE = re.compile(
    r'(axr_companions\.actors_command\(\s*")'  # group 1: prefix
    r'([^"]+)'                                  # group 2: first arg value
    r'(")',                                     # group 3: closing quote
)


def fix_content(source: str) -> tuple[str, int]:
    """Return (updated_source, number_of_replacements)."""
    count = 0

    def replacer(m: re.Match) -> str:
        nonlocal count
        old_arg = m.group(2)
        new_arg = to_snake_case(old_arg)
        if new_arg == old_arg:
            return m.group(0)
        count += 1
        return f'{m.group(1)}{new_arg}{m.group(3)}'

    new_source = CALL_RE.sub(replacer, source)
    return new_source, count


def process_file(path: Path, dry_run: bool) -> int:
    text = path.read_text(encoding='utf-8')
    new_text, count = fix_content(text)

    if count == 0:
        return 0

    print(f'\n{path}  ({count} replacement(s))')

    # Show each changed line
    for i, (old_line, new_line) in enumerate(
        zip(text.splitlines(), new_text.splitlines()), 1
    ):
        if old_line != new_line:
            print(f'  line {i}:')
            print(f'    - {old_line.strip()}')
            print(f'    + {new_line.strip()}')

    if not dry_run:
        path.write_text(new_text, encoding='utf-8')

    return count


def process(scripts_dir: Path, dry_run: bool) -> None:
    total = 0
    for path in sorted(scripts_dir.rglob('*.script')):
        total += process_file(path, dry_run)

    action = 'Would update' if dry_run else 'Updated'
    print(f'\n{action} {total} call(s) across gamedata/scripts.')


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(
        description='Rewrite axr_companions.actors_command first args to snake_case.'
    )
    parser.add_argument(
        'scripts_dir',
        nargs='?',
        default='gamedata/scripts',
        help='Path to scripts directory (default: gamedata/scripts)',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without writing any files',
    )
    args = parser.parse_args()

    scripts_dir = Path(args.scripts_dir)
    if not scripts_dir.is_dir():
        print(f'Error: directory not found: {scripts_dir}')
        return 1

    print(f'{"[DRY RUN] " if args.dry_run else ""}Processing: {scripts_dir.resolve()}')
    process(scripts_dir, args.dry_run)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
