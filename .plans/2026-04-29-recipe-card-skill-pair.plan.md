---
name: Recipe-card skill pair (build + check)
description: Scaffold a project-scoped primitive-pair under .claude/skills/ that records recipe-cards from URLs/images/PDFs/text and audits the vault, with a Tier-1 Python audit script and an opt-in repair loop.
type: plan
status: executing
branch: feat/recipe-card-skill-pair
related:
  - .designs/2026-04-29-recipe-card-skill-pair.design.md
  - AGENTS.md
  - RESOLVER.md
  - scripts/transform_recipes.py
---

# Recipe-card skill pair (build + check)

## Goal

Land a project-scoped pair of skills — `build-recipe-card` and
`check-recipe-card` — under `.claude/skills/` that lets the user record
recipes from a cited source into this vault's structured format and audit
the existing 171 recipe-cards against a single shared rubric.

## Scope

### Must have

- A distilled principles doc under `.claude/skills/_shared/` that both
  halves of the pair reference as the single rubric.
- `build-recipe-card/SKILL.md` accepting URL, pasted text, single or
  multi-image, and PDF inputs; with hybrid credibility gating
  (warn-then-confirm for low-credibility sources, tag the resulting
  card); with `TODO:` + `needs-review` ambiguity handling.
- `check-recipe-card/SKILL.md` covering Tier-1 deterministic checks,
  Tier-2 judgment checks, and Tier-3 cross-vault checks; with an
  opt-in repair loop (auto-fix deterministic, propose-diff for
  judgment).
- `audit-dimensions.md` enumerating every Tier-1 / Tier-2 / Tier-3
  dimension with pass/fail criteria and a pointer to the principles-doc
  section it enforces.
- `repair-playbook.md` mapping each finding type to a concrete fix
  recipe (auto-fix code path or proposed-diff template).
- A Tier-1 Python audit script under
  `check-recipe-card/scripts/audit_recipe_card.py` runnable on a single
  file or a folder, exiting non-zero on any deterministic finding.
- `RESOLVER.md` updated to point new recipe filing through
  `/build:build-recipe-card`.
- `AGENTS.md` updated to register the pair in working agreements.
- End-to-end validation: build one new recipe-card from a real source,
  audit it clean; run audit on the existing vault and confirm the
  expected "broken description" finding count.

### Won't have

- A full 171-file repair sweep — that is follow-on work and gets its own
  plan once the pair is approved and the auto-fix paths are trusted.
- Distribution as a portable plugin — the rubric is tightly coupled to
  this vault's `RESOLVER.md`, frontmatter shape, and `AGENTS.md` rules.
- Video or audio transcript ingestion.
- Multi-image stitching inside the skill — caller stitches externally
  and passes a single composite image.
- Modifying `_index.md` Dataview queries (stable infra).
- Touching `attachments/` (image storage).
- Replacing or absorbing `scripts/transform_recipes.py` — that is the
  one-shot import script and remains independent. The Tier-3 alias-index
  audit may borrow its parsing pattern but does not import from it.

## Approach

**Placement decision (load-bearing).** The toolkit's
`/build:build-skill-pair` hardcodes write paths under
`plugins/build/skills/<primitive>/` and
`plugins/build/_shared/references/` (toolkit issue #369:
https://github.com/bcbeidel/toolkit/issues/369). Rather than reinvent
the meta-skill's distillation and rubric-scaffolding work, this plan
**dogfoods `/build:build-skill-pair`** to produce the five artifacts at
its hardcoded locations *inside this repo's working tree*, then
**relocates them** to project-scoped paths under `.claude/skills/` and
patches internal cross-references. The transient `plugins/build/...`
tree is removed in the same task so it never lands in version control.
Project-scoped is correct because the rubric encodes this vault's
`RESOLVER.md` filing rules, the existing 171-file frontmatter shape,
and `AGENTS.md`'s "no invented ingredients" / "well-cited sources"
rules — none of which port to another vault without modification.

**Distillation source.** The principles doc is distilled from in-repo
material exclusively: `AGENTS.md`, `RESOLVER.md`, `_index.md` (for
Dataview field expectations), `scripts/transform_recipes.py` (filing
rules and alias-index pattern), and a sample sweep across the existing
171 recipe-cards. Claude's named knowledge of recipe-writing best
practices supplements where the repo is silent (mise-en-place ordering,
imperative-voice steps, unit consistency). No external URLs needed.

**Validation strategy.** The check half is the easier half to validate
first because it can run against the existing 171 files immediately —
the broken-description bug is a known finding that should appear ~150+
times. The build half is validated by recording one well-cited recipe
end-to-end and running the check half against the result.

**Tier-1 script language.** Python — recipe frontmatter is YAML
(structured data), the existing `scripts/transform_recipes.py` is
Python, and the toolkit's own routing guidance prefers Python for
anything beyond glue. The script lives inside the check skill at
`check-recipe-card/scripts/audit_recipe_card.py` so the skill is
self-contained.

## File changes

### Create

- `.claude/skills/_shared/recipe-card-best-practices.md` — distilled
  principles doc, referenced by both halves
- `.claude/skills/build-recipe-card/SKILL.md` — build workflow
- `.claude/skills/check-recipe-card/SKILL.md` — audit workflow
- `.claude/skills/check-recipe-card/references/audit-dimensions.md` —
  scoreable rubric, one entry per dimension
- `.claude/skills/check-recipe-card/references/repair-playbook.md` —
  finding → diagnosis → fix recipe per dimension
- `.claude/skills/check-recipe-card/scripts/audit_recipe_card.py` —
  Tier-1 deterministic audit script
- `.plans/2026-04-29-recipe-card-skill-pair.plan.md` — this file

### Modify

- `RESOLVER.md` — add a note that new recipe-card filing goes through
  `/build:build-recipe-card`; the audit goes through
  `/build:check-recipe-card`. Filing table is unchanged (still routes by
  meal-type folder).
- `AGENTS.md` — register the pair in the *Working Agreements* section
  with one bullet pointing at the two slash commands.

### Delete

None.

## Tasks

Tasks are sequential. Each task ends with a single git commit on the
`feat/recipe-card-skill-pair` branch. Task 0 sets up the branch.

### Task 0 — Branch and prep <!-- sha:00be7dc -->

**Status:** completed.

- Create branch `feat/recipe-card-skill-pair` from `main`.
- Confirm `.claude/skills/` is writable (create the parent if absent;
  do not create the per-skill subdirs yet — those are written by Task 1
  via the meta-skill, then moved into place in Task 2).
- Verify: `git branch --show-current` returns `feat/recipe-card-skill-pair`;
  `test -d .claude` succeeds.
- Commit: `chore: branch for recipe-card skill pair`

### Task 1 — Invoke `/build:build-skill-pair recipe-card` <!-- no-commit: rolls into Task 2 -->

**Status:** completed. Five artifacts written to `plugins/build/...`; commit folded into Task 2 per plan.

Dogfood the toolkit's primitive-pair builder to produce the five
artifacts. The skill writes to its hardcoded `plugins/build/...`
locations inside the cwd; that's expected and gets fixed in Task 2.

- Invoke `/build:build-skill-pair recipe-card`.
- Provide intake answers verbatim (these are bound by the design doc,
  not negotiable at execution time):
  - **Definition:** "A recipe-card is a single markdown document —
    kebab-case filename, located in a meal-type folder per
    `RESOLVER.md` — that records an existing recipe from a cited
    source. It carries the vault's standard YAML frontmatter and a body
    with `## Ingredients` (bullets) → `---` → `## Preparation`
    (numbered steps), faithfully transcribed with no invented
    ingredients."
  - **Scope boundary:** "Not a meal plan, menu, or shopping list. Not
    a how-to guide unconnected to a specific dish. Not the `_index.md`
    Dataview page or `RESOLVER.md` routing doc. Not an image attachment
    under `attachments/`."
  - **Best-practice material:** the in-repo files `AGENTS.md`,
    `RESOLVER.md`, `_index.md`, `scripts/transform_recipes.py`, plus a
    sample of 8–10 existing recipe-cards spanning all meal-type
    folders, plus Claude's named knowledge of recipe-writing best
    practices (mise-en-place ordering, imperative-voice steps, unit
    consistency).
  - **Routing-doc placement:** *skip* — `primitive-routing.md` belongs
    to the toolkit, not this vault. If the meta-skill insists on
    writing a routing-doc edit, accept the diff in scratch space; it
    will be discarded in Task 2.
- At the meta-skill's Review Gate, approve.
- Five artifacts (plus possibly a routing-doc edit) will be written to:
  - `plugins/build/_shared/references/recipe-card-best-practices.md`
  - `plugins/build/skills/build-recipe-card/SKILL.md`
  - `plugins/build/skills/check-recipe-card/SKILL.md`
  - `plugins/build/skills/check-recipe-card/references/audit-dimensions.md`
  - `plugins/build/skills/check-recipe-card/references/repair-playbook.md`
- Verify: `find plugins/build -type f -name '*.md'` lists exactly the
  five files above (plus optionally `primitive-routing.md`).
- **Do not commit yet** — Task 2 relocates these files; the transient
  `plugins/` tree should never appear in version control.

### Task 2 — Relocate to project-scoped paths and patch references

**In-flight amendment:** `.claude/` was broadly gitignored
(`.claude/`). Amended `.gitignore` to mirror the `.obsidian/` pattern
(`.claude/*` + `!.claude/skills/`) so project-scoped skills land in
version control while `.claude/settings.local.json` stays local.

- Create destination skeleton:
  - `.claude/skills/_shared/`
  - `.claude/skills/build-recipe-card/`
  - `.claude/skills/check-recipe-card/references/`
  - `.claude/skills/check-recipe-card/scripts/`
- Move files (use plain `mv`, not `git mv` — files are not yet tracked):
  - `plugins/build/_shared/references/recipe-card-best-practices.md`
    → `.claude/skills/_shared/recipe-card-best-practices.md`
  - `plugins/build/skills/build-recipe-card/SKILL.md`
    → `.claude/skills/build-recipe-card/SKILL.md`
  - `plugins/build/skills/check-recipe-card/SKILL.md`
    → `.claude/skills/check-recipe-card/SKILL.md`
  - `plugins/build/skills/check-recipe-card/references/audit-dimensions.md`
    → `.claude/skills/check-recipe-card/references/audit-dimensions.md`
  - `plugins/build/skills/check-recipe-card/references/repair-playbook.md`
    → `.claude/skills/check-recipe-card/references/repair-playbook.md`
- Patch internal cross-references in the moved files. The meta-skill
  emits paths assuming the toolkit layout; rewrite them to project-
  scoped equivalents:
  - In both `SKILL.md` files, replace any
    `plugins/build/_shared/references/recipe-card-best-practices.md`
    references with `../_shared/recipe-card-best-practices.md`
    (relative path from the skill dir).
  - In `check-recipe-card/SKILL.md`, replace any
    `plugins/build/skills/check-recipe-card/references/...`
    references with `references/...`.
  - In `audit-dimensions.md` and `repair-playbook.md`, replace any
    references to the principles doc at
    `plugins/build/_shared/references/recipe-card-best-practices.md`
    with `../../_shared/recipe-card-best-practices.md`.
  - Sweep with `grep -rn 'plugins/build' .claude/skills/` — must be
    empty after the patch.
- Discard any `primitive-routing.md` edit the meta-skill made (toolkit
  artifact, not relevant here):
  `rm -rf plugins/`
- Verify:
  - `find .claude/skills -name SKILL.md | wc -l` returns `2`.
  - `find .claude/skills/check-recipe-card/references -name '*.md'
    | wc -l` returns `2`.
  - `test -f .claude/skills/_shared/recipe-card-best-practices.md`
    succeeds.
  - `grep -rn 'plugins/build' .claude/skills/` returns nothing.
  - `test ! -d plugins` succeeds.
- Commit: `feat: scaffold recipe-card skill pair via build-skill-pair
  and relocate to .claude/skills/`

### Task 3 — Tier-1 Python audit script

- Write
  `.claude/skills/check-recipe-card/scripts/audit_recipe_card.py`.
- CLI: `audit_recipe_card.py [--folder <path> | <file>...]`, emits JSON
  findings to stdout, exits 0 on clean / 1 on any finding / 2 on
  invocation error.
- Implements every Tier-1 check from audit-dimensions.md: frontmatter
  shape, kebab-case filename, folder/meal-type match, body structure
  presence, description-not-placeholder, description-not-first-
  ingredient.
- Use only stdlib (`pathlib`, `re`, `json`, `argparse`, `sys`). No
  PyYAML — frontmatter parsing reuses the regex pattern from
  `scripts/transform_recipes.py`.
- Make executable: `chmod +x`.
- Verify (smoke test):
  - `python3 .claude/skills/check-recipe-card/scripts/audit_recipe_card.py
    --folder dinner` exits non-zero (broken descriptions are present).
  - `python3 .claude/skills/check-recipe-card/scripts/audit_recipe_card.py
    --help` prints usage.
- Commit: `feat: add Tier-1 audit script for recipe-cards`

### Task 4 — Wire RESOLVER.md and AGENTS.md

- In `RESOLVER.md`, append a note under the *Notes* section pointing
  out that new recipe filing goes through `/build:build-recipe-card`
  and audit goes through `/build:check-recipe-card`. Do not modify the
  filing or context tables — folders are unchanged.
- In `AGENTS.md`, add one bullet under *Working Agreements* registering
  the pair (one line each for build and check, with one-sentence
  description).
- Verify: `git diff RESOLVER.md AGENTS.md` shows additive changes only;
  no existing lines removed.
- Commit: `docs: register recipe-card skill pair in RESOLVER and AGENTS`

### Task 5 — End-to-end validation: build half

- Pick one well-cited URL not yet in the vault (the user provides it
  during execution; if not provided, skip and note as deferred).
- Manually run the build-recipe-card workflow against it. The skill
  workflow is read-and-followed by the executor; this is the dogfood
  pass.
- Confirm the resulting file lands in the correct meal-type folder,
  has valid frontmatter, and runs clean through the Tier-1 script.
- Verify:
  - `python3 .claude/skills/check-recipe-card/scripts/audit_recipe_card.py
    <new-file>` exits 0.
  - The file's `description:` field is a real one-sentence summary.
- Commit: `test: validate build-recipe-card end-to-end with <recipe-name>`
  (skip commit if validation source not provided; document the skip
  in the plan's Validation section).

### Task 6 — End-to-end validation: check half on the vault

- Run the Tier-1 script across every recipe folder:
  `for d in dinner breakfast lunch sides desserts appetizers basics; do
   python3 .claude/skills/check-recipe-card/scripts/audit_recipe_card.py
   --folder "$d"; done`
- Capture the count of `description-not-placeholder` and
  `description-not-first-ingredient` findings to confirm the pair
  catches the existing-bug at the expected scale (≥ 100 of the 171
  files).
- Capture the JSON output to `/tmp/recipe-card-audit.json` (gitignored,
  not committed) for the follow-on repair plan to consume.
- Verify: total finding count ≥ 100 across the vault; report broken
  out by dimension printed to stdout.
- Commit: `test: validate check-recipe-card across vault (baseline
  finding counts)` — commits a short markdown summary at
  `.plans/2026-04-29-recipe-card-skill-pair.notes.md` (not the raw
  audit JSON).

## Validation

Run after Task 6 completes. All criteria must pass before the plan is
marked complete.

1. **Pair structure complete.**
   - `find .claude/skills -name SKILL.md | wc -l` returns `2`.
   - `find .claude/skills/check-recipe-card/references -name '*.md'
     | wc -l` returns `2`.
   - `test -f .claude/skills/_shared/recipe-card-best-practices.md`
     succeeds.
   - `test -x
     .claude/skills/check-recipe-card/scripts/audit_recipe_card.py`
     succeeds.

2. **Tier-1 script is self-consistent.**
   - `python3
     .claude/skills/check-recipe-card/scripts/audit_recipe_card.py
     --help` prints usage and exits 0.
   - Running the script against a known-good fixture (a hand-crafted
     synthetic recipe-card kept under `/tmp/` for the test) exits 0.
   - Running it against a known-bad fixture exits 1 with the expected
     dimension in the JSON output.

3. **Cross-artifact consistency.**
   - Every dimension named in `audit-dimensions.md` has a matching
     entry in `repair-playbook.md`. Verify with:
     `diff <(grep '^### ' audit-dimensions.md | sort)
     <(grep '^### ' repair-playbook.md | sort)`
     → exits 0 (no diff).
   - Both `SKILL.md` files reference the principles doc at the same
     path. Verify with:
     `grep -l 'recipe-card-best-practices.md'
     .claude/skills/build-recipe-card/SKILL.md
     .claude/skills/check-recipe-card/SKILL.md`
     → returns both paths.

4. **Existing-bug catch confirmed.**
   - Tier-1 sweep across the seven recipe folders reports
     ≥ 100 findings tagged `description-not-placeholder` or
     `description-not-first-ingredient`.

5. **Build half end-to-end (if validation source provided).**
   - One new recipe-card created via the build workflow audits clean
     under Tier-1.
   - The new file's `description:` is genuinely descriptive (manual
     read-back).

6. **Docs registered.**
   - `grep -c '/build:build-recipe-card' RESOLVER.md AGENTS.md` returns
     ≥ 2 across the two files.

7. **Branch is clean.**
   - `git status` reports a clean working tree.
   - `git log feat/recipe-card-skill-pair --oneline` shows one commit
     per completed task in order.

## Open implementation questions (resolve during execution)

- **Validation source for Task 5.** Which URL should be used for the
  build half end-to-end test? If not provided at execution time, the
  task is skipped and noted in the validation report.
- **Credibility classifier encoding.** Static domain allowlist plus
  judgment fallback, or judgment-only? Default for v1 is judgment-only
  (the dialogue assesses each source); allowlist is a follow-on.
- **Tier-2 / Tier-3 sweep performance.** The Python script handles
  Tier-1 fast. Tier-2 (LLM judgment) and Tier-3 (cross-vault) run
  inline in the check workflow with explicit user opt-in to keep
  costs bounded. No batched-LLM mode in v1.
