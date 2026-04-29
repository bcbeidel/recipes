---
name: Audit Dimensions for Recipe-Cards
description: Per-dimension rubric used by check-recipe-card. Each entry maps to the principles doc section it enforces.
---

# Audit Dimensions

Each dimension has: *what it checks*, *pass*, *fail*, *severity*,
*principles section enforced*. Dimensions are grouped Tier-1
(deterministic, script-enforceable), Tier-2 (judgment), Tier-3
(cross-vault).

The principles doc lives at
`../../_shared/recipe-card-best-practices.md` — section names below
refer to that doc.

## Tier-1 — Deterministic

### frontmatter-present

- **Checks:** File begins with YAML frontmatter delimited by `---`.
- **Pass:** Frontmatter block present at line 1.
- **Fail:** No frontmatter or malformed delimiters.
- **Severity:** error.
- **Enforces:** *Anatomy*.

### required-fields-present

- **Checks:** Frontmatter contains `aliases`, `tags`, `meal-type`
  (or the file is in `basics/`), `cooking-time-minutes`, `url` (for
  non-basics).
- **Pass:** Every required field present for the card's folder.
- **Fail:** Any required field missing.
- **Severity:** error.
- **Enforces:** *Anatomy*.

### aliases-shape

- **Checks:** `aliases:` is a YAML list with ≥1 string.
- **Pass:** List with at least one quoted string.
- **Fail:** Empty list, scalar, or missing.
- **Severity:** error.
- **Enforces:** *Anatomy*.

### meal-type-value

- **Checks:** `meal-type:` ∈ {dinner, breakfast, lunch, side,
  dessert, appetizer} (singular form), or absent for `basics/` cards.
- **Pass:** Value matches one of the six singular forms, or absent
  in `basics/`.
- **Fail:** Plural form (`dinners`), unknown value, or absent in a
  non-basics folder.
- **Severity:** error.
- **Enforces:** *Anatomy*; RESOLVER.md filing table.

### folder-meal-type-match

- **Checks:** File's parent folder matches `meal-type:` per the
  FOLDERS map in `scripts/transform_recipes.py`
  (`dinner→dinner/`, `side→sides/`, `dessert→desserts/`,
  `appetizer→appetizers/`, `breakfast→breakfast/`, `lunch→lunch/`).
- **Pass:** Folder matches the mapping.
- **Fail:** Mismatch.
- **Severity:** error.
- **Enforces:** RESOLVER.md filing table.

### filename-kebab-case

- **Checks:** Filename stem matches `^[a-z0-9]+(-[a-z0-9]+)*$`.
- **Pass:** Match.
- **Fail:** Capital letters, underscores, spaces, or punctuation.
- **Severity:** error.
- **Enforces:** *Anatomy*.

### filename-no-curly-apostrophes

- **Checks:** Filename contains no `'`, `'`, `"`, or `"`.
- **Pass:** ASCII only.
- **Fail:** Curly char present.
- **Severity:** error.
- **Enforces:** *Anti-Patterns*.

### body-has-ingredients

- **Checks:** Body contains a `## Ingredients` heading.
- **Pass:** Heading present.
- **Fail:** Missing or differently capitalized.
- **Severity:** error.
- **Enforces:** *Anatomy*.

### body-has-preparation

- **Checks:** Body contains a `## Preparation` heading.
- **Pass:** Heading present.
- **Fail:** Missing or wrong heading text (`## Steps`, `## Method`).
- **Severity:** error.
- **Enforces:** *Anatomy*.

### body-section-order

- **Checks:** `## Ingredients` appears before `## Preparation`.
- **Pass:** Correct order.
- **Fail:** Reversed.
- **Severity:** error.
- **Enforces:** *Anatomy*.

### description-not-placeholder

- **Checks:** `description:` is not literally `> Description`,
  `Description`, or empty when present.
- **Pass:** Non-placeholder string (or field absent).
- **Fail:** Placeholder.
- **Severity:** error.
- **Enforces:** *Anti-Patterns* (description as body fragment).

### description-not-first-ingredient

- **Checks:** `description:` does not start with `- `, `FOR THE`,
  `For The`, `For the`, or other patterns matching a body fragment.
- **Pass:** Looks like a sentence (or field absent).
- **Fail:** Looks scraped from the body.
- **Severity:** error.
- **Enforces:** *Anti-Patterns*.

### url-present

- **Checks:** `url:` field exists and looks like a URL
  (`http(s)://`) for non-basics cards.
- **Pass:** Valid-looking URL, or `null` only for `basics/`.
- **Fail:** Missing or non-URL string for non-basics.
- **Severity:** warning (basics may use cookbook citations elsewhere
  in the file).
- **Enforces:** *Patterns That Work* (cite well-known sources).

### cooking-time-minutes-int

- **Checks:** `cooking-time-minutes:` parses as an integer.
- **Pass:** Integer or `null`.
- **Fail:** String, float, or non-numeric.
- **Severity:** warning.
- **Enforces:** *Anatomy*; required for the Dataview quick-weeknights
  query in `_index.md`.

## Tier-2 — Judgment

### description-is-summary

- **Checks:** `description:` is a one-sentence functional description
  of the dish.
- **Pass:** Names the dish + one distinguishing feature.
- **Fail:** Generic, missing, or doesn't describe what it is.
- **Severity:** warning.
- **Enforces:** *Patterns That Work*.

### ingredients-noun-phrase-form

- **Checks:** Ingredient bullets are noun phrases with quantity, not
  imperative steps.
- **Pass:** "1 pound ground chicken" (noun phrase with quantity).
- **Fail:** "Brown the butter" (imperative — belongs in Preparation).
- **Severity:** warning.
- **Enforces:** *Patterns That Work*.

### preparation-imperative-voice

- **Checks:** Numbered steps use imperative voice.
- **Pass:** "Heat the oven."
- **Fail:** "The oven is heated." or "I heat the oven."
- **Severity:** warning.
- **Enforces:** *Patterns That Work*.

### ingredient-step-coverage

- **Checks:** Every listed ingredient is referenced in at least one
  preparation step.
- **Pass:** All referenced.
- **Fail:** Orphan ingredient.
- **Severity:** warning.
- **Enforces:** *Anti-Patterns* (steps reference ingredients not in
  the list — inverse).

### mise-en-place-order

- **Checks:** Ingredients are listed in order of first use.
- **Pass:** Order matches first-use sequence in steps.
- **Fail:** Significant reordering (alphabetical, by category).
- **Severity:** info.
- **Enforces:** *Patterns That Work*.

### unit-consistency

- **Checks:** Units are imperial XOR metric (or paired in
  parentheses).
- **Pass:** Consistent system, or paired (`1 pound (450g)`).
- **Fail:** Mixed without conversion.
- **Severity:** info.
- **Enforces:** *Patterns That Work*.

### citation-quality

- **Checks:** Source is a named cookbook, test kitchen, or named
  author per AGENTS.md.
- **Pass:** Named, credible source (NYT Cooking, Serious Eats, ATK,
  Bon Appétit, named cookbook author, etc.).
- **Fail:** Uncredited blog or AI-generated content.
- **Severity:** warning (or **error** if AI-generated).
- **Enforces:** AGENTS.md *Bias to well-cited sources*.

## Tier-3 — Cross-Vault

### alias-uniqueness

- **Checks:** Each alias is unique (case-insensitive) across the
  vault.
- **Pass:** Unique.
- **Fail:** Two cards share an alias.
- **Severity:** error.
- **Enforces:** *Patterns That Work* (one alias = one card).

### filename-uniqueness

- **Checks:** Each filename stem is unique across all seven recipe
  folders.
- **Pass:** Unique.
- **Fail:** Two cards share a stem.
- **Severity:** error.
- **Enforces:** *Anatomy* (filename is the canonical id).

### wikilink-targets-resolve

- **Checks:** Every `[[target]]` in any card resolves to a card
  filename or alias.
- **Pass:** Resolves.
- **Fail:** Dangling link.
- **Severity:** warning.
- **Enforces:** *Patterns That Work* (wikilinks to basics).

### meal-type-folder-consistency-vault

- **Checks:** Vault-wide pass of `folder-meal-type-match`. Reports
  the count and list of mismatches across the entire vault.
- **Pass:** Zero mismatches.
- **Fail:** Any mismatch.
- **Severity:** error.
- **Enforces:** RESOLVER.md filing table.
