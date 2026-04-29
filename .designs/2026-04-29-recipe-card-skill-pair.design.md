---
name: Recipe-card skill pair (build-recipe-card / check-recipe-card)
description: A primitive-pair for recording and auditing recipe-card files in this vault — build-recipe-card extracts faithful records from URLs/images/PDFs/text, check-recipe-card audits single files or the whole vault across deterministic, judgment, and cross-vault tiers. The "card" framing reinforces that we transcribe existing recipes, not invent new ones.
type: design
status: draft
related:
  - ../AGENTS.md
  - ../RESOLVER.md
  - ../scripts/transform_recipes.py
---

# Recipe-card skill pair (build-recipe-card / check-recipe-card)

## Purpose

Codify the recipe-card authoring and auditing workflow that has, until
now, been ad-hoc. The vault holds 171 recipe-card files with a consistent
shape but known drift (broken `description:` field on most files,
possibly mis-filed or low-credibility sources). The pair lets new
recipe-cards land clean from a source (URL/image/PDF/text) *and* lets the
existing 171 be swept and repaired against the same rubric.

## Primitive definition

**A recipe-card** is a single markdown document — kebab-case filename,
located in a meal-type folder per `RESOLVER.md` — that *records* an
existing recipe from a cited source. It carries YAML frontmatter
(`description`, `aliases`, `tags`, `meal-type`, `difficulty`, `cuisine`,
`dietary`, `cooking-time`, `cooking-time-minutes`, `servings`, `url`,
`rating`, `last-cooked`) and a body with `## Ingredients` (bullet list) →
`---` → `## Preparation` (numbered steps), faithfully transcribed with no
invented ingredients. The "card" naming is deliberate: a card is a record
of an existing recipe, not a new creation.

### Scope boundary — what a recipe-card is *not*

- Not a meal plan, menu, or shopping list
- Not a how-to guide unconnected to a specific dish (knife skills, kitchen
  setup)
- Not the `_index.md` Dataview query page or `RESOLVER.md` routing doc
- Not an image attachment under `attachments/`

## `build-recipe-card` behavior

### Accepted source types

- URL (via WebFetch)
- Pasted text or markdown
- Single or multi-image (vision-extracted; multi-page cookbook spreads are
  the caller's responsibility to collate)
- PDF

Video/audio transcripts are explicitly out of scope.

### Workflow

1. **Intake source.** Caller provides one of the accepted source types.
2. **Credibility assessment.** Classify as:
   - `well-cited` — NYT Cooking, Serious Eats, ATK, Bon Appétit, named
     cookbook author, established food publication
   - `acceptable` — named author with a track record, niche but credible
     publication
   - `low-credibility` — uncredited blog, AI-generated, SEO content,
     unverifiable

   Emit assessment in dialogue. If `low-credibility`, prompt the user to
   confirm before proceeding and tag the resulting file with
   `low-credibility` in `tags:`.
3. **Faithful extraction.** Pull ingredients and preparation verbatim.
   Never substitute, omit, or fill from model knowledge.
4. **Ambiguity handling.** For any gap (cropped image, "salt to taste"
   without quantity, cross-references to other posts), insert a
   `TODO: <what's missing>` marker inline at the gap *and* add
   `needs-review` to `tags:`. Do not invent.
5. **Frontmatter generation.** Derive every field from source.
   `meal-type` determines target folder. `description` is a real
   one-sentence summary (not the placeholder `"> Description"` and not a
   verbatim copy of the first ingredient line — the existing bug).
   `dietary` is `[]` unless the source explicitly identifies the recipe
   as vegetarian/vegan/etc.
6. **Filing.** Write to `<folder>/<kebab-case-stem>.md` per
   `RESOLVER.md`. If `meal-type` is genuinely ambiguous from source,
   file under `basics/` with `needs-review` (matches existing triage).
7. **Handoff.** Offer `/check-recipe-card <new-file>` to audit the
   just-written recipe-card.

## `check-recipe-card` behavior

### Scope

Single file *or* whole-vault sweep (any folder under `RESOLVER.md`'s
recipe folders: `dinner/`, `breakfast/`, `lunch/`, `sides/`, `desserts/`,
`appetizers/`, `basics/`).

### Tier 1 — deterministic (Python script under `scripts/`)

- Frontmatter shape: required fields present, types correct (lists are
  lists, ints are ints), enum-ish fields valid (`difficulty` ∈ {easy,
  medium, hard, project}, etc.)
- Filename is kebab-case, no curly apostrophes
- File is in folder matching `meal-type` per `RESOLVER.md`
- Body structure: `## Ingredients` present with bullet list,
  `## Preparation` present with numbered list, `---` separator between
- `description:` is not `"> Description"` and is not a verbatim copy of
  the first ingredient line (the existing 171-file bug)

### Tier 2 — judgment (LLM-evaluated, scored against `audit-dimensions.md`)

- Description is genuinely descriptive of the dish (not generic, not
  off-topic)
- `url:` points to a credible domain — same `well-cited` / `acceptable` /
  `low-credibility` classifier as build
- Ingredient/preparation coherence: every ingredient referenced in steps
  appears in the ingredient list, and vice versa (heuristic, not strict
  exact-match)
- `dietary:` claims are consistent with ingredient list (a `vegan`-tagged
  recipe should not list butter or eggs)
- Tag hygiene: `meal-type` mirrored in `tags:`, no contradictions across
  fields

### Tier 3 — cross-vault

- Duplicate-card detection (same dish recorded under different filenames,
  alias collisions)
- Alias-index consistency for `[[wikilinks]]` — every wikilink target
  resolves to a real file
- Dietary-tag consistency across vault (same recipe-class isn't tagged
  vegan in one file and not in another)

### Repair loop (opt-in, hybrid)

- **Auto-fix** deterministic findings with one right answer: kebab-case
  rename (via `git mv` to preserve history), frontmatter type coercion,
  `meal-type`/folder mismatch (move file with `git mv`).
- **Propose diff** for judgment findings: regenerated description from
  `url:`, credibility tag, dietary corrections. User approves per-file or
  per-batch.
- The repair playbook (`repair-playbook.md`) provides the recipe for
  each finding type.

## Distillation inputs (for the principles doc)

- This repo's own conventions: `RESOLVER.md` (filing rules), `_index.md`
  (Dataview field expectations), `scripts/transform_recipes.py` (encodes
  filing/folder rules and the alias-index pattern)
- `AGENTS.md` rules: no invented ingredients, well-cited sources,
  named-author preference
- The existing 171 recipe-cards as the canonical "anatomy" example
- Claude's named knowledge of recipe-writing best practices (mise-en-place
  ingredient ordering, imperative-voice steps, unit consistency)

No external URLs needed — the repo itself is the strongest source.

## Routing-doc placement

**New top-level primitive class.** Recipe-cards are not scripts, hooks,
or config primitives — they are content artifacts that record an
existing recipe (the dish-instructions from a cited source) into the
vault's structured frontmatter format. Update `primitive-routing.md`:

- Add a paragraph under *What Each Primitive Was Designed For* describing
  recipe-cards as content artifacts that record (not invent) recipes,
  with structured frontmatter and cited provenance.
- Extend the *Routing Test* with a branch for "user pasted a
  URL/image/PDF of a recipe" → `/build-recipe-card`.
- Add route lines: `/build-recipe-card` and `/check-recipe-card`.

## Acceptance criteria

A reasonable user with this pair installed can:

1. Paste an NYT Cooking URL and get a clean, well-filed recipe-card in
   under 30 seconds.
2. Paste a low-credibility blog URL and be warned, with the resulting
   recipe-card tagged `low-credibility`.
3. Paste a cookbook page photo missing a quantity and get a recipe-card
   with `TODO:` markers plus `needs-review` tag.
4. Run `/check-recipe-card` over the whole vault and get a categorized
   report of findings (broken descriptions, mis-filed files,
   low-credibility sources, duplicates).
5. Run the repair loop and have kebab-case renames plus folder moves
   applied automatically, while approving description regenerations one
   by one.

## Non-goals

- Video or audio transcription of cooking videos
- Nutrition calculation, scaling, or unit conversion
- Photo generation for recipes
- Modifying `_index.md` Dataview queries (stable infrastructure)
- Touching `attachments/` (image storage)
- Replacing `scripts/transform_recipes.py` (one-shot import script;
  audit borrows its alias-index logic but does not absorb it)

## Open implementation questions (for plan-work)

- Where does the Tier-1 Python script live: inside the
  `check-recipe-card/scripts/` directory of the skill, or in this repo's
  `scripts/` folder so it can be invoked outside the skill harness?
  (Skill-pair builder default: inside the skill.)
- Credibility classifier — encoded as a static domain allowlist plus
  judgment fallback, or judgment-only? The allowlist is faster and more
  consistent but goes stale.
- Whole-vault sweep performance — 171 files is small now, but Tier-2
  judgment checks per file get expensive. Consider a fast pre-filter
  (Tier-1 only) and explicit opt-in for Tier-2 vault sweeps.
