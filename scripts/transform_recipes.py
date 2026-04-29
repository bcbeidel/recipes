#!/usr/bin/env python3
"""Transform recipe vault for Obsidian.

Per-file:
  1. Strip curly apostrophes from filename
  2. Rename frontmatter `name:` -> `aliases:` (list, ASCII apostrophe in value)
  3. Decide target folder from `meal-type` (or `basics/` if missing)
  4. Convert "X (see recipe)" patterns to [[wikilinks]] using alias dictionary
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/bbeidel/Documents/git/recipes")
FOLDERS = {
    "dinner": "dinner",
    "breakfast": "breakfast",
    "lunch": "lunch",
    "side": "sides",
    "dessert": "desserts",
    "appetizer": "appetizers",
}
DEFAULT_FOLDER = "basics"
SKIP = {"AGENTS.md", "CLAUDE.md", "_index.md"}
RESERVED_DIRS = {"dinner", "breakfast", "lunch", "sides", "desserts", "appetizers", "basics", ".obsidian", ".git"}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
NAME_LINE_RE = re.compile(r'^name:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)
MEALTYPE_RE = re.compile(r'^meal-type:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)


def strip_curly(s: str) -> str:
    return s.replace("’", "").replace("‘", "")


def fix_alias_value(s: str) -> str:
    # Curly -> ASCII apostrophe in display value, fix capitalization e.g. Butcher’S -> Butcher's
    out = s.replace("’", "'").replace("‘", "'")
    out = re.sub(r"'S\b", "'s", out)
    out = re.sub(r"'Ve\b", "'ve", out)
    out = re.sub(r"'T\b", "'t", out)
    out = re.sub(r"'Re\b", "'re", out)
    out = re.sub(r"'Ll\b", "'ll", out)
    out = re.sub(r"'D\b", "'d", out)
    return out


def parse_frontmatter(text: str) -> tuple[str, str] | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    return m.group(1), text[m.end():]


def collect_recipes() -> list[Path]:
    return sorted(p for p in ROOT.glob("*.md") if p.name not in SKIP)


def build_alias_index(files: list[Path]) -> dict[str, str]:
    """Map lowercased alias -> new filename stem (without curly apostrophes)."""
    index: dict[str, str] = {}
    for p in files:
        text = p.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm:
            continue
        m = NAME_LINE_RE.search(fm[0])
        if not m:
            continue
        alias = fix_alias_value(m.group(1).strip().strip('"'))
        new_stem = strip_curly(p.stem)
        index[alias.lower()] = new_stem
    return index


def transform_body(body: str, alias_index: dict[str, str], self_stem: str) -> tuple[str, list[str]]:
    """Convert 'Name, ... (see recipe)' patterns to wikilinks. Returns (body, links_added)."""
    links: list[str] = []

    def replace(match: re.Match) -> str:
        prefix = match.group(1)  # whitespace/list marker
        name_phrase = match.group(2).strip()
        rest = match.group(3)  # the rest of the line up to (see recipe)
        # Try alias resolution: look for the longest matching alias at the start of name_phrase
        name_lower = name_phrase.lower()
        target = None
        # Direct match on the noun phrase before any comma
        head = name_lower.split(",")[0].strip()
        if head in alias_index:
            target = alias_index[head]
            display = name_phrase.split(",")[0].strip()
        # Fallback: full lowercased phrase
        elif name_lower in alias_index:
            target = alias_index[name_lower]
            display = name_phrase
        if target and target != self_stem:
            links.append(f"{display} -> {target}")
            after = name_phrase[len(display):]  # comma + remainder
            # Drop the "(see recipe)" marker — the wikilink replaces it
            return f"{prefix}[[{target}|{display}]]{after}"
        return match.group(0)

    pattern = re.compile(r"^(\s*-\s+)([^(\n]+?)(\s*\(see recipe\))", re.MULTILINE)
    new_body = pattern.sub(replace, body)
    return new_body, links


def transform_file(path: Path, alias_index: dict[str, str]) -> dict | None:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if not fm:
        return None
    fm_block, body = fm

    name_match = NAME_LINE_RE.search(fm_block)
    if not name_match:
        return {"path": path, "skip_reason": "no name field"}

    alias_value = fix_alias_value(name_match.group(1).strip().strip('"'))
    new_fm = NAME_LINE_RE.sub(f'aliases:\n  - "{alias_value}"', fm_block, count=1)

    mt_match = MEALTYPE_RE.search(fm_block)
    meal_type = mt_match.group(1).strip().strip('"') if mt_match else None
    folder = FOLDERS.get(meal_type, DEFAULT_FOLDER)

    new_body, links = transform_body(body, alias_index, strip_curly(path.stem))

    new_stem = strip_curly(path.stem)
    new_path = ROOT / folder / f"{new_stem}.md"
    new_text = f"---\n{new_fm}---\n{new_body}"

    return {
        "path": path,
        "new_path": new_path,
        "renamed_filename": path.stem != new_stem,
        "moved": True,
        "alias": alias_value,
        "meal_type": meal_type,
        "folder": folder,
        "links_added": links,
        "new_text": new_text,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Actually move/edit files")
    ap.add_argument("--limit", type=int, default=None, help="Only process N files (for pilot)")
    ap.add_argument("--only", nargs="*", help="Only process these filenames")
    args = ap.parse_args()

    files = collect_recipes()
    alias_index = build_alias_index(files)

    if args.only:
        files = [f for f in files if f.name in set(args.only)]
    elif args.limit:
        files = files[: args.limit]

    plans = []
    for p in files:
        plan = transform_file(p, alias_index)
        if plan is None:
            print(f"SKIP no-frontmatter: {p.name}")
            continue
        if "skip_reason" in plan:
            print(f"SKIP {plan['skip_reason']}: {p.name}")
            continue
        plans.append(plan)

    print(f"\n{'APPLY' if args.apply else 'DRY-RUN'}: {len(plans)} file(s)")
    print(f"Alias index: {len(alias_index)} entries\n")

    total_links = 0
    for plan in plans:
        old = plan["path"].relative_to(ROOT)
        new = plan["new_path"].relative_to(ROOT)
        marks = []
        if plan["renamed_filename"]:
            marks.append("RENAMED")
        if plan["meal_type"] is None:
            marks.append("NO-MEAL-TYPE")
        if plan["links_added"]:
            marks.append(f"+{len(plan['links_added'])} links")
            total_links += len(plan["links_added"])
        marks_str = f" [{', '.join(marks)}]" if marks else ""
        print(f"  {old}  ->  {new}{marks_str}")
        for link in plan["links_added"]:
            print(f"      link: {link}")

    print(f"\nTotal cross-reference links added: {total_links}")

    if not args.apply:
        return 0

    for plan in plans:
        old_path = plan["path"]
        new_path = plan["new_path"]
        new_path.parent.mkdir(parents=True, exist_ok=True)
        # Write transformed content to new path, then git mv (or fallback)
        if old_path == new_path:
            new_path.write_text(plan["new_text"], encoding="utf-8")
            continue
        # Use git mv to preserve history when possible
        try:
            subprocess.run(["git", "-C", str(ROOT), "mv", str(old_path.relative_to(ROOT)), str(new_path.relative_to(ROOT))], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            shutil.move(str(old_path), str(new_path))
        new_path.write_text(plan["new_text"], encoding="utf-8")

    print(f"\nApplied {len(plans)} transforms.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
