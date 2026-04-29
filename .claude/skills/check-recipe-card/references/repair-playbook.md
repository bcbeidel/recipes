---
name: Repair Playbook for Recipe-Cards
description: For each audit dimension, the diagnosis and the fix recipe — auto-applicable for Tier-1, propose-diff for Tier-2 / Tier-3.
---

# Repair Playbook

Each entry: *Finding → Diagnosis → Fix Recipe*. Tier-1 fixes are
auto-applicable; Tier-2/3 fixes are propose-diff.

The principles doc lives at
`../../_shared/recipe-card-best-practices.md`. The dimension catalog
is in `audit-dimensions.md` (sibling to this file).

## Tier-1 — Auto-fix

### frontmatter-present

- **Diagnosis:** File saved without YAML frontmatter (likely a
  partial paste or a hand-written stub).
- **Fix:** Insert a frontmatter block at line 1 with the fields from
  the *Anatomy* template; populate from filename and best-effort
  body parse; tag `needs-review`.

### required-fields-present

- **Diagnosis:** Importer dropped a field, or schema evolved.
- **Fix:** Append missing fields with sensible defaults: `tags:
  [recipe]` if missing; `cooking-time-minutes: null` if unknown;
  `aliases:` derived from the filename in Title Case. Tag
  `needs-review` for any null required field.

### aliases-shape

- **Diagnosis:** `aliases:` was a scalar (legacy `name:` field) or
  empty — typically pre-`transform_recipes.py` content.
- **Fix:** Convert to a YAML list with one Title Case string derived
  from the filename, e.g. `aliases:\n  - "Basic Pesto Sauce"`.

### meal-type-value

- **Diagnosis:** Plural form (`dinners`) or wrong taxonomy.
- **Fix:** Map plural→singular. If unmappable, set to `null` and
  move the file to `basics/` per the FOLDERS-default convention.

### folder-meal-type-match

- **Diagnosis:** Card was filed before `meal-type` was set, or moved
  manually without updating frontmatter.
- **Fix:** `git mv <card> <correct-folder>/<card>` per the FOLDERS
  map in `transform_recipes.py`. Verify Dataview query coverage in
  `_index.md` afterward (the queries pull `FROM "<folder>"`).

### filename-kebab-case

- **Diagnosis:** Imported with capitalization, spaces, or
  underscores.
- **Fix:** Rename via `git mv` to a kebab-case stem. Update any
  wikilinks pointing at the old name.

### filename-no-curly-apostrophes

- **Diagnosis:** Imported from a source with smart quotes.
- **Fix:** `git mv` to ASCII-stripped stem (remove the apostrophe,
  per `transform_recipes.py:strip_curly`). Display alias keeps the
  ASCII `'`.

### body-has-ingredients / body-has-preparation

- **Diagnosis:** Heading has wrong text (`## Method`,
  `## Instructions`) or is missing entirely.
- **Fix:** Replace heading text with `## Ingredients` or
  `## Preparation`. **If the section is missing entirely**, surface
  a TODO at the top of the body and tag `needs-review` — do not
  invent steps or ingredients.

### body-section-order

- **Diagnosis:** Sections in wrong order (Preparation before
  Ingredients).
- **Fix:** Swap the two section blocks; preserve the `---`
  separator between them.

### description-not-placeholder

- **Diagnosis:** Importer wrote literal `> Description` placeholder.
- **Fix:** Set `description: null` and tag `needs-review`. The
  Tier-2 `description-is-summary` repair path generates a real
  summary on user opt-in.

### description-not-first-ingredient

- **Diagnosis:** Importer scraped the first body line into the
  `description` field — the dominant existing-bug pattern in this
  vault.
- **Fix:** Same as above — set `description: null` and add
  `needs-review`. With user opt-in, generate a summary via the
  Tier-2 path.

### url-present

- **Diagnosis:** Importer dropped the URL.
- **Fix:** Surface a TODO and tag `needs-review`. Do not invent a
  URL — citation integrity is load-bearing per AGENTS.md.

### cooking-time-minutes-int

- **Diagnosis:** Field is a string (`"45 minutes"`) or includes a
  prep/cook split (`"15 prep + 30 cook"`).
- **Fix:** Parse the integer prefix (`"45 minutes"` → `45`). On
  ambiguity (`"1 hour, plus chilling"`), set to total active time
  (`60`) and flag `needs-review`.

## Tier-2 — Propose-Diff

### description-is-summary

- **Diagnosis:** Description is a fragment, generic, or missing.
- **Fix:** Generate a one-sentence summary naming the dish + a
  distinguishing feature, drawing on the alias and ingredients.
  Present as a proposed diff; user accepts or edits before write.

### ingredients-noun-phrase-form

- **Diagnosis:** A bullet was written as an imperative step.
- **Fix:** Propose a rewrite as a noun phrase with quantity, plus a
  new step in `## Preparation` that captures the displaced action.
  User reviews because the displacement may need step renumbering.

### preparation-imperative-voice

- **Diagnosis:** Step uses passive voice or first-person.
- **Fix:** Propose an imperative rewrite of the offending step.

### ingredient-step-coverage

- **Diagnosis:** Step references an ingredient not listed (or vice
  versa).
- **Fix:** Propose adding the missing bullet (with TODO for quantity
  if uncertain) **OR** removing the orphan ingredient. **Never
  invent quantities** — tag `needs-review` if the source is
  ambiguous.

### mise-en-place-order

- **Diagnosis:** Ingredients listed alphabetically or by category
  rather than by first use.
- **Fix:** Propose a reordered ingredients block. User reviews
  because reorder may break sub-grouped (`FOR THE...`) headings.

### unit-consistency

- **Diagnosis:** Mix of metric and imperial without parens.
- **Fix:** Propose paired units (`1 pound (450g)`) or pick one
  system and convert. User chooses the system; do not auto-pick.

### citation-quality

- **Diagnosis:** URL points to an uncredited blog or AI source.
- **Fix:** Tag `needs-review`; propose finding a credible
  alternative source for the same recipe. **Do NOT auto-replace** —
  citation integrity matters.

## Tier-3 — Propose-Diff

### alias-uniqueness

- **Diagnosis:** Two cards share an alias (e.g., both call
  themselves "Pesto").
- **Fix:** Propose disambiguating one alias (e.g., `"Basic Pesto
  Sauce"` vs `"Pistachio Pesto"`); update `aliases:` lists; rebuild
  any wikilinks that pointed at the now-removed alias.

### filename-uniqueness

- **Diagnosis:** Two cards have the same stem in different folders
  (rare but possible after manual moves).
- **Fix:** Propose disambiguating filenames; `git mv`; update
  wikilinks pointing at either.

### wikilink-targets-resolve

- **Diagnosis:** `[[target]]` does not resolve to a file or alias.
- **Fix:** Try alias-index lookup (per
  `transform_recipes.py:build_alias_index` pattern). On hit, rewrite
  to the resolved stem; on miss, surface a TODO and tag
  `needs-review`.

### meal-type-folder-consistency-vault

- **Diagnosis:** Vault-wide drift (multiple cards in wrong folder).
- **Fix:** Propose a batched `git mv` plan; user reviews the full
  list before applying. Rerun Tier-1 after to confirm zero
  mismatches.
