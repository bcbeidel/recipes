#!/usr/bin/env python3
"""Tier-1 deterministic audit for recipe-cards.

Implements every Tier-1 dimension from
`.claude/skills/check-recipe-card/references/audit-dimensions.md`.

Stdlib only. Frontmatter parsing reuses the regex pattern from
`scripts/transform_recipes.py`.

Exits:
  0 — no findings
  1 — one or more findings
  2 — invocation error (bad args, unreadable file)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FOLDER_FOR_MEAL_TYPE = {
    "dinner": "dinner",
    "breakfast": "breakfast",
    "lunch": "lunch",
    "side": "sides",
    "dessert": "desserts",
    "appetizer": "appetizers",
}
RECIPE_FOLDERS = {"dinner", "breakfast", "lunch", "sides", "desserts", "appetizers", "basics"}
VALID_MEAL_TYPES = set(FOLDER_FOR_MEAL_TYPE.keys())

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
SCALAR_FIELD_RE = re.compile(r'^([a-z][a-z0-9-]*):\s*"?([^"\n]*?)"?\s*$', re.MULTILINE)
LIST_FIELD_HEAD_RE = re.compile(r'^([a-z][a-z0-9-]*):\s*\n((?:\s+-\s+.+\n?)+)', re.MULTILINE)
KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CURLY_CHARS = {"’", "‘", "“", "”"}
DESCRIPTION_PLACEHOLDERS = {"> Description", "Description", ""}
DESCRIPTION_BAD_PREFIXES = ("- ", "FOR THE", "For The", "For the", "FOR ", "* ")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def parse_frontmatter(text: str) -> tuple[str, str] | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    return m.group(1), text[m.end():]


def get_scalar(fm: str, key: str) -> str | None:
    for m in SCALAR_FIELD_RE.finditer(fm):
        if m.group(1) == key:
            return m.group(2)
    return None


def has_field(fm: str, key: str) -> bool:
    if get_scalar(fm, key) is not None:
        return True
    for m in LIST_FIELD_HEAD_RE.finditer(fm):
        if m.group(1) == key:
            return True
    return False


def get_list(fm: str, key: str) -> list[str] | None:
    for m in LIST_FIELD_HEAD_RE.finditer(fm):
        if m.group(1) == key:
            items = []
            for line in m.group(2).splitlines():
                stripped = line.strip()
                if stripped.startswith("- "):
                    items.append(stripped[2:].strip().strip('"'))
            return items
    return None


def find(file: Path, dimension: str, severity: str, message: str, snippet: str | None = None) -> dict:
    return {
        "file": str(file),
        "dimension": dimension,
        "severity": severity,
        "message": message,
        "snippet": snippet,
    }


def audit_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [find(path, "file-readable", "error", f"unreadable: {e}")]

    folder = path.parent.name
    stem = path.stem
    in_basics = folder == "basics"

    # filename-kebab-case
    if not KEBAB_RE.match(stem):
        findings.append(find(path, "filename-kebab-case", "error",
                             "filename stem is not kebab-case", stem))

    # filename-no-curly-apostrophes
    curly = [c for c in stem if c in CURLY_CHARS]
    if curly:
        findings.append(find(path, "filename-no-curly-apostrophes", "error",
                             f"filename contains curly chars: {curly!r}", stem))

    fm_split = parse_frontmatter(text)
    if fm_split is None:
        findings.append(find(path, "frontmatter-present", "error",
                             "no YAML frontmatter found"))
        return findings
    fm, body = fm_split

    # required-fields-present
    required = ["aliases", "tags", "cooking-time-minutes"]
    if not in_basics:
        required.append("meal-type")
        required.append("url")
    for key in required:
        if not has_field(fm, key):
            findings.append(find(path, "required-fields-present", "error",
                                 f"missing required field: {key}"))

    # aliases-shape
    aliases = get_list(fm, "aliases")
    if aliases is None or len(aliases) == 0:
        findings.append(find(path, "aliases-shape", "error",
                             "aliases must be a non-empty list"))

    # meal-type-value
    meal_type = get_scalar(fm, "meal-type")
    if meal_type is not None:
        meal_type = meal_type.strip()
        if meal_type and meal_type not in VALID_MEAL_TYPES and meal_type != "null":
            findings.append(find(path, "meal-type-value", "error",
                                 f"meal-type must be one of {sorted(VALID_MEAL_TYPES)}",
                                 meal_type))
    elif not in_basics:
        findings.append(find(path, "meal-type-value", "error",
                             f"meal-type required for cards outside basics/ (folder={folder})"))

    # folder-meal-type-match
    if meal_type and meal_type in FOLDER_FOR_MEAL_TYPE:
        expected_folder = FOLDER_FOR_MEAL_TYPE[meal_type]
        if folder != expected_folder:
            findings.append(find(path, "folder-meal-type-match", "error",
                                 f"meal-type={meal_type} expects folder={expected_folder}, got {folder}"))
    elif in_basics and meal_type and meal_type != "null":
        # meal-type set in basics — should be empty or null
        findings.append(find(path, "folder-meal-type-match", "error",
                             f"basics/ card has meal-type={meal_type}; move to {FOLDER_FOR_MEAL_TYPE.get(meal_type, '?')}/"))

    # body-has-ingredients / body-has-preparation / body-section-order
    ing_idx = body.find("## Ingredients")
    prep_idx = body.find("## Preparation")
    if ing_idx == -1:
        findings.append(find(path, "body-has-ingredients", "error",
                             "missing ## Ingredients heading"))
    if prep_idx == -1:
        findings.append(find(path, "body-has-preparation", "error",
                             "missing ## Preparation heading"))
    if ing_idx != -1 and prep_idx != -1 and ing_idx > prep_idx:
        findings.append(find(path, "body-section-order", "error",
                             "## Ingredients must precede ## Preparation"))

    # description-not-placeholder / description-not-first-ingredient
    description = get_scalar(fm, "description")
    if description is not None:
        desc = description.strip()
        if desc in DESCRIPTION_PLACEHOLDERS:
            findings.append(find(path, "description-not-placeholder", "error",
                                 "description is a placeholder", desc))
        elif desc.startswith(DESCRIPTION_BAD_PREFIXES):
            findings.append(find(path, "description-not-first-ingredient", "error",
                                 "description looks scraped from body", desc[:80]))

    # url-present
    url_val = get_scalar(fm, "url")
    if not in_basics:
        if url_val is None or url_val.strip() in ("", "null"):
            findings.append(find(path, "url-present", "warning",
                                 "url field missing or null"))
        elif not URL_RE.match(url_val.strip()):
            findings.append(find(path, "url-present", "warning",
                                 "url does not look like http(s)://", url_val))

    # cooking-time-minutes-int
    ctm_val = get_scalar(fm, "cooking-time-minutes")
    if ctm_val is not None and ctm_val.strip() not in ("", "null"):
        try:
            int(ctm_val.strip())
        except ValueError:
            findings.append(find(path, "cooking-time-minutes-int", "warning",
                                 "cooking-time-minutes must be an integer", ctm_val))

    return findings


def collect_targets(args_files: list[str], folder: str | None) -> list[Path]:
    targets: list[Path] = []
    if folder:
        d = Path(folder)
        if not d.is_dir():
            print(f"error: --folder {folder} is not a directory", file=sys.stderr)
            sys.exit(2)
        targets.extend(sorted(d.glob("*.md")))
    for f in args_files:
        p = Path(f)
        if not p.is_file():
            print(f"error: file not found: {f}", file=sys.stderr)
            sys.exit(2)
        targets.append(p)
    return targets


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Tier-1 deterministic audit for recipe-cards. "
                    "Emits JSON findings to stdout. Exit 0 on clean, 1 on findings, 2 on invocation error.")
    ap.add_argument("--folder", help="Audit every *.md in this folder")
    ap.add_argument("files", nargs="*", help="One or more recipe-card files")
    args = ap.parse_args(argv)

    if not args.folder and not args.files:
        ap.print_help(sys.stderr)
        return 2

    targets = collect_targets(args.files, args.folder)
    all_findings: list[dict] = []
    for path in targets:
        all_findings.extend(audit_file(path))

    summary: dict[str, int] = {}
    for f in all_findings:
        summary[f["dimension"]] = summary.get(f["dimension"], 0) + 1

    output = {
        "audited": len(targets),
        "findings_count": len(all_findings),
        "by_dimension": summary,
        "findings": all_findings,
    }
    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")

    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())
