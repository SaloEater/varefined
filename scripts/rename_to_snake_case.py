#!/usr/bin/env python3
"""Rename folders from PascalCase/CamelCase to snake_case, bottom-up.

Guarantees all output folder names are fully lowercase.
Handles Windows case-insensitive filesystem via temp-name two-step rename.
"""

import os
import re
import sys
import uuid
import argparse


def to_snake_case(name: str) -> str:
    """Convert PascalCase or CamelCase (with optional _ separators) to snake_case."""
    # Insert underscore before uppercase letters that follow lowercase or digits
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    # Insert underscore before uppercase letters followed by lowercase (e.g. "AIC" -> keep as-is but handle "AICase")
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)
    return s.lower()


def rename_folders(root: str, dry_run: bool = False) -> None:
    """Rename all folders under root from PascalCase to snake_case, deepest first."""
    # Collect all dirs bottom-up so renames don't break parent paths
    dirs_to_rename = []
    for dirpath, dirnames, _ in os.walk(root, topdown=False):
        for dirname in dirnames:
            new_name = to_snake_case(dirname)
            if new_name != dirname:
                dirs_to_rename.append((dirpath, dirname, new_name))

    if not dirs_to_rename:
        print("No folders need renaming.")
        return

    for dirpath, old_name, new_name in dirs_to_rename:
        old_path = os.path.join(dirpath, old_name)
        new_path = os.path.join(dirpath, new_name)
        if dry_run:
            print(f"  {old_path}  ->  {new_name}")
        else:
            # On Windows the filesystem is case-insensitive, so os.path.exists
            # returns True for case-only renames (e.g. "AIC" -> "aic").
            # Check with exact case by listing the parent directory.
            siblings = os.listdir(dirpath)
            if new_name in siblings and new_name != old_name:
                print(f"SKIP (already exists): {old_path} -> {new_path}")
                continue
            if old_name.lower() == new_name:
                # Case-only rename: go via a temp name to satisfy Windows
                temp_path = os.path.join(dirpath, f"_tmp_{uuid.uuid4().hex}")
                os.rename(old_path, temp_path)
                os.rename(temp_path, new_path)
            else:
                os.rename(old_path, new_path)
            print(f"Renamed: {old_name} -> {new_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename nested folders from PascalCase to snake_case.")
    parser.add_argument("path", help="Root directory to process")
    parser.add_argument("--dry-run", action="store_true", help="Preview renames without making changes")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: '{args.path}' is not a directory.")
        sys.exit(1)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Processing: {args.path}\n")
    rename_folders(args.path, dry_run=args.dry_run)
    print("\nDone.")
