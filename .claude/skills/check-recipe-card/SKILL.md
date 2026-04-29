---
name: check-recipe-card
description: Use when the user wants to audit one recipe-card or the entire vault for structural, content, and cross-vault drift. Runs Tier-1 deterministic checks via a Python script, optional Tier-2 LLM judgment, and Tier-3 cross-vault checks; on opt-in, drives a repair loop.
allowed-tools: Read, Edit, Bash, Glob, Grep
references:
  - ../_shared/recipe-card-best-practices.md
  - references/audit-dimensions.md
  - references/repair-playbook.md
---

# Check Recipe-Card

Audit recipe-cards against the shared rubric. The principles doc is
the source of truth; `audit-dimensions.md` enumerates pass/fail
criteria; `repair-playbook.md` maps findings to fixes.

**Workflow:** 1. Route → 2. Scope → 3. Tier-1 (script) → 4. Tier-2
(judgment, opt-in) → 5. Tier-3 (cross-vault) → 6. Report → 7. Repair
(opt-in)

## 1. Route

Confirm the user wants an audit, not a build. If they want to:

- *Add* a new card → route to `/build:build-recipe-card`.
- *Re-cook* / consult an index → use `_index.md` directly.

## 2. Scope

Determine the target:

- **Single file** — `<folder>/<file>.md`.
- **Folder** — `dinner/`, `breakfast/`, `lunch/`, `sides/`,
  `desserts/`, `appetizers/`, or `basics/`.
- **Whole vault** — all seven recipe folders.

Confirm with the user before running Tier-2/3 against the whole
vault — those tiers run inline LLM judgment and are not free.

## 3. Tier-1 (deterministic, fast)

Run the Python script:

```bash
python3 .claude/skills/check-recipe-card/scripts/audit_recipe_card.py \
  [<file>... | --folder <path>]
```

The script uses stdlib only and exits 0 on clean / 1 on any finding /
2 on invocation error. It emits JSON findings to stdout. Dimensions
are enumerated in `audit-dimensions.md` under *Tier-1*.

## 4. Tier-2 (judgment, opt-in)

For each card, evaluate the Tier-2 dimensions in
`audit-dimensions.md`. Each is a single LLM-judgment pass: read the
file, score the dimension, report.

**Bound the cost** — ask the user before running across more than one
folder. Tier-2 is per-card LLM work; a vault-wide Tier-2 sweep is a
deliberate decision, not a default.

## 5. Tier-3 (cross-vault)

Cross-card and vault-wide checks. Run **after** Tier-1 because the
deterministic findings narrow the scope:

- Build the alias index by reusing the parsing pattern from
  `scripts/transform_recipes.py:build_alias_index`.
- Detect alias collisions, filename collisions across folders,
  unresolved wikilinks, and folder/meal-type drift counted at vault
  scale.

Tier-3 only makes sense over the whole vault. If the user scoped to a
single file, skip Tier-3 and tell them why.

## 6. Report

Group findings by tier and dimension. For each finding include:

- File path
- Dimension name
- Severity (error / warning / info)
- Snippet (the offending value, e.g., the broken `description:`)
- Pointer to the principles-doc section it enforces

Write the report to stdout. For vault-wide sweeps, also write the
JSON findings to a path the caller specifies (e.g.,
`/tmp/recipe-card-audit.json`) for follow-on tooling.

## 7. Repair (opt-in)

If the user opts in:

- **Tier-1 / structural findings** — apply the auto-fix recipe from
  `repair-playbook.md`. These are deterministic (e.g., move file to
  the matching folder, strip curly apostrophes from filename, set a
  broken `description:` to null and tag `needs-review`).
- **Tier-2 / Tier-3 / judgment findings** — propose a diff per the
  playbook template. User reviews each diff before applying.

**Never auto-write Tier-2/3 fixes.** Judgment-derived edits go
through user approval. The Tier-1 fixes are safe to auto-apply
because the rules are mechanical and the failure modes are loud.

## Anti-Pattern Guards

1. **Auto-fixing judgment findings.** Tier-2/3 dimensions are
   LLM-scored; propose, don't apply.
2. **Skipping Tier-1 before Tier-2.** Deterministic findings narrow
   the review surface; running Tier-2 against unsorted data wastes
   cycles.
3. **Running Tier-3 on a single file.** Cross-vault checks need the
   whole vault to be meaningful — refuse and route the user back to
   single-file Tier-1 + Tier-2.
4. **Silently fixing a citation.** `citation-quality` repair is
   propose-only. Citation integrity is load-bearing per AGENTS.md;
   never auto-replace a URL.

## Handoff

**Receives:** target path or folder; user opt-in for Tier-2/3 and
repair.

**Produces:** structured findings report; with opt-in, applied fixes
(Tier-1) and proposed diffs (Tier-2/3).

**Chainable to:** `/build:build-recipe-card` (rebuild a malformed
card from source); a follow-on plan that batches Tier-1 auto-fixes
across the vault.
