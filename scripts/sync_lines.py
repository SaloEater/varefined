#!/usr/bin/env python3
"""
sync_lines.py

Rewrites the [lines_*] sections in gamedata/configs/plugins/varefined.ltx
based on actual .ogg files found in gamedata/sounds/characters_voice.
Also regenerates varefined_mcm_generated.script and _ui_mcm_varefined_generated.xml
from the union of all discovered reaction names.

Rules:
- Language is determined by category folder suffix (e.g. player -> rus, player_eng -> eng)
- The commands / commands_eng categories are excluded (they use a different path format)
- Only non-muffled files (no m_ prefix) are counted; muffled variants share the same count
- Keys are the base ogg file names (m_ and _N stripped), sorted alphabetically
- Entries with no actual files are included with a count of 0
"""

import re
import argparse
from collections import defaultdict
from pathlib import Path

INDEXED_OGG = re.compile(r'^(m_)?(.+)_\d+\.ogg$', re.IGNORECASE)
SECTION_RE = re.compile(r'^\[(.+)\]')
EXCLUDED_CATEGORIES: set[str] = set()  # categories to skip (bare name, no lang suffix)


def parse_languages(ltx_text: str) -> dict[str, str]:
    """Return {lang_key: folder_suffix} from the [language] section."""
    result = {}
    in_lang = False
    for raw in ltx_text.splitlines():
        line = raw.strip()
        if line == '[language]':
            in_lang = True
            continue
        if in_lang:
            if line.startswith('['):
                break
            if '=' in line and not line.startswith(';'):
                key, _, rest = line.partition('=')
                suffix = rest.split(';')[0].strip()
                result[key.strip()] = suffix
    return result


def folder_lang(folder_name: str, lang_suffixes: dict[str, str]) -> str | None:
    """
    Return the language key whose suffix matches the end of folder_name.
    Non-empty suffixes are tried longest-first so 'player_eng' beats 'player'.
    Falls back to the language with an empty suffix (typically 'rus').
    """
    for lang, suffix in sorted(lang_suffixes.items(), key=lambda kv: len(kv[1]), reverse=True):
        if suffix and folder_name.endswith(suffix):
            return lang
    # fallback: language with no suffix
    for lang, suffix in lang_suffixes.items():
        if not suffix:
            return lang
    return None


def base_category(folder_name: str, lang_suffixes: dict[str, str]) -> str:
    """Strip the language suffix to get the bare category name."""
    for suffix in sorted(lang_suffixes.values(), key=len, reverse=True):
        if suffix and folder_name.endswith(suffix):
            return folder_name[: -len(suffix)]
    return folder_name


def scan_counts(sounds_root: Path, lang_suffixes: dict[str, str]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {k: defaultdict(int) for k in lang_suffixes}

    for category_dir in sounds_root.iterdir():
        if not category_dir.is_dir():
            continue

        lang = folder_lang(category_dir.name, lang_suffixes)
        if lang is None:
            print(f'Warning: skipping unrecognized folder: {category_dir.name}')
            continue

        bare = base_category(category_dir.name, lang_suffixes)
        if bare.lower() in EXCLUDED_CATEGORIES:
            print(f'Warning: skipping excluded category: {bare}')
            continue

        found_any = False
        for f in category_dir.rglob('*'):
            if f.is_dir():
                ogg_files = list(f.glob('*.ogg'))
                if not ogg_files:
                    counts[lang][f.name] += 0
                    found_any = True
                continue
            m = INDEXED_OGG.match(f.name)
            if not m:
                print(f'Warning: skipping non-matching file: {f.name} in {category_dir.name}')
                continue
            is_muffled = bool(m.group(1))
            if is_muffled:
                continue
            base_name = m.group(2)
            counts[lang][base_name] += 1
            found_any = True

        if not found_any:
            counts[lang][bare] = 0

    return {k: dict(v) for k, v in counts.items()}


def format_section(lang_key: str, counts: dict[str, int]) -> str:
    lines = [f'[lines_{lang_key}]']
    for key in sorted(counts, key=str.casefold):
        if counts[key] > 0:
            lines.append(f'{key} = {counts[key]}')
    return '\n'.join(lines)


def rewrite_ltx(original: str, lang_suffixes: dict[str, str], counts: dict[str, dict[str, int]]) -> str:
    """Replace every [lines_*] section body with fresh data; preserve everything else."""
    target_sections = {f'lines_{k}' for k in lang_suffixes}
    out_lines = []
    lines = original.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        raw = lines[i]
        m = SECTION_RE.match(raw.strip())
        if m and m.group(1) in target_sections:
            lang_key = m.group(1)[len('lines_'):]
            out_lines.append(format_section(lang_key, counts.get(lang_key, {})))
            i += 1
            # skip the old body until the next section header or EOF
            while i < len(lines):
                if SECTION_RE.match(lines[i].strip()):
                    break
                i += 1
            out_lines.append('')  # blank separator
        else:
            out_lines.append(raw.rstrip('\n').rstrip('\r'))
            i += 1
    return '\n'.join(out_lines) + '\n'


def report_differences(counts: dict[str, dict[str, int]], lang_suffixes: dict[str, str]) -> None:
    """Print keys that are present in some languages but missing in others."""
    all_keys: dict[str, set[str]] = {lang: set(data.keys()) for lang, data in counts.items()}
    union = set()
    for keys in all_keys.values():
        union |= keys

    has_diff = False
    for lang in sorted(lang_suffixes):
        missing = sorted(union - all_keys.get(lang, set()), key=str.casefold)
        if missing:
            has_diff = True
            print(f'\n[lines_{lang}] is missing {len(missing)} key(s):')
            for k in missing:
                present_in = [l for l in sorted(lang_suffixes) if k in all_keys.get(l, set())]
                print(f'  {k}  (present in: {", ".join(present_in)})')

    if not has_diff:
        print('\nAll languages have identical keys.')


def reaction_title(name: str) -> str:
    """Convert reaction name to a human-readable title.

    'loot_open_box' -> 'Loot open box'
    """
    words = name.replace('_', ' ').lower()
    return words[:1].upper() + words[1:]


def write_generated_script(path: Path, reactions: list[str]) -> None:
    """Write varefined_mcm_generated.script with all reactions."""
    entries = ',\n'.join(f'        "{r}"' for r in reactions)
    content = (
        'function load_generated()\n'
        '    return {\n'
        f'{entries}\n'
        '    }\n'
        'end\n'
    )
    path.write_text(content, encoding='utf-8')


def write_generated_xml(path: Path, reactions: list[str]) -> None:
    """Write _ui_mcm_varefined_generated.xml with a title entry per reaction."""
    entries = []
    for r in reactions:
        string_id = f'ui_mcm_varefined_varefined_generated_chance_{r}'
        title = reaction_title(r)
        entries.append(
            f'    <string id="{string_id}">\n'
            f'        <text>{title}</text>\n'
            f'    </string>'
        )
    content = (
        '<?xml version="1.0" encoding="windows-1251"?>\n\n'
        '<string_table>\n'
        + '\n'.join(entries)
        + '\n</string_table>\n'
    )
    path.write_text(content, encoding='windows-1251')


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Sync [lines_*] sections in varefined.ltx from actual .ogg files '
                    'and regenerate MCM generated files.'
    )
    parser.add_argument(
        '--ltx',
        default='gamedata/configs/plugins/varefined.ltx',
        help='Path to varefined.ltx',
    )
    parser.add_argument(
        '--sounds',
        default='gamedata/sounds/characters_voice',
        help='Path to characters_voice sounds directory',
    )
    parser.add_argument(
        '--generated-script',
        default='gamedata/scripts/varefined_mcm_generated.script',
        help='Path to varefined_mcm_generated.script to regenerate',
    )
    parser.add_argument(
        '--generated-xml',
        default='gamedata/configs/text/eng/_ui_mcm_varefined_generated.xml',
        help='Path to _ui_mcm_varefined_generated.xml to regenerate',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print results without writing any files',
    )
    parser.add_argument(
        '--diff-only',
        action='store_true',
        help='Only report differences between languages, do not rewrite files',
    )
    args = parser.parse_args()

    ltx_path = Path(args.ltx)
    sounds_root = Path(args.sounds)

    if not ltx_path.is_file():
        print(f'Error: ltx not found: {ltx_path}')
        return 1
    if not sounds_root.is_dir():
        print(f'Error: sounds dir not found: {sounds_root}')
        return 1

    original = ltx_path.read_text(encoding='utf-8')
    lang_suffixes = parse_languages(original)
    if not lang_suffixes:
        print('Error: no languages found in [language] section')
        return 1

    counts = scan_counts(sounds_root, lang_suffixes)

    for lang, data in sorted(counts.items()):
        print(f'[lines_{lang}]: {len(data)} entries  ->  ' + ', '.join(sorted(data, key=str.casefold)[:6]) + (
            '…' if len(data) > 6 else ''))

    report_differences(counts, lang_suffixes)

    if args.diff_only:
        return 0

    all_reactions = sorted(
        {key for lang_counts in counts.values() for key, cnt in lang_counts.items() if cnt > 0},
        key=str.casefold,
    )

    new_ltx = rewrite_ltx(original, lang_suffixes, counts)

    if args.dry_run:
        print('\n--- varefined.ltx result ---')
        print(new_ltx)
        print('\n--- varefined_mcm_generated.script ---')
        entries = ',\n'.join(f'        "{r}"' for r in all_reactions)
        print(f'function load_generated()\n    return {{\n{entries}\n    }}\nend')
        print('\n--- _ui_mcm_varefined_generated.xml ---')
        for r in all_reactions:
            print(f'  {r!r}  ->  {reaction_title(r)!r}')
    else:
        ltx_path.write_text(new_ltx, encoding='utf-8')
        print(f'Written: {ltx_path}')

        write_generated_script(Path(args.generated_script), all_reactions)
        print(f'Written: {args.generated_script}  ({len(all_reactions)} reactions)')

        write_generated_xml(Path(args.generated_xml), all_reactions)
        print(f'Written: {args.generated_xml}')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
